# 4. Staging runbook: install the SI chat feature on the three staging VMs

**Track:** Software (building, moving, and installing the SI service). Security decisions are in the [Cyber Security package](../cyber/README.md).

**Who this is for:** the person logged in to the three staging VMs. Follow the steps in order and copy the
commands as written. You do not need to know Kubernetes. When something fails, stop, write down the step, the
command, and the last 20 lines it printed, and send that back (section 9). Do not fix things by hand unless a
step tells you to.

**What you are doing:** building the release bundle the lab will get, cutting the VMs off from the internet,
and installing the bundle exactly as the lab will, then checking that it works. This is the chat feature only
(phase 1), the software on the list sent to the ISSM. The VMs have no GPU, so a small stand-in model answers
instead of gpt-oss-120b. Its add-on is kept separate and never goes to the lab.

**What we assume, so we get as far as possible:** the lab has **no package mirror**, so the bundle carries
its own OS packages. The **USA-only model rule covers the whole lineage** of the models we deliver.

**Time:** the pull takes several hours (about 200 GB of downloads). The install and checks take about half a
day.

**Done means:** `smoke-test.sh` prints `ALL PASSED`, the chat page answers in a browser, the egress log on all
three VMs is empty, and the results in section 9 are sent back.

---

## 0. Before you start

Pick which VM is which. **VM1** builds the bundle, runs the first Kubernetes server, and holds the models.
**VM2** and **VM3** join it. Run this on each VM and fill in the table:

```bash
hostname; ip -4 -br addr; cat /etc/redhat-release; uname -r
getenforce; fips-mode-setup --check; nproc; free -g; df -h / /srv /var/lib /opt 2>/dev/null
systemctl is-active firewalld NetworkManager; command -v podman git
```

| | VM1 | VM2 | VM3 |
|---|---|---|---|
| Host name (`hostname`) | | | |
| IP address | | | |
| RHEL version, kernel | | | |
| SELinux (`getenforce`), FIPS | | | |
| CPUs, RAM, free disk | | | |
| firewalld active? | | | |

**Staging network** (the range that holds all three IPs, for example `10.20.30.0/24`): ______________

**Size.** We don't know the VMs' exact sizes yet, so start with what they have. Our estimate of what is
needed: VM1 about 16 CPUs, 64 GB RAM, 700 GB free under `/srv` and `/var/lib` (bundle, build scratch, a copy
of the models, Kubernetes); VM2 and VM3 about 8 CPUs, 32 GB RAM, 200 GB free under `/var/lib` and `/opt`.
If a step fails for lack of disk or memory (`No space left on device`, a pod `OOMKilled` or `Pending`), stop,
write down which VM and how much it has, and send it back: the program will ask for more.

**You need:** root on all three VMs (`sudo -i`), SSH from VM1 to VM2 and VM3, a Hugging Face token (optional,
faster downloads), and a workstation with a browser that can reach VM1 (section 7).

Run every command below as root (`sudo -i`).

## 1. Get the repository and podman (VM1, internet on)

The program tells you which commit to use. Write it down: ______________

```bash
dnf -y install podman git          # if this fails, VM1 has no RHEL repositories: stop and report
mkdir -p /srv/si && cd /srv/si
git clone <repository URL> repo && cd repo && git checkout <commit>
```

podman is the only build tool on VM1. Everything else runs inside a container, so VM1 stays a clean node.
VM2 and VM3 get nothing from the internet at all.

## 2. Make a test signing key (VM1)

The lab refuses unsigned bundles. Staging uses a throw-away key, never used for the lab.

```bash
export GNUPGHOME=/srv/si/gnupg-sign; install -d -m 700 "${GNUPGHOME}"
gpg --batch --passphrase '' --quick-gen-key "SI staging test key (not for the lab)" rsa3072 sign 1y
export GPG_KEY=$(gpg --list-keys --with-colons | awk -F: '/^fpr/{print $10; exit}')
gpg --armor --export "${GPG_KEY}" > /srv/si/staging-signing-key.pub.asc
echo "${GPG_KEY}"
```

