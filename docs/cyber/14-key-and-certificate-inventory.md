# 14. Key and certificate inventory (initial, for Cyber Security)

**Track:** Cyber Security ([package index and decision register](README.md)).
**Status:** Draft, 2026-11-14. Phase 1 (SI through the chat page only; analysts get no API keys). Taken from the delivery and install scripts as they are
today; "to confirm" marks what only the sandbox can prove.

## What this is

A **key** is a secret that proves who you are or unlocks something. A **certificate** is a public key with a
signed label saying who it belongs to. This list says, for every key, password, token, and certificate in phase 1:
what it protects, who creates it, where it lives, who can get to it, when it expires, how it is changed, and what
to do if it leaks.

The software BOM ([12](12-software-bom.md)) says what code comes in. The model BOM ([13](13-model-bom.md)) says
what weights come in. This list covers the secrets that decide **who can change that code, reach those models,
and read the data**.

**Damage if leaked** uses three levels:
- **Critical:** lets someone put their own software into the lab, or take over the whole system.
- **High:** lets someone read other people's data, act as another user, or turn off the records.
- **Moderate:** lets someone use the service without being identified, or interrupts it.

## Summary

| ID | What | Damage if leaked | Created by | Lives in | Expires |
|---|---|---|---|---|---|
| KC1 | Bundle signing private key | **Critical** | Us (release owner) | Build workstation | We set it (proposed 2 years) |
| KC2 | Bundle signing public key | **Critical** if swapped | Us; imported by the lab admin | Lab admin host | With KC1 |
| KC3 | Lab CA (certificate authority) | **Critical** | Lab PKI team | Lab PKI | Lab policy |
| KC4 | TLS certificate and private key for the chat page | High | Us (key and request); lab CA signs | Kubernetes secret `si-tls` | Lab CA policy (often 1 year) |
| KC5 | Gateway master key | **Critical** | `deploy.sh apps` (random) | Kubernetes secret `litellm-masterkey` | Never (today) |
| KC6 | Chat page's gateway key | Moderate | `deploy.sh gateway-key` | Kubernetes secret `open-webui-gateway-key` | Never (today) |
| KC7 | User API keys, one per analyst (later phase only; none in phase 1) | Moderate to High | `deploy.sh user-key <name>` | Analyst machines; gateway database (hashed) | Never (today) |
| KC8 | Cluster admin credentials | **Critical** | RKE2, at install | `/etc/rancher/rke2/rke2.yaml` on svc01-03 | 1 year (RKE2 client certificate) |
| KC9 | RKE2 join token | **Critical** | RKE2, at `server-init` | svc01; copied to each joining node | Never, until rotated |
| KC10 | Kubernetes internal certificates and the secrets encryption key | **Critical** | RKE2, at install | `/var/lib/rancher/rke2/server/` on svc01-03 | Certificates 1 year, renewed by RKE2; key never |
| KC11 | Zarf registry and agent credentials | **Critical** | `zarf init` (random) | Kubernetes secret `zarf-state` | Never |
| KC12 | Gateway database password | High | CloudNativePG operator (random) | Kubernetes secret `si-postgres-app` | Never |
| KC13 | Chat page session-signing key | High | **Nobody sets it.** The chat page makes its own (see KC13) | Inside the chat page container | Changes on every restart (to confirm) |
| KC14 | Hardware and OS accounts: BMC passwords, switch admin, OS root and admin accounts | **Critical** | Installers | Devices | Lab policy |

KC14 belongs to the hardware install. It is listed here so that the inventory is complete; the installers fill it
in ([05](../hardware/05-rack-build-guide.md)).

## How the keys relate

```
 BUILD SIDE (unclassified)          TRANSFER             LAB
 ─────────────────────────          ────────             ───────────────────────────────────────────────
 KC1 signing private key ──signs──▶ bundle ───────────▶ verify.sh checks it with KC2 (public key)
                                                          │ (KC2 must arrive by a SEPARATE route)
                                                          ▼
                                                        deploy.sh installs
                                                          │
           KC9 join token ── lets a machine become a node │
           KC8 cluster admin ── controls everything below ▼
           KC10 cluster certs, secrets key   KC11 Zarf registry ── decides which images run
                                                          │
           KC3 lab CA ──signs──▶ KC4 TLS ── protects the chat page and API on the network
                                                          │
           KC5 master key ──creates──▶ KC6 chat page key, KC7 user keys ── who may use the model
           KC12 database password ── gateway logs and keys      KC13 session key ── chat page logins
```

