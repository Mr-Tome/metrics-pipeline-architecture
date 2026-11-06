# 03. Network and switch capacity

![Network cabling](diagrams/network-cabling.svg)

## 1. What the lab told us

- The lab is installing a **Cisco C9500X-28C8D** core above rows 2 and 3 (28 x 100G QSFP28, 8 x 400G
  QSFP-DD). It runs IOS XE 17.15.06 (the lab tracks the second-latest Cisco MD release).
- Our switch connects directly to it at 100G, and we supply the optics for both ends (2026-11-04).
- Its own uplink to the rest of the lab network is 10G. Analysts reach our rack through the lab network
  and that uplink.
- The only patch panels are in the middle rack of rows 2 and 3, for fiber back to the main building. Our
  racks have none. Our cords run directly between switches, so we choose the fiber type (section 3).
- Older notes mention C9300-48S access switches, and on 2026-11-06 the team briefly pointed us at their
  N93180YC-FX3 access switches. They then confirmed the direct C9500X-28C8D connection: the
  N93180YC-FX3 answer came from taking our switch for a server.

## 2. Is 10G enough? For the SI phase, yes, by a wide margin

The language model runs on our GPU server, in our rack. What crosses the lab network is text going in and
text coming out. Rough numbers:

| Traffic | Size | 50 users at peak | Notes |
|---|---|---|---|
| Chat prompt + streamed answer | 10 to 200 KB per request | under 10 Mbps total | Streaming sends tokens as small chunks. |
| Large document pasted or uploaded | 1 to 50 MB, now and then | bursts, under 1 s at 1G | Limited by the user's own 1G desk port, not the 10G uplink. |
| Voice note for transcription | 1 to 10 MB | negligible | |
| Model weights | about 65 GB | **0 on the lab network** | Loaded from local NVMe in the GPU server. |
| Cluster-internal traffic (gateway to GPU, database) | moderate | stays inside sw01 | Never touches the C9500X-28C8D. |

The narrowest link users cross is the C9500X-28C8D's 10G uplink. 10G carries about 1,250 MB/s. Fifty users chatting use well under 1% of it.

**Where capacity does matter:**

1. **Inside our rack (east-west).** The gateway, chat page, and database on the service nodes talk to
   the GPU server constantly. That is why the BOM has its own 25G switch (sw01). This traffic never
   leaves the rack.
2. **Later pipeline phases, maybe.** If a later phase moves large test data sets into the rack, 10G
   could become the limit. Whether that happens depends on future pipeline scope, which isn't set.
   It doesn't change this purchase.
3. **Multi-server model serving.** Splitting one model across two servers needs very fast links
   (InfiniBand or RoCE at 200-400G). **We avoid this by design.** gpt-oss-120b is about 65 GB at its native
   4-bit format, so it fits on one 96 GB GPU. Adding users adds more copies of the model on more GPUs,
   not one model spread across servers.

## 3. How our rack connects (decided 2026-11-06)

The network team confirmed (2026-11-06): direct to the C9500X-28C8D, 2 x 100G for data, plus a third
port for a separate management link. The racks are about 12 ft apart (their estimate). Our top-of-rack
switch is a **Cisco Nexus N93180YC-FX3**, so every optic is Cisco on both ends.

```
LAB
  C9500X-28C8D (lab core), 3 ports for us
     |-- 2 x 100G data, multimode LC fiber, bonded (LACP) ------> sw01
     |-- 1 x 10G management, multimode LC fiber (QSA adapter) --> oob01
OUR RACK (next to ACE 15)
  sw01  Cisco Nexus N93180YC-FX3 (data switch)
     |-- gpu01   2 x 25G data
     |-- svc01   2 x 25G data
     |-- svc02   2 x 25G data
     |-- svc03   2 x 25G data
  oob01  Cisco C1300-24T-4X (management switch)
     |-- gpu01 BMC   1G copper
     |-- svc01 BMC   1G copper
     |-- svc02 BMC   1G copper
     |-- svc03 BMC   1G copper
     |-- sw01 management port
```

In plain words:

1. Our rack connects to the lab's C9500X-28C8D with three links: two for data, one for management.
2. The two 100G data links come from sw01's 100G ports. Every server's data ports go to sw01's 25G ports.
3. The 10G management link comes from oob01. Every server's BMC port (its built-in remote management:
   power, screen, reinstall) goes to oob01.
4. Because management has its own link, remote management still works if sw01 or the data links go down.
5. Every optic is Cisco and listed in Cisco's compatibility matrix for the switch it goes in. We supply all
   optics and cords, both ends.

