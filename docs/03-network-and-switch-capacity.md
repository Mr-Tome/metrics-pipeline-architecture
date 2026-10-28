# 03. Network and switch capacity

![Network cabling](diagrams/network-cabling.svg)

## 1. What the lab told us

- 2 x "C9300-485" access switches, uplinked to a C9500X core.
- Links between them "might be fiber" and are 10Gb.

"C9300-485" is almost certainly a misread of a Catalyst 9300 model. **C9300-48S** (48 x 1G SFP) is the
closest match. Other options are C9300-48P, -48T, -48U, or -48UXM. The exact model changes what the
user-facing ports are, but it does not change the conclusion below. Ask the network team for
`show inventory` from each switch ([07-open-questions.md](07-open-questions.md), N1).

## 2. Is 10G enough? For the AI phase, yes, by a wide margin

The language model runs on our GPU server, in our rack. What crosses the lab network is text going in and
text coming out. Rough numbers:

| Traffic | Size | 20 users at peak | Notes |
|---|---|---|---|
| Chat prompt + streamed answer | 10 to 200 KB per request | under 5 Mbps total | Streaming sends tokens as small chunks. |
| Large document pasted or uploaded | 1 to 50 MB, now and then | bursts, under 1 s at 1G | Limited by the user's own 1G desk port, not the 10G uplink. |
| Voice note for transcription | 1 to 10 MB | negligible | |
| Model weights | about 65 GB | **0 on the lab network** | Loaded from local NVMe in the GPU server. |
| Cluster-internal traffic (gateway to GPU, database) | moderate | stays inside sw01 | Never touches the C9300/C9500X. |

A 10G uplink carries about 1,250 MB/s. Twenty users chatting use well under 1% of it.

**Where capacity does matter:**

1. **Inside our rack (east-west).** The gateway, chat page, and database on the service nodes talk to
   the GPU server constantly. That is why the BOM has its own 25G switch (sw01). This traffic never
   leaves the rack.
2. **Later pipeline phases.** Bulk test-data onboarding (telemetry, video, large datasets) can saturate
   10G. That is a future concern, and the preferred uplink (section 3, option A) already handles it.
3. **Multi-server model serving.** Splitting one model across two servers needs very fast links
   (InfiniBand or RoCE at 200-400G). **We avoid this by design.** gpt-oss-120b is about 65 GB at its native
   4-bit format, so it fits on one 96 GB GPU. Adding users adds more copies of the model on more GPUs,
   not one model spread across servers.

## 3. How our rack connects

**Option A (preferred): lab switch to the C9500X core, 2 x 100G.**

- The C9500X-28C8D has 28 x 100G QSFP28 and 8 x 400G QSFP-DD ports. If two 100G ports are free,
  this is the cleanest design. It does not touch the access layer, and it is ready for the later pipeline.
- sw01 (S5248F-ON) has 4 x 100G QSFP28 uplinks. Use two in an LACP port-channel to the core.
- Optics depend on the fiber the lab already has:
  - Multimode (OM4) with MPO: **100GBASE-SR4**, up to 100 m.
  - Single-mode with LC: **100GBASE-LR4** or **CWDM4**.
- Coding: use Cisco-coded optics in the C9500X and Dell-compatible optics in sw01. Check the Cisco
  optics-to-device compatibility matrix for the lab's IOS-XE version before ordering.

**Option B (fallback): 2 x 10G from the C9300 network modules.**

- Use this if the core has no free ports or the network team won't allow it.
- It requires the C9300s to have a network module with free 10G ports (for example C9300-NM-8X,
  8 x 10G SFP+).
- sw01's 25G SFP28 ports accept 10G SFP+ optics. No extra hardware is needed on our side beyond
  10GBASE-SR (multimode) or -LR (single-mode) optics.
- This is enough for the whole AI phase (section 2). Later pipeline phases may need Option A.

**Not recommended:** plugging the GPU server straight into a C9300 user port. The service nodes then
reach the GPU over the access layer, and the network team has to support our east-west traffic.

## 4. InfiniBand (BOM tab, cell B21)

Not needed. InfiniBand is for spreading training or one large model across many servers. This design
serves one model copy per GPU and does no multi-node training. 25GbE inside the rack is enough.
If multi-node fine-tuning ever becomes a requirement, revisit it then. The rack has room and power for it.

## 5. Checking switch capacity: steps for the network team

These are read-only commands. Ask the lab network team to run them (we should not have access to their
switches) and send back the output. `validate/net-test.sh` runs the matching tests from our side.

**On each C9300 and on the C9500X:**

```
show version
show inventory
show interfaces status
show etherchannel summary
show interfaces <uplink-interface> | include rate|drops|errors
show platform resources
```

What to look for:

| Output | Question it answers | Healthy |
|---|---|---|
| `show inventory` | Exact model, network modules, optics present | Model numbers to put in our docs |
| `show interfaces status` | Free ports and their speeds | 2 free 100G on the core (option A) or 2 free 10G on a C9300 (option B) |
| `... include rate` (5-minute rate) on the 10G uplinks | Current load at a busy time of day | Under 50% of 10 Gbps |
| `... include drops\|errors` | Congestion or bad optics | Output drops and CRC errors near 0 and not climbing |
| `show etherchannel summary` | Are the two 10G links bonded (20G total) or is one a standby? | Both members flagged `P` (bundled) |

**End-to-end test, after our rack is connected:**

1. From one analyst workstation, run `iperf3 -c <svc01-ip> -P 4 -t 30`. Expect close to the desk port
   speed (about 940 Mbps on a 1G port).
2. From two or three workstations on different access switches at once, confirm each still gets close to
   its desk speed.
3. Inside the rack (`validate/net-test.sh`): node to node should reach about 23 Gbps per 25G link.
4. Load test: run `validate/llm-load-test.py --users 4`. Four parallel users is the 20-user peak from the BOM.
   Time-to-first-token should stay under about 2 s.
