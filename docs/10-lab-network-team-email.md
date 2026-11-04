# 10. Email to the lab network team (P1-P4)

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