The pattern: **KC1, KC2, KC8, KC9, KC11 decide what runs in the lab. KC5 decides who can use it. KC4 and KC13
protect what users send.** Anyone who can read Kubernetes secrets (KC8) can read KC4, KC5, KC6, KC12, and KC11.
So the people who hold KC8 effectively hold all of those too.

## Each item

### KC1. Bundle signing private key

| | |
|---|---|
| What it protects | Proof that a bundle came from us and was not changed after sealing. `90-seal.sh` signs the checksum list with it. |
| If leaked or misused | Someone could add malware to a bundle, sign it, and `verify.sh` would accept it. This is the main way unapproved code could get into the lab. |
| Created by | The release owner, once, with `gpg --full-generate-key` (or `cosign generate-key-pair`, S10) |
| Lives in | Today: wherever the release owner keeps it on the build workstation. **Proposed:** on a hardware token (a smart card or USB security key that GPG supports), so the key cannot be copied off it, protected by a PIN. |
| Who can reach it | The release owner only. Proposed: a named backup holder with a second token, kept locked. |
| Must never be | In this repository, in a bundle, on the transfer media, or on a shared machine |
| Expires | Set at creation. Proposed: 2 years. |
| How it is changed | Make a new key, deliver its public half (KC2) by the separate route, then sign the next bundle with it |
| If leaked | Tell the ISSM. Stop all transfers. Revoke the key, make a new one, deliver the new KC2. Re-check every bundle signed since the last known-good date. |

### KC2. Bundle signing public key

| | |
|---|---|
| What it protects | The lab's copy of "what our signature looks like". `verify.sh` checks every bundle against it. |
| If misused | If it travels on the same media as a bundle, whoever tampers with the bundle can swap in their own public key too, and the check passes. Also, today `verify.sh` accepts a signature from **any** key in the admin's GPG keyring, not only ours (finding R5 in [15](15-security-review.md)). |
| Created by | Comes with KC1. Imported into the lab by the lab admin. |
| Lives in | The lab admin host's keyring, used only for bundles |
| How it gets there | **Separately from any bundle**, by a route the ISSM approves. The admin checks its fingerprint against one read out or handed over in person by the release owner. |
| Expires and changes | With KC1 |

### KC3. Lab CA

| | |
|---|---|
| What it protects | It signs the certificates that users' browsers and tools trust |
| If leaked | Someone could make a trusted certificate for any internal name and pose as any internal site |
| Created and held by | The lab's PKI team (open question N6). We never hold it. We only need its public certificate, so analysts' browsers trust our site. |

### KC4. TLS certificate and private key (chat page and API)

| | |
|---|---|
| What it protects | Encrypts everything between users and the service (prompts, answers, passwords, API keys), and proves to users that they reached the real server |
| If leaked | Someone on the lab network could pose as the chat page and collect sign-ins, or read traffic. If it expires unnoticed, the service stops working for everyone. |
| Created by | We make the private key and a certificate request on the lab admin host. The lab CA signs it for both names (chat and API). |
| Lives in | Kubernetes secret `si-tls` (namespace `si`), loaded by `deploy.sh apps --tls-cert --tls-key`. The files given to `deploy.sh` stay on the admin host afterwards. |
| Who can reach it | Root on the admin host; anyone with KC8 |
| Must never be | In a bundle or in this repository |
| Expires | Per the lab CA, often 1 year. Needs a reminder in the operations calendar. |
| How it is changed | Get a new certificate, replace the `si-tls` secret, restart Traefik's routes (no redeploy needed). To be written up and tried in the sandbox. |
| If leaked | Ask the lab CA to revoke it, issue a new one, replace the secret |

### KC5. Gateway master key (LiteLLM)

