# 08a. Quote request: servers and GPUs (submitted)

**Track:** Hardware (facility, network, rack, purchasing). Security decisions are in the [Cyber Security package](../cyber/README.md).

**Status: submitted to purchasing as a PR, 2026-11-04.** This is the record of what was asked for.
Do not resend. The network, rack, and setup items are in [08b](08b-quote-network-and-rack.md).

Item numbers are kept from the original single request so references in other docs still match.

Links were checked on 2026-10-29. Thinkmate links open the configurator at its default settings.
Thinkmate does not support links with options already selected, so the options to pick are listed in
each item. "Save This Config" or "Email" on the Thinkmate page creates a saved configuration that
can be sent with the quote request.

---

**Subject:** Quote request: GPU server, GPUs, and service nodes, metrics analysis pipeline (50-user build)

Please get quotes for the items below. Estimated total is $187,025. Government pricing (GSA, SEWP) is welcome.

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 1 | GPU server, 2U, 4 GPU slots. Select: 2 x AMD EPYC 9115 (16-core, 2.60 GHz); 12 x 32GB DDR5-6400 ECC RDIMM (384 GB); 2 x 3.84TB Micron 7600 PRO U.2 NVMe; Intel E810-XXVDA2 (2 x 25G SFP28); TPM 2.0; 5 Year Advanced Parts Replacement Warranty; OS per question 6 below. | Thinkmate GPX GE95-2206-41 | 1 | $47,792 | $47,792 | https://www.thinkmate.com/system/gpx-ge95-2206-41 |
| 2 | GPU, installed in item 1 (select in item 1 as "NVIDIA RTX PRO 6000 Blackwell Server Edition - 96GB", qty 4, all four GPU slots) | NVIDIA RTX PRO 6000 Blackwell Server Edition 96 GB, mfr NVRTXPRO6000TCGPU-KIT | 4 | $18,246 | $72,984 | https://www.cdw.com/product/nvidia-rtx-pro-6000-blackwell-server-edition-graphics-card-rtx-pro-60/8426124 |
| 3 | Service node, 1U. Redundant 1300 W PSUs are part of the base system (the "Barebone" line), nothing to select. Select: AMD EPYC 9115 (16-core); 128 GB DDR5 ECC RDIMM; 2 x 1.92TB U.2 NVMe; Broadcom N225P OCP 3.0 (2 x 25G SFP28); 5 Year Advanced Parts Replacement Warranty | Thinkmate RAX RE95-1104-01 | 3 | $22,083 | $66,249 | https://www.thinkmate.com/system/rax-re95-1104-01 |

**Total: $187,025**

**Only if needed (not in the total)**

| # | Item | When | Qty | Est. total | Link |
|---|---|---|---|---|---|
| 13 | Red Hat Enterprise Linux Server, Standard, 1 year, 2 sockets, 1 physical node (RH00004) | If the OS must be RHEL (question 6). One per server: gpu01 and svc01-svc03. Can also be selected in the Thinkmate configurator ("Red Hat Enterprise Linux 9 Server (Standard) (1 Year)"). Rocky Linux 9 is free and needs none. | 4 | $5,600 per year | https://cdw.com/product/red-hat-enterprise-linux-server-standard-subscription-2-sockets-1-phys/6905904 |

With it, the total is $192,625.

**Questions**

1. **GPU server power cords.** The server has 4 x 2000 W PSUs. Is the PSU inlet C14 or C20? The site's
   rack PDUs have mostly C13 outlets and three C19 outlets per PDU.
   - If C14: we need 4 x C13-to-C14 cords, 6 ft (1 server, 4 total). (Preferred, if offered.)
   - If C20: we need 4 x C19-to-C20 cords, 6 ft (1 server, 4 total).
   - Do not ship NEMA 5-15P (wall plug) cords. The configurator only offers those.
2. **Service node power cords.** 2 x C13-to-C14 cords per node, 6 ft (3 nodes, 6 total), no NEMA 5-15P.
3. **Factory install.** Please install all 4 GPUs (item 2) and the 25G NICs at the factory, and burn in the GPU server with all 4 GPUs loaded.
4. **Rails.** The racks are Vertiv VR3300 with square holes, vertical rails adjustable, currently 29 in
   apart. Do the rail kits for items 1 and 3 fit?
5. **Lead time** for each item, especially the GPUs.
6. **Operating system.** Does the lab require a specific server OS (for example RHEL 9 with STIG)? If it
   must be RHEL, each server needs a Red Hat subscription (item 13, about $1,400 per server per year),
   which is not in the original BOM. If the lab allows it, Rocky Linux 9 is compatible and free.