## 3. Build the bundle and the stand-in add-on (VM1, internet on)

Use `tmux` (or `screen`) so a dropped SSH session does not stop it.

```bash
cd /srv/si/repo/delivery
SI_ROOT=/srv/si HF_TOKEN=<token or leave out> ./build-in-container.sh
```

It builds the container, then runs every pull step: RKE2, Zarf, the Zarf package (charts and images),
the models (including the Whisper conversion), the OS packages, Trivy and its database, the image scan, the
NVIDIA driver installer, and the seal. Progress goes to `/srv/si/bundle.pull.log`. It ends with
`done. Next: move ...`. If it stops with `ERROR`, report the last 20 lines of the log.

Then build the add-on (stand-in model and CPU Whisper):

```bash
SI_ROOT=/srv/si ./build-in-container.sh staging/build-addon.sh
```

Check: `ls /srv/si/bundle` shows `SHA256SUMS.asc`, and `/srv/si/staging-addon/package/` holds one
`.tar.zst` file. Keep `/srv/si/bundle/scanner/reports/SUMMARY.txt` for section 9.

## 4. Copy what VM2 and VM3 need (VM1)

VM2 and VM3 need only the RKE2 files, the OS packages, and the install scripts. Replace `vm2` and `vm3` with
their host names or IPs:

```bash
for h in vm2 vm3; do
  ssh root@$h mkdir -p /srv/si/bundle
  scp -rp /srv/si/bundle/{rke2,os-packages,intake,SHA256SUMS,SHA256SUMS.asc,VERSIONS.env,MODELS.txt} root@$h:/srv/si/bundle/
  scp /srv/si/staging-signing-key.pub.asc /srv/si/repo/delivery/staging/egress-block.sh root@$h:/srv/si/
done
```

## 5. Cut off the internet (all three VMs)

From here on, nothing may reach the internet. The VMs keep their route (Kubernetes needs one), but every new
outbound connection outside the staging network is blocked and logged. Your SSH session is not affected.

On VM1: `cd /srv/si/repo/delivery/staging`. On VM2 and VM3: `cd /srv/si`. Then on each:

```bash
./egress-block.sh on <staging network>       # for example: ./egress-block.sh on 10.20.30.0/24
curl -m 5 -sS https://github.com -o /dev/null && echo "NOT BLOCKED: stop and report" || echo "blocked: OK"
```