| | |
|---|---|
| What it protects | Full control of the gateway: create and delete user keys, set limits, read usage logs, change which model a name points to. It is also the password for LiteLLM's admin web page. |
| If leaked | The holder can issue themselves untracked keys, read who asked what, raise their own limits, or point a model name at a different service. |
| Created by | `deploy.sh apps`: 24 random bytes (`openssl rand`), only if the secret doesn't already exist |
| Lives in | Kubernetes secret `litellm-masterkey`. `deploy.sh gateway-key` and `user-key` read it and use it through a port-forward from the admin host. |
| Who can reach it | Anyone with KC8 |
| Must never be | Given to users, or typed into the chat page or a notebook |
| Expires | Never today |
| How it is changed | Not scripted yet. Proposed: a `deploy.sh rotate-master-key` step, run every 6 months and whenever a person who held KC8 leaves. User keys stay valid across a change. |
| If leaked | Replace the secret, restart the gateway, review and revoke keys issued since the leak |

### KC6. Chat page's gateway key

| | |
|---|---|
| What it protects | Lets the chat page call the gateway. Every chat page request is logged under this one key. |
| If leaked | Someone could use the model directly through the API and their use would look like chat page traffic. That is unattributed use, not a takeover. |
| Created by | `deploy.sh gateway-key` |
| Lives in | Kubernetes secret `open-webui-gateway-key` |
| How it is changed | Run `deploy.sh gateway-key` again, then revoke the old key in the gateway |

### KC7. User API keys

**Later phase only.** Phase 1 is the chat page, so no analyst gets a key. This entry is here for when the
analyst tools (Jupyter, VS Code, MATLAB) are added.

| | |
|---|---|
| What it protects | Who used the model (the audit trail) and each user's usage limits |
| If leaked or shared | Someone else's use is logged under the owner's name. That breaks accountability and gets around limits. Keys often end up pasted into notebooks or scripts that are shared. |
| Created by | The admin, with `deploy.sh user-key <name>`. Shown once. |
| Lives in | The gateway database stores only a hash. The user keeps the key in their tool setup on a lab workstation. |
| Must never be | In a notebook, a script, a shared folder, or the chat |
| Expires | Never today. Proposed: 90 days, with a usage limit per key (finding R18). |
| How it is changed | Issue a new key, then revoke the old one. Revoke on the day someone leaves. |
| Handed over by | An approved channel (S23). Proposed: in person, or the lab's approved secure messaging. |

### KC8. Cluster admin credentials

| | |
|---|---|
| What it protects | Full control of Kubernetes: every workload, every secret on this list, every volume |
| If leaked | The holder controls everything, including turning off logging |
| Created by | RKE2 at install (`/etc/rancher/rke2/rke2.yaml`, readable by root only) |
| Who can reach it | Root on svc01, svc02, svc03. **That list of people is the real admin list for the whole system.** |
| Expires | The client certificate inside it lasts 1 year and RKE2 renews it |
| How it is changed | Remove a person's root access. Proposed later: personal admin accounts through single sign-on instead of one shared file. |

### KC9. RKE2 join token

| | |
|---|---|
| What it protects | Decides which machines may join the cluster |
| If leaked | A rogue machine on the lab network could join as a node. The cluster would then schedule workloads, and the secrets they use, onto it. |
| Created by | RKE2 at `deploy.sh server-init` |
| Lives in | `/var/lib/rancher/rke2/server/node-token` on svc01, and `/etc/rancher/rke2/join-token` (root only) on each node that joined |
| Known issue | `deploy.sh server-init` prints it to the terminal, so it can end up in scrollback or a session log (R12) |
| Expires | Never, until rotated |
| How it is changed | `rke2 token rotate` once all nodes have joined, and again if a node is replaced. To be tried in the sandbox. |

### KC10. Kubernetes internal certificates and the secrets encryption key

| | |
|---|---|
| What it protects | Traffic between cluster parts, and Kubernetes secrets at rest (RKE2 encrypts them on disk by default) |
| If leaked | Someone who also has the server's disk can read every Kubernetes secret |
| Created by | RKE2 at install, under `/var/lib/rancher/rke2/server/` on the server nodes |
| Expires | Certificates last 1 year and RKE2 renews them when it restarts close to expiry. If the cluster runs untouched past expiry, it can stop working. |
| How it is changed | `rke2 certificate rotate` and `rke2 secrets-encrypt rotate-keys`. Schedule yearly. To be tried in the sandbox. |

