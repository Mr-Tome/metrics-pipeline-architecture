# 10. Emails to the lab network team

**Track:** Hardware (facility, network, rack, purchasing). Security decisions are in the [Cyber Security package](../cyber/README.md).

**Current: answered 2026-11-06 (see the last section). Nothing more is needed for purchasing.**
The earlier emails are kept as a record.

Copy everything below the line into the email. These are the questions that block the network order
([08b](08b-quote-network-and-rack.md), "Answer these first"). Record the answers in
[07](07-open-questions.md) under N3, N10, F6, and N7.

---

**Subject:** SI rack: connection to the new C9500X-28C8D, four questions before we order optics

Hi,

Thanks for confirming that our rack switch can connect to the new C9500X-28C8D above rows 2 and 3
at 100G, and that we supply the optics for both ends. Before we order the optics and cables, we need
four answers from you:

1. **Patch panels.** Where will the new patch panels go (in each rack, at the top of the rack, or
   overhead), and will they reach our racks? What fiber runs from them to the C9500X-28C8D:
   - OM4 multimode or single-mode?
   - MPO-12 or LC connectors?
   - If MPO, which polarity (Type A, B, or C)?

2. **Optics.** Do the optics in the C9500X-28C8D have to be Cisco-branded, or do you accept
   Cisco-compatible third-party optics? Which IOS-XE version does the switch run? We will check our
   optics against the Cisco compatibility matrix for that version.

3. **Our racks.** Which two adjacent racks in row 2 or row 3 are ours? Facilities confirmed those
   racks match what we planned for (power, cooling, rack model), so the only open point is which ones.

4. **Management network.** Our rack has a small 1G management switch (Cisco C1300-24T-4X) for the
   servers' remote management (BMC) ports. Where should its uplink go: to the C9500X-28C8D, or to a
   separate lab management switch? Fiber or copper? It has 1G copper ports and 10G SFP+ ports.

For reference, our plan is two 100G links from our switch (Dell S5248F-ON, QSFP28 ports) to two ports
on the C9500X-28C8D, bonded with LACP. We need two free 100G QSFP28 ports on your side.

Thanks,

---

## Answers received 2026-11-05

- Patch panels: only in the middle rack of row 2 and of row 3, for the fiber back to the main building.
  Our switch most likely connects straight to the C9500X-28C8D.
- Fiber: single-mode. Connector: LC.
- IOS XE: the second-latest Cisco MD release, currently 17.15.06.
- Not answered, decided by us 2026-11-05: Cisco-branded optics; we keep the racks next to ACE 15 (row 4)
  with 20 m cords; the management switch uplinks through our switch (option 1 in
  [03](03-network-and-switch-capacity.md), section 3).

Recorded in [07](07-open-questions.md) (N3, N7, N10) and [08b](08b-quote-network-and-rack.md).

## Follow-up email (round 2, superseded)

Answered in a meeting on 2026-11-06 instead; see the next section.

Copy everything below the line into the reply.

---

**Subject:** RE: SI rack: connection to the new C9500X-28C8D

Hi,

Thanks, that settles the fiber. Here is how we plan to connect, so you can check it before we order:

```
LAB
  C9500X-28C8D (lab core, above rows 2 and 3)
     |  2 x 100G, single-mode LC fiber, 20 m each, bonded (LACP)
     |  carries two VLANs: data, and management
OUR RACK (next to ACE 15, row 4)
  sw01  Dell S5248F-ON (fast switch)
     |-- gpu01   2 x 25G data
     |-- svc01   2 x 25G data
     |-- svc02   2 x 25G data
     |-- svc03   2 x 25G data
     |-- oob01   1 x 10G (management switch uplink)
           |
         oob01  Cisco C1300-24T-4X (management switch)
           |-- gpu01 BMC   1G copper
           |-- svc01 BMC   1G copper
           |-- svc02 BMC   1G copper
           |-- svc03 BMC   1G copper
           |-- sw01 management port
```

In plain words:

1. Our rack connects to the lab in one place: two 100G fibers from sw01 to the C9500X-28C8D.
2. Inside the rack, every server's data ports go to sw01.
3. Every server's BMC port (its built-in remote management: power, screen, reinstall) goes to oob01,
   and oob01 plugs into sw01.