Then add the chat page name on all three VMs (VM1's IP):

```bash
echo "<VM1 IP> chat.staging.lab" >> /etc/hosts
```

## 6. Verify and install

### 6a. Check the bundle (VM1, then VM2 and VM3)

This rehearses the lab's intake: the public key arrives separately, and the bundle is checked against it.

VM1 (full bundle):

```bash
export GNUPGHOME=/srv/si/gnupg-verify; install -d -m 700 "${GNUPGHOME}"
gpg --import /srv/si/staging-signing-key.pub.asc
/srv/si/bundle/intake/verify.sh /srv/si/bundle          # must end with PASS
```

VM2 and VM3 (only the parts copied in section 4):

```bash
export GNUPGHOME=/srv/si/gnupg-verify; install -d -m 700 "${GNUPGHOME}"
gpg --import /srv/si/staging-signing-key.pub.asc
cd /srv/si/bundle && gpg --verify SHA256SUMS.asc SHA256SUMS && sha256sum --quiet -c --ignore-missing SHA256SUMS && echo PASS
```

### 6b. OS packages (all three VMs)

If firewalld is active, Kubernetes networking will not work. For staging, turn it off and note it in
section 9 (it is a question for Cyber, S27):

```bash
systemctl disable --now firewalld 2>/dev/null; true
/srv/si/bundle/intake/deploy.sh os-packages
```

It installs from the bundle only, with every other repository off. If `dnf` reports a conflict or a missing
package, that is exactly what we need to know: report it in full.

### 6c. Kubernetes (VM1 first, then VM2 and VM3)

VM1:

```bash
cd /srv/si/bundle/intake
./deploy.sh server-init                     # prints the join token at the end
install -m 600 /var/lib/rancher/rke2/server/node-token /root/join-token
for h in vm2 vm3; do scp /root/join-token root@$h:/root/join-token; done
```

VM2, then VM3 (wait until the first one shows `joined`):

```bash
RKE2_TOKEN_FILE=/root/join-token /srv/si/bundle/intake/deploy.sh server-join <VM1 IP>
```

Back on VM1, wait until all three show `Ready` (a few minutes):

```bash
export PATH=/var/lib/rancher/rke2/bin:$PATH KUBECONFIG=/etc/rancher/rke2/rke2.yaml
kubectl get nodes -w
```

### 6d. Models, platform, and apps (VM1)

Make the stand-in certificate first. It rehearses the lab CA steps on the browser side.

```bash
cd /srv/si && openssl req -x509 -newkey rsa:3072 -nodes -days 90 -keyout ca.key -out ca.crt -subj "/CN=SI Staging CA"
openssl req -newkey rsa:3072 -nodes -keyout si.key -out si.csr -subj "/CN=chat.staging.lab"
openssl x509 -req -in si.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 90 -out si.crt \
  -extfile <(printf 'subjectAltName=DNS:chat.staging.lab')
```

Then, using the three host names from `kubectl get nodes`:

```bash
cd /srv/si/bundle/intake
./deploy.sh models
SERVICE_NODES="<vm1> <vm2> <vm3>" MODEL_NODES="<vm1>" ./deploy.sh platform
./deploy.sh apps --chat-host chat.staging.lab --tls-cert /srv/si/si.crt --tls-key /srv/si/si.key --staging
./deploy.sh gateway-key
/srv/si/repo/delivery/staging/deploy-addon.sh /srv/si/staging-addon /srv/si/bundle
```

`apps` takes a while (the database starts first). Wait until `./deploy.sh status` says `all pods running`.
The stand-in model can take five minutes to load.

## 7. Check that it works

### 7a. Automatic checks (VM1)

```bash
/srv/si/repo/validate/smoke-test.sh /srv/si/bundle | tee /srv/si/smoke-1.txt
```

Each line is `PASS` or `FAIL` with a check ID. Answers from the stand-in model are slow (up to a minute) and
simple; that is expected.

### 7b. In a browser (your workstation)

1. Add `<VM1 IP> chat.staging.lab` to the workstation's hosts file.
2. Import `/srv/si/ca.crt` into the workstation's trusted certificates (copy it off VM1 first).
3. Open `https://chat.staging.lab`. There must be **no certificate warning**.
4. Create the first account. **The first account becomes the admin.** Then ask: "Name the three primary
   colors." The answer streams in. (C11)
5. Admin Panel, Settings, Documents: engine `openai`, model `doc-embed`, and a key that is not empty. (C11b)
6. Upload a text PDF of 50 to 100 pages. Write down how long indexing takes. Ask about a fact that is on one
   page only. Then upload a scanned (image-only) PDF of about 20 pages and write down how long it takes. (C11b)
7. Record a few seconds of speech with the microphone button, if the browser allows it. (C10, by hand)

## 8. Resilience (VM1 unless stated)

| # | What to do | Pass if |
|---|---|---|
| C16 | On **each** VM: `egress-block.sh status` (VM1: in `/srv/si/repo/delivery/staging`; VM2, VM3: in `/srv/si`). Save the output. | No `SI-EGRESS` lines. Every line that appears is a finding: copy it into section 9. |
| C17 | Reboot all three VMs (`reboot`). When they are back, run `deploy.sh status`, then the smoke test again into `smoke-2.txt`. | Same result as before, with no manual steps |
| C18 | Run the `./deploy.sh apps ... --staging` line from 6d twice more, then the smoke test into `smoke-3.txt` | Nothing breaks |
| C19 | Rollback. Needs a previous bundle, so skip it on the first run and write "skipped". | |

## 9. Send back

| Item | Where it is |
|---|---|
| The table from section 0 and the commit from section 1 | |
| Pull log | `/srv/si/bundle.pull.log` |
| Scan summary | `/srv/si/bundle/scanner/reports/SUMMARY.txt` |
| What went into the bundle | `/srv/si/bundle/MANIFEST.txt` |
| Smoke test results | `/srv/si/smoke-1.txt`, `smoke-2.txt`, `smoke-3.txt` |
| Egress log from each VM (C16) | output of `egress-block.sh status` on each |
| Browser checks (7b) | pass or fail per step, indexing and OCR times |
| Changes you had to make | for example: firewalld turned off, anything else |
| Every failure | step, command, and the last 20 lines it printed |

## If you need to start over

On each VM: `/usr/local/bin/rke2-uninstall.sh`, then `rm -rf /var/lib/models`. Go back to section 6c. To
pull a new bundle, first turn the block off on VM1 (`egress-block.sh off`), then go back to section 3.

## How staging differs from the lab

Staging runs the lab's install steps, but these things are different on purpose. Each is a staging-only
choice, not a change to the lab plan. If a result depends on one of them, say so when you send it back.
Every artifact the scripts fetch, and which of them never leave staging: [Staging artifact list](5-staging-artifacts.md).

| | Staging (these VMs) | Lab (production) |
|---|---|---|
| Hardware | Three VMs, no GPU, sizes not yet known | svc01 to svc03 and gpu01 (four RTX PRO 6000) |
| OS | RHEL 9, whatever the VMs were built with | Rocky 9 or RHEL 9 with the lab's hardening (L1, open) |
| OS packages | From the bundle (Rocky 9.9 builds) installed on RHEL | From the bundle, unless the lab has a mirror (S11) |
| Build | VM1 builds the bundle in a container, then is also a cluster node | A separate build workstation; only the bundle crosses |
| Internet cut-off | `egress-block.sh` on each VM: blocks and logs outbound traffic | No internet at all |
| Signing key | A throw-away test key made in section 2 | The real signing key (S10) |
| Install steps | No `driver`, no `os-packages --gpu`; `apps --staging` (0 gpt-oss copies, no GPU Whisper) | Every step, including the driver; `apps` with 3 gpt-oss copies and Whisper on GPU |
| Chat model | A small IBM model on CPU (granite-3.3-2b-instruct), answering under the name `gpt-oss-120b` | gpt-oss-120b on GPU |
| Whisper | The same converted model, on CPU (int8), from the add-on | On GPU, from the bundle |
| Staging add-on | `si-staging-addon` (CPU vLLM image, CPU speaches image, the stand-in model). Never sealed into the bundle and never sent to the lab | Not present |
| Models node | VM1 holds the models | gpu01 |
| Host name and certificate | `chat.staging.lab` in hosts files; a CA made on VM1 | The lab's DNS name and certificate from the lab's CA |

## What staging does not prove

- **The GPU path:** the driver build, the GPU Operator, gpt-oss-120b on the RTX PRO 6000, and real speed.
  See the [Sandbox bring-up plan](3-sandbox-bringup-plan.md), W1.
- **The lab's OS:** the bundle's OS packages come from Rocky Linux 9.9. Installing them on RHEL shows the
  "no mirror" path works, but if the lab runs RHEL with a different minor version or kernel, the driver
  build tools must be pulled for that kernel (`OS_KERNEL`, in [Software delivery](2-software-delivery.md)).
- **The lab's hardening:** unless these VMs have the lab's STIG settings, SELinux and fapolicyd failures can
  still appear in the lab (W4).