### KC11. Zarf registry and agent credentials

| | |
|---|---|
| What it protects | The in-cluster image registry that every pod pulls from, and the Zarf agent that rewrites image names to point at it |
| If leaked | Someone could push their own image under an approved name, and pods would run it on the next restart. That bypasses the whole bundle check. |
| Created by | `zarf init`, random |
| Lives in | Kubernetes secret `zarf-state`. `zarf tools get-creds` prints them for anyone with KC8. |
| How it is changed | `zarf tools update-creds`. Proposed: once after install, and whenever KC8 holders change. |

### KC12. Gateway database password

| | |
|---|---|
| What it protects | The gateway's database: user keys (hashed), usage records, spend, and request logs |
| If leaked | Someone could read or change usage records and could delete log entries |
| Who sets it | **The CloudNativePG operator.** When it creates the `si-postgres` cluster (`manifests/pg-cluster.yaml`), it makes the `litellm` database owner with a random password and stores it in the secret `si-postgres-app`. The gateway reads it from that secret (`values/litellm.yaml`). Nobody types it. The `postgres` superuser has no password and can't log in over the network, because CloudNativePG turns superuser access off by default. |
| Lives in | Kubernetes secret `si-postgres-app` |
| Expires | Never |
| How it is changed | Change the secret and let the operator apply it, then restart the gateway. To be tried in the sandbox. |

### KC13. Chat page session-signing key

| | |
|---|---|
| What it protects | Every chat page login. After a user signs in, the chat page gives their browser a token signed with this key. |
| If leaked | Someone could make a valid login token for **any** user, including the admin, without a password, and read their chat history and uploaded documents |
| Who sets it | **Nobody, today.** Our settings don't set it (`values/open-webui.yaml`), and the Open WebUI chart 17.5.0 doesn't either. So the container's start script (`backend/start.sh` in Open WebUI v0.12.5) makes a random 24-byte key at first start and writes it to `/app/backend/.webui_secret_key`. That path is **outside** the data volume (`/app/backend/data`), so it is likely remade on every restart. That logs everyone out, and no one controls or backs up the key. To confirm in the sandbox. |
| Proposed | `deploy.sh apps` creates the secret `open-webui-secret-key` (random, once), and the chart values pass it to the chat page as `WEBUI_SECRET_KEY` (finding R16) |
| How it is changed | Replace the secret and restart. Every user has to sign in again. |

The chat page has **no database password**. Its chat history and settings are a database file (SQLite), and its
document vectors are files, both on its own volume on one node's disk. Anyone with KC8 or root on that node can
read every user's chats. Whether that is acceptable is a data question for Cyber (finding R24).

## What Cyber needs to decide

| Register | Question |
|---|---|
| S10 | Signing tool (GPG or cosign), who holds KC1 and the backup, whether a hardware token is required, how KC2 reaches the lab |
| S23 | How user keys are handed to users. Key lifetimes: user keys (proposed 90 days), master key (proposed 6 months), TLS certificates (lab CA policy). |
| S24 | Who may hold cluster admin (KC8), that is, root on svc01-03 |
| S25 | Whether data on the server disks must be encrypted at rest (chat history, uploads, databases, models) |

## What we will add to the scripts

All are tracked as findings in the security review ([15](15-security-review.md)):

- `verify.sh`: accept only our signing key by fingerprint, not any key in the keyring (R5)
- `deploy.sh server-init`: stop printing the join token; tell the admin which root-only file to copy (R12)
- `deploy.sh apps`: create the chat page session key as a secret (R16)
- `deploy.sh user-key`: set an expiry and usage limits on each new key (R18)
- New steps: rotate the master key, Zarf credentials, and join token, and replace the TLS certificate. Each one
  tried in the sandbox.
- A key calendar: TLS expiry, Kubernetes certificate expiry, signing key expiry, user key expiry
