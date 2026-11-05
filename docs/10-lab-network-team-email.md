# 10. Emails to the lab network team

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

## Follow-up email

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
