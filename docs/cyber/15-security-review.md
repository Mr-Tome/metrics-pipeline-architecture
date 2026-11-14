# 15. Security review of the phase 1 plan (our own, before meeting the ISSM)

**Track:** Cyber Security ([package index and decision register](README.md)).
**Status:** Draft, 2026-11-14. A review of the plan **as it is today**: the delivery and install scripts, the chart
settings, and documents 12 to 14. It is our own check, written so that we walk into the ISSM meeting knowing our
weak spots, with a fix or a proposal for each.

**Phase 1 is the chat page only.** Analysts use SI through a browser. There is no API address and no analyst
tools or keys; those are a later phase, and findings that apply only to them are marked *Later*.

Many of these were already tracked as W items in the sandbox plan ([11](../software/11-sandbox-bringup-plan.md),
section 7). They are repeated here so that every security issue is in one list. New findings start with "New."

## How to read it

**Severity**
- **High:** someone could put unapproved software into the lab, take over a service, or act as another user
  without being noticed. Fix before the bundle crosses or before users get access.
- **Medium:** weakens a control, or leaves us unable to show the ISSM that a control works.
- **Low:** good practice; a reviewer is likely to ask.

**When:** *ISSM* = we need their decision; bring a proposal. *Before transfer* = fix before the bundle crosses.
*Before users* = may cross, but fix before analysts get access. *Later* = accepted for phase 1, written down.

**Control** is the NIST SP 800-53 control family a reviewer will file it under, to help match their checklist.

## Before the ISSM meeting

1. **Fix the cheap script findings now** (each is a few lines, then a sandbox run): R5, R7, R12, R16, R18, R23.
   R19 is already closed for phase 1: there is no API address. That turns them from findings into "done" in the meeting.
2. **Bring a proposal for each decision** we need from them: signing key custody (S10), how keys are handed out
   and how long they last (S23), who may be cluster admin (S24), disk encryption (S25), log content and retention
   (W10), and the USA-only model rule's scope (S22).
3. **Bring dates** for the "before users" work: network policies (R9), sign-in hardening (R17), backups (R26),
   monitoring (R27).

## Findings

### A. Building and signing the bundle (connected side)

| ID | Finding | How it could be misused | Fix | Sev. | When | Control |
|---|---|---|---|---|---|---|
| R1 | New. The build workstation is not defined: which machine, who uses it, how it is patched. It is connected to the internet and produces what the lab trusts. | Malware on that machine could alter files before sealing. The signature would then vouch for the altered files. | A dedicated machine used only for pulls and sealing, patched, with no email or browsing. Two people review the `versions.env` diff and the scan `SUMMARY.txt` before sealing, and both are named in the bundle record. | High | ISSM | SR-3, CM-7 |
| R2 | New. The signing key's custody is not set (S10). Today it is a file wherever the release owner keeps it. | Anyone who copies the file can sign bundles as us ([14](14-key-and-certificate-inventory.md), KC1). | Key on a hardware token with a PIN, one named holder and one named backup, 2-year expiry | High | ISSM | SC-12, SI-7 |
| R3 | Images are referenced by tag. Digests are recorded after the pull, not pinned before it. Upstream signatures are not checked. (W7) | A tag can be moved upstream to a different image between two pulls | After the first reviewed pull, pin each image by digest. Check upstream signatures where the project publishes them. Iron Bank where it exists (S6). | Medium | Before transfer | SR-4, SI-7 |
| R4 | New. The analyst Python packages (100 or more per platform) and the VS Code extension are not scanned. Only container images are. | A known-vulnerable package goes onto analysts' Windows machines unnoticed | Phase 1 brings none of these (chat page only; `clients/` is left out). When the analyst tools are added: scan `clients/RESOLVED.txt` with Trivy as a requirements list, and review the extension's publisher and version by hand. | Medium | Later | RA-5 |

### B. Transfer and intake (lab side)

| ID | Finding | How it could be misused | Fix | Sev. | When | Control |
|---|---|---|---|---|---|---|
| R5 | New. `verify.sh` runs `gpg --verify`, which accepts a good signature from **any** key in the admin's keyring, not only ours | If any other key is in that keyring, a bundle signed with it passes intake | Check the signer's fingerprint against our pinned fingerprint, using a keyring that holds only our key | High | Before transfer | SI-7 |
| R6 | New. How the public key reaches the lab is not defined | If it comes on the same media as a bundle, a tamperer can swap both and the check means nothing | A separate route approved by the ISSM. The admin checks the fingerprint against the release owner's, given in person. | High | ISSM | SC-12 |
| R7 | New. Model files are checked against a list of **banned** extensions (`.bin`, `.pt`, and so on). Anything not on that list passes. | A file type we didn't think of (for example NumPy or joblib files, which can also hold pickle) gets through | Turn it around: a list of **allowed** file types (safetensors, JSON, text, tokenizer files, the Jinja chat template, header-checked CTranslate2). Refuse everything else, including `.py` (S21). | Medium | Before transfer | SI-7, CM-7 |
| R8 | New. We don't know what the lab's own intake does (scanning, review, who signs off) (S3) | Our scan is the only scan, done by the people who built the bundle | Ask for the lab's process. Send `SUMMARY.txt` ahead of each transfer. | Medium | ISSM | SR-11 |