4. Data traffic and management traffic share the two 100G links, kept apart as two VLANs.
5. What we need from the lab: 2 x 100G ports on the C9500X-28C8D, two VLANs (data and management), and
   an IP subnet for each.

Parts we will supply: 2 x Cisco QSFP-100G-CWDM4-S for your C9500X-28C8D (we will check them against the
compatibility matrix for 17.15), the matching Dell optics for our switch, and 20 m LC-LC single-mode cords.
Our racks are the two next to ACE 15 in row 4.

Three questions:

1. **Cable route.** Which rack is the C9500X-28C8D in, and which route should our 20 m cords take from row
   4 (overhead tray or under the floor)? Do we run the cords, or does your team?
2. **Ports.** Which two 100G ports on the C9500X-28C8D will be ours?
3. **VLANs.** Is it OK to carry both our data VLAN and our management VLAN over the two 100G links? If so,
   please send the VLAN IDs and subnets you want us to use (one /27 for servers, one /28 for management).

Thanks,

## Answers received 2026-11-06 (meeting with the network team)

- They don't know which rack "ACE 15" is.
- For data connectivity in the RHINOs we will most likely **not** connect directly to the C9500X.
- Access layer: **Cisco N93180YC-FX3** switches. The C9500X is the core/aggregation layer and the link
  back to the C9500X in the other building.
- This replaces the 2026-11-04 answer (direct 100G to the C9500X-28C8D). The 2026-11-05 answer
  (single-mode LC) was about the patch panels to the main building, so the fiber to the N93180YC-FX3 is
  unknown.
- Planning facts (Cisco datasheet): the N93180YC-FX3 has 48 x 1/10/25G SFP28 and 6 x 40/100G QSFP28
  ports and runs NX-OS. The QSFP28 ports are often its uplinks, so 2 x 25G is our fallback.

Recorded in [07](07-open-questions.md) (F6, N2, N11-N14).

## Round 3 email: connecting to the N93180YC-FX3

Copy everything below the line into the email. It asks only what changes the network parts
([08b](08b-quote-network-and-rack.md), items 4 and 6a-6g). Configuration questions are deferred (07, N14).

---

**Subject:** SI racks: connecting to your N93180YC-FX3, 5 questions before we order

Hi,

Thanks for bringing the network team in. We now understand that the C9500X is your core/aggregation
layer and that our racks connect through your N93180YC-FX3 access switches. So we can order the right
parts in one go, here is what we have, what we propose, and the five questions that decide what we buy.
A short answer under each number is plenty.

**What we have**

Two racks in the server room, next to the rack labeled "ACE 15" (we believe in row 4). We are building
rack 1 now; rack 2 is held for growth. Rack 1 holds:

- 4 servers (1 GPU server, 3 service nodes). Each has 2 x 25G data ports and 1 x 1G copper management
  (BMC) port.
- Our own switch, sw01 (Dell S5248F-ON: 48 x 25G SFP28, 4 x 100G QSFP28). It connects the servers to each
  other and to you.
- A small management switch, oob01 (Cisco C1300-24T-4X), for the BMC ports.

**What we propose**

```
YOUR NETWORK
  C9500X  (core / aggregation, link to the other building)
     |  your existing links
  N93180YC-FX3  (access switch for our racks: which one? Q1)
     |  2 x 100G QSFP28 (preferred) or 2 x 25G SFP28, bonded (LACP)
     |  carries two VLANs: data, and management
OUR RACK 1 (next to ACE 15: what do you call it? Q1)
  sw01  Dell S5248F-ON (our switch)
     |-- gpu01   2 x 25G data
     |-- svc01   2 x 25G data
     |-- svc02   2 x 25G data
     |-- svc03   2 x 25G data
     |-- oob01   1 x 10G (management switch uplink)
           |
         oob01  Cisco C1300-24T-4X (management switch)
           |-- gpu01 BMC   1G copper
           |-- svc01 BMC   1G copper
           |-- svc02 BMC   1G copper
           |-- svc03 BMC   1G copper
           |-- sw01 management port
```

In plain words:

1. Our rack connects to your network in one place: two links from sw01 to your N93180YC-FX3.
2. We would like those links to be 100G (the N93180YC-FX3 has 6 x 100G QSFP28 ports). If those ports are
   reserved for your uplinks, 2 x 25G on its SFP28 ports is enough for us: user traffic is under
   10 Mbps at 50 users.
3. Server-to-server traffic stays inside our rack on sw01. It never crosses your network.
4. Management (BMC) traffic rides the same two links on its own VLAN.
5. We supply the optics and cords for both ends.

**Questions (only what decides what we buy)**

1. **Location.** What name or number do you use for our two racks (the two next to the rack labeled
   "ACE 15"), and which RHINO are they in? Which N93180YC-FX3 serves them, and roughly how far is it from
   our racks? (This sets the cord length.)
2. **Our switch or yours.** May we connect our own switch (sw01) to your N93180YC-FX3 as drawn above? Or
   do you want our servers plugged straight into your switch? If so, we would need 8 x 25G SFP28 ports for
   data from you, and we would not buy sw01.
3. **Port speed.** Can we have 2 x 100G QSFP28 ports on the N93180YC-FX3? If not, 2 x 25G SFP28 ports?
   (This picks our optics: 100G QSFP28 or 25G SFP28.)
4. **Fiber and optics.** Is it a direct cord from our rack to your switch, or through a patch panel?
   Single-mode or multimode? LC connectors? Must the optics in your switch be Cisco-branded, and which
   NX-OS version does it run? (We check our optics against Cisco's compatibility matrix for it.)
5. **Management (copper).** Our BMC (remote management) ports are 1G RJ45 copper. Is it OK for that
   management traffic to reach you over the same two links on its own VLAN? If you want it separate,
   where should our management switch plug in, and is that 1G copper or 10G fiber? Note: the GPU server
   also has 2 x 10G RJ45 copper ports on the motherboard, and each service node has 1 x 1G RJ45. We
   leave those unplugged; all data goes over the 25G SFP28 cards.

VLANs, addressing, bonding, and port settings can wait until after the order. We will send those
separately.

Thanks,

## Answers received 2026-11-06 (round 3)

The engineer corrected the earlier answer: he had taken the Dell for a server.

1. Connect directly to the C9500X. (The N93180YC-FX3 answer was a mix-up.)
2. 2 x 100G on the C9500X. A third port for management was confirmed later the same day.
3. 6-8 m should be enough: about 12 ft between racks.
4. Multimode, LC. Version: second-latest Cisco MD release, currently 17.15.06.
5. Management ideally separate, so it does not depend on the data side. He recommends connecting the C1300
   directly to the C9500X, which needs a 10G SFP in a QSFP port.

What we did with it ([03](03-network-and-switch-capacity.md), section 3):

- Our switch is now a Cisco Nexus N93180YC-FX3, so the 100G links use QSFP-40/100-SRBD (multimode LC, as he
  said) at both ends, listed for both switches in Cisco's matrix. (A Dell switch had no confirmed match.)
- Cords in 8 m and 15 m, because "about 12 ft" is an estimate.
- Management on its own link, with the QSA adapter (CVR-QSFP-SFP10G), which Cisco's matrix supports for
  SFP-10G-SR-S on this switch.

The final layout:

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

## Short note to send: our switch is a Nexus

He mentioned the N93180YC-FX3 is rated for 25G. Copy below the line.

---

**Subject:** RE: SI racks: our switch will be an N93180YC-FX3

Hi,

Thanks, that settles the connection. One change on our side: to keep every optic on Cisco's compatibility
list, our top-of-rack switch will be a Cisco Nexus N93180YC-FX3 instead of the Dell.

Agreed that its 48 server ports are 25G. It also has six 40/100G QSFP28 ports, and we will use two of them
for the 2 x 100G links to your C9500X-28C8D, with Cisco QSFP-40/100-SRBD at both ends (multimode, LC, as you
said; Cisco lists it for both switches). The management link stays as discussed: our C1300 to a third
C9500X port with a CVR-QSFP-SFP10G adapter and SFP-10G-SR-S, which we supply.

Is your team comfortable with us running an N93180YC-FX3 as our top-of-rack switch?

Thanks,
