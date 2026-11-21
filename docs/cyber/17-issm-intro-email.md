# 17. First email to the ISSM (sent)

**Track:** Cyber Security ([package index and decision register](README.md)).
**Status:** Sent, with the phase 1 part of the phased software list. Record the ISSM's answers in the decision register. As drafted, it was to attach the phased software list
([16-phased-sbom.csv](16-phased-sbom.csv)) and the model list ([13](13-model-bom.md)).

The email uses plain questions without our internal IDs. The table at the end maps each question to the
decision register so answers can be recorded there.

---

**Subject:** Introduction and first questions: SI chat service for analysts in RF

Hi [ISSM name],

I'm [your name], I am working under [] and have recently been mapped into RF, under the leadership of []. I am a [your role], and I am working with a large group of individuals on the metrics analysis pipeline. We're preparing to install a small GPU system in the lab (PR is being worked by [] and []) and I'd like to bring you in now, before anything goes into the lab, so the security review has the ability to shape the plan and implementation.

**What we're building**

- **Initial Goal:** give analysts, a Radar Engineer, and others within the lab a language model ("SI") that they can use inside the lab. 
- **First phase (what this email is about):** analysts use SI through a chat page in their browser. They can ask questions, dictate by voice, and upload a document to ask about it. I'm hoping that the server will adequately provide these basic capabilities for about 20 users. Note: during the first phase, nothing is intended to be installed on analysts' PCs.
- **Hardware:** one GPU server (four GPUs), three service servers, a Cisco Nexus switch, and a small
  management switch, in the existing racks next to ACE 15.
- **How I was planning for software to get in:** everything would be downloaded on a build workstation outside the lab, scanned, and installed tested in an "offline" test machine (probably going to be the same as the build machine with the internet disconnected). The package would then be prepared for transfer in a single signed bundle, then provided to your team (or whoever is approved to do this) on  approved media. Once your team approved the contents, we would work through standing up the software stach on the aforementioned hardware.
- **Future phase (not part of this request):** letting analysts call SI from Jupyter, VS Code, and MATLAB. Connecting shared platform services (lab sign-in, GitLab, monitoring) and the metrics pipeline itself. When we can prove out the hardened workflows, installations of SI Agents on individuals machines. Note: I intend to present each of these future concepts to you as its own request & capability, but they'll all be building off of eachother. They're in the attached list so you can see where this is going.

**What's attached**

- **Phased software list (spreadsheet):** every item for every phase, with its version, license, and the
  exact link it is downloaded from. Phase 1 is the part we're asking you to review first.
- **Model list:** each model file, who made it, its country of origin, and its file format. All models
  will be made in the USA.

We've listed everything we might bring, including alternatives we're still choosing between, rather than
filtering it ourselves. Please tell us what is and isn't allowed.

**A few quick questions to start**

1. What is the approved process to bring new hardware into the lab?
2. Does accreditation require a specific server operating system or baseline (for example RHEL 9 with a
   STIG)? If not, we plan to use Rocky Linux 9. Is there a lab package mirror we can use for OS updates?
3. What transfer media is approved? Does the lab provide it, and how long does a transfer usually take?
4. Is Secure Boot required on the servers?
5. Who on your team should we work with, and in what format would you like the software list
   (spreadsheet, CycloneDX, or SPDX)?

**More detailed questions** (we have a proposal for each and would be glad to go through them together)

6. **Container images:** may we use the projects' own published images, or only Iron Bank images where
   Iron Bank has them?
7. **Model files:** which file formats are allowed? We propose only formats that cannot run code when they
   are loaded (safetensors and CTranslate2).
8. **Made in the USA:** does the rule cover only who publishes a model, or also the model it was built from
   and whoever converted it?
9. **Signing the bundle:** GPG or cosign, who should hold the signing key, and how our public key should
   reach the lab.
10. **Driver build:** installing the NVIDIA driver needs a few OS packages (gcc, kernel-devel, and dkms from
    EPEL). Should they come from the lab mirror, or in our bundle?
11. **Switch setup:** to set up our own rack switch (sw01) the first time, we'd plug a USB-to-serial console
    cable into svc01 for about an hour, then remove it. It stays inside our rack and touches no lab network.
    Is a USB serial adapter allowed on svc01, or would you rather we use an approved laptop?
12. **Testing hardware first:** may new servers be tested outside the lab before they go in (then wiped), or
    should all testing happen inside?
13. **Admin access:** who may hold full admin rights on the cluster? That role can read every chat and log.
14. **Encryption:** must chat history, uploaded files, and logs be encrypted on disk?
15. **Audit records:** what must the log record (including the questions and answers?), how long is it kept,
    and where should it go so that admins can't change it?
16. **Keys and certificates:** how long should service keys and the site's certificate last?
17. **Choices we've left open:** where the list shows two options (the chat page's standard or slim image,
    the speech-to-text server, the embedding model), please tell us which are acceptable.

We've also done our own security review of the plan and an inventory of every key and certificate it uses.
We'd like to walk you through both. Could we set up an hour in the next two weeks?

Thanks,
[your name]
[phone / email]

---

## Question map (not part of the email)

| Email question | Decision register |
|---|---|
| 1 | S1 |
| 2 | L1 |
| 3 | S3 |
| 4 | S4 |
| 5 | Review contacts; SBOM format is finding R33 in [15](15-security-review.md) |
| 6 | S6 |
| 7 | S20 (and S21) |
| 8 | S22 |
| 9 | S10 |
| 10 | S11 |
| 11 | S8 |
| 12 | S2 |
| 13 | S24 |
| 14 | S25 |
| 15 | S26 |
| 16 | S23 |
| 17 | S13, S12, S5 |

Not asked yet, because they come up once the review starts: S14 (licenses), S15 (RKE2's outbound
reporting, which we switch off), S16 (known shortcuts), and S9 (deferred model).