### C. Cluster platform

| ID | Finding | How it could be misused | Fix | Sev. | When | Control |
|---|---|---|---|---|---|---|
| R9 | No network policies (W8). vLLM, Whisper, embeddings, and Tika have no sign-in of their own. | Any pod, or anything else that reaches the pod network, can call the model directly. That skips the gateway's keys, limits, and logs. | Default-deny in namespace `si`. Allow only: gateway to model services, chat page to gateway and Tika, gateway to PostgreSQL, Traefik to chat page and gateway. | High | Before users | SC-7, AC-4 |
| R10 | No CIS hardening profile and no pod security enforcement (W11) | A compromised container can do more on its node than it needs to | RKE2 `profile: cis`, with the GPU Operator and storage namespaces exempted. Rehearse in the sandbox. | Medium | ISSM | CM-6 |
| R11 | New. We set no Kubernetes audit policy. What RKE2 records by default has not been checked. | Changes to the cluster (new pods, secrets read) may leave no record | Set an audit policy that records secret reads, changes, and `exec` into pods. Send those logs where admins can't edit them. | Medium | Before users | AU-2, AU-12 |
| R12 | New. `deploy.sh server-init` prints the join token to the terminal. There is no rotation step. | The token stays in scrollback or session logs. A machine with it can join the cluster (KC9). | Stop printing it. Point the admin to the root-only file. Run `rke2 token rotate` after all nodes join. | Medium | Before transfer | IA-5 |
| R13 | New. Root on svc01-03 equals control of everything: all secrets, the Zarf registry, all data ([14](14-key-and-certificate-inventory.md), KC8, KC11). Who has it is not defined (S24). | One person with root can push an image, read every chat, and change logs | Name the admins (S24). Rotate Zarf credentials after install. Later: personal admin accounts through single sign-on. | Medium | ISSM | AC-6, AC-2 |
| R14 | New. Traffic inside the cluster is not encrypted (chat page to gateway to model, plain HTTP) | Someone with access to a node or the pod network could read prompts in transit | R9 limits who can reach it. If the ISSM requires encryption inside the cluster, add a service mesh later (Big Bang has one). | Low | ISSM | SC-8 |
| R15 | New. Nothing tracks certificate expiry (TLS, Kubernetes, signing key) | An expiry takes the service down, and renewing in an air gap is slow | Key calendar ([14](14-key-and-certificate-inventory.md)), and a check in `deploy.sh status` that warns 60 days out | Low | Before users | SC-17 |

### D. SI services

| ID | Finding | How it could be misused | Fix | Sev. | When | Control |
|---|---|---|---|---|---|---|
| R16 | New. Nobody sets the chat page's session-signing key. The chat page makes one in a spot that is likely lost on every restart ([14](14-key-and-certificate-inventory.md), KC13). | The key is uncontrolled and unbacked. If anyone reads it, they can sign in as any user, including the admin. | `deploy.sh apps` makes it once as a Kubernetes secret; the chart values pass it to the chat page | High | Before users | IA-5, SC-12 |
| R17 | The first person to open the chat page becomes its admin, and anyone can sign up (W9) | Whoever reaches the page first after install owns it | Create the admin during install, then turn sign-up off. Accounts are created by the admin. | High | Before users | AC-2 |
| R18 | The gateway master key and the chat page's gateway key never change. User API keys (later phase) would never expire and have no limits. (W9) | A leaked key works forever, with no cap | Add a rotation step for both keys. For the later phase, `deploy.sh user-key` sets a 90-day expiry and a request limit, and keys are revoked when someone leaves. | Medium | Before users | IA-5, AC-2 |
| R19 | New. If the gateway API address is opened (later phase), its admin web page and admin API (create keys, read logs) are reachable from the whole lab network. The master key is the login. Phase 1 opens no API address, so today the gateway is reachable only inside the cluster. | Anyone who gets the master key could manage the gateway from any desk | Phase 1: done (2026-11-14, `apps` without `--api-host`). Later phase: block the admin page and admin API paths at Traefik, so only the model paths are public. | Medium | Later | AC-17, CM-7 |
| R20 | New. Chat page features we don't use may be on by default: admin-added "Functions" and "Tools" (Python that runs on the server), code execution, and fetching web addresses | An admin account, or a mistake, could run code on the server. URL fetching can be used to probe internal sites from the server. | List what is on in v0.12.5. Turn off everything we don't use. Check in the sandbox. | Medium | Before users | CM-7 |
| R21 | The speaches server has had no stable release since 2025-09-19 (S12) | Known flaws stay unpatched | S12: keep faster-whisper with a maintained server, or move to vLLM | Medium | Before transfer | SI-2 |
| R22 | Telemetry off-switches are set but not proven (W12). `rke2-security-responder` may report the cluster version to SUSE (S15). | Repeated outbound attempts set off the lab's alarms, or would leak if a route ever existed | The sandbox network tripwire (C16) must show none. Turn off the responder if it tries. | Medium | Before transfer | SC-7 |
| R23 | New. The chat page trusts the client address in forwarded headers from any source (Open WebUI default) | Logs can show a false client address | Trust forwarded headers only from Traefik | Low | Before users | AU-3 |