**Parts** ([08b](08b-quote-network-and-rack.md), items 4, 5, 6a-6e):

- **sw01 (item 4):** Cisco Nexus N93180YC-FX3: 48 x 1/10/25G SFP28 (servers) and 6 x 40/100G QSFP28
  (uplinks). Port-side exhaust: NXA-PAC-650W-PE power supplies, NXA-FAN-35CFM-PE fans. Room for gpu02 at
  100 users, and four 100G ports stay free.
- **Server cables (item 5):** 10 x Cisco SFP-H25G-CU3M, 3 m passive 25G DAC (8 used, 2 spare).
- **Data links (6a-6c):** 4 x Cisco QSFP-40/100-SRBD (one at each end of each link), OM4 multimode LC-LC
  cords: 3 x 8 m and 3 x 15 m, covering both data links and the management link, since the route is not
  measured yet.
- **Management (6d-6e):** 1 x Cisco CVR-QSFP-SFP10G adapter in the C9500X-28C8D, 2 x Cisco SFP-10G-SR-S
  (one in the adapter, one in oob01).
- sw01 bonds its two QSFP28 uplinks (Ethernet1/49-1/50) in one LACP port-channel.

**Optic compatibility (Cisco Optics-to-Device Compatibility Matrix, tmgmatrix.cisco.com, checked 2026-11-06):**

| Link | Part | C9500X-28C8D (IOS XE) | N93180YC-FX3 (NX-OS) |
|---|---|---|---|
| 100G data, multimode LC duplex | QSFP-40/100-SRBD | Listed from 17.7.1 | Listed from 9.3(7) |
| 25G server cables | SFP-H25G-CU3M | n/a | Listed |
| 10G management | SFP-10G-SR-S in CVR-QSFP-SFP10G | Listed from 17.7.1 ("For QSFP28 and QSFP-DD ports, QSA (CVR-QSFP-SFP10G) is required") | n/a |

The lab runs IOS XE 17.15.06, so the C9500X side is covered.

**Why not the Dell S5248F-ON.** Cisco lists no 100G multimode LC optic for the C9500X-28C8D that a Dell
switch supports, and Dell's site would not confirm a single-mode alternative on the S5248F-ON. A Cisco
switch at our end removes that cross-vendor guess.

**"Rated for 25G."** The engineer noted the N93180YC-FX3 is rated for 25G. That is true of its 48 server
ports. Its 6 uplink ports are 40/100G QSFP28, which is why Cisco lists 100G optics for it. In the lab's
own network those uplinks are probably taken, so a device plugged into their N93180YC-FX3 would only get
25G. Ours is our own switch, so its uplinks are ours.

**Small checks left:** the servers' 25G cards (Intel E810, Broadcom N225P) take Cisco passive DACs. Passive
DACs are standardized and these cards normally accept them; Thinkmate confirms in the quote. Rail fit at
29 in is asked in 08b, question 1.

**Not recommended:** plugging the GPU server straight into a lab switch port. The service nodes then
reach the GPU over the lab network, and the network team has to support our east-west traffic.

## 4. InfiniBand (BOM tab, cell B21)

Not needed. InfiniBand is for spreading training or one large model across many servers. This design
serves one model copy per GPU and does no multi-node training. 25GbE inside the rack is enough.
If multi-node fine-tuning ever becomes a requirement, revisit it then. The rack has room and power for it.

## 5. Checking switch capacity: steps for the network team

These are read-only commands. Ask the lab network team to run them (we should not have access to their
switches) and send back the output. `validate/net-test.sh` runs the matching tests from our side.

**On the C9500X-28C8D:**

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
| `show interfaces status` | Free ports and their speeds | 2 free 100G QSFP28 ports |
| `... include rate` (5-minute rate) on its 10G uplink | Current load at a busy time of day | Under 50% of 10 Gbps |
| `... include drops\|errors` | Congestion or bad optics | Output drops and CRC errors near 0 and not climbing |
| `show etherchannel summary` | After we connect: are our two 100G links bonded (200G total) or is one a standby? | Both members flagged `P` (bundled) |

**End-to-end test, after our rack is connected:**

1. From one analyst workstation, run `iperf3 -c <svc01-ip> -P 4 -t 30`. Expect close to the desk port
   speed (about 940 Mbps on a 1G port).
2. From two or three workstations in different parts of the lab at once, confirm each still gets close to
   its desk speed.
3. Inside the rack (`validate/net-test.sh`): node to node should reach about 23 Gbps per 25G link.
4. Load test: run `validate/llm-load-test.py --users 10`. Ten parallel users is the 50-user peak from the BOM.
   Time-to-first-token should stay under about 2 s.