### E. Data and records

| ID | Finding | How it could be misused | Fix | Sev. | When | Control |
|---|---|---|---|---|---|---|
| R24 | New. Chat history and uploaded documents sit in a database file on one node's disk, readable by any admin. Nothing on the server disks is encrypted at rest. | An admin, or anyone who takes a disk out, can read every user's chats and documents | ISSM decision (S25). Options: encrypted data disks (LUKS), and a written rule on who may read user data. Moving chat data into PostgreSQL (W23) adds copies but not encryption. | Medium | ISSM | SC-28, AC-6 |
| R25 | The audit trail records who called and how much, not what was asked or answered. Logs sit in the gateway database, which admins can change. (W10) | Misuse can't be reconstructed, and an admin could erase their own tracks | ISSM decides content and retention. Then log prompts and responses if required, and copy logs to a place admins can't edit (the lab's log service, if there is one). | High | ISSM | AU-2, AU-9, AU-11 |
| R26 | No backups (W13), including the secrets in [14](14-key-and-certificate-inventory.md) | A lost disk means lost chat history, keys, and usage records | Scheduled PostgreSQL dump and chat page data copy to the lab's NFS share. Keep the backups as protected as the originals. | Medium | Before users | CP-9 |
| R27 | No monitoring or alerting (W15) | Attacks and failures go unnoticed | Minimal Prometheus and Grafana, or at least a scheduled check that someone reads, including failed sign-ins at the gateway | Medium | Before users | SI-4 |
| R28 | New. In the later analyst-tools phase, analysts would keep an API key on their workstations: in notebooks, MATLAB scripts, VS Code settings. Phase 1 gives analysts no keys. | Keys spread through shared notebooks and scripts (KC7) | One-page guidance before that phase: the key goes in an environment variable or the tool's secret setting, never in a file you share. | Medium | Later | IA-5 |

### F. Models

| ID | Finding | How it could be misused | Fix | Sev. | When | Control |
|---|---|---|---|---|---|---|
| R29 | New. The USA-only model rule (S22) conflicts with the current choices once lineage counts. **M3** (Snowflake, USA) is built on BAAI's `bge-m3-retromae` (BAAI is in China). **M2** is OpenAI's Whisper weights, but converted and published by Systran (France). The standard chat page image carries **E2**, which is distilled from a BAAI model, and E1 and E3. | Not misuse, but a likely rejection in review | Ask the program whether the rule covers who published the model or its whole lineage. If lineage: replace M3 with IBM's `granite-embedding-278m-multilingual` (IBM, USA; covers our six languages), and convert OpenAI's Whisper to CTranslate2 ourselves from OpenAI's own files instead of using Systran's copy. See [13](13-model-bom.md). | High | ISSM | SR-3, SR-4 |
| R30 | `.py` files in model folders are not refused. Models inside container images skip the model intake. (S21) | Model code arrives unreviewed. A model could come in that nobody listed. | R7 (allowed-types list). Run the same check over the image contents. | Medium | Before transfer | SI-7 |

### G. Process

| ID | Finding | How it could be misused | Fix | Sev. | When | Control |
|---|---|---|---|---|---|---|
| R31 | New. No written steps for a leaked key, a compromised bundle, or an urgent security fix | Slow, improvised response in an air gap, where each fix costs a transfer | One page per case: who to tell, what to revoke, how an urgent bundle is built and checked | Medium | Before users | IR-4, SI-2 |
| R32 | New. Not decided whether this repository's documents and the training pages (HTML with JavaScript) go into the lab | Unreviewed active content in the lab | Decide; if they go in, they're part of the bundle and its checksums | Low | ISSM | CM-7 |
| R33 | The scan records are in Syft and Trivy formats, not the CycloneDX or SPDX formats some reviewers require | Extra work at review time | Add a CycloneDX export if Cyber wants it ([12](12-software-bom.md), section 9) | Low | ISSM | CM-8 |

## Count

| Severity | Count | Of which new |
|---|---|---|
| High | 9 | 6 |
| Medium | 19 | 11 |
| Low | 5 | 4 |
| **Total** | **33** | **21** |
