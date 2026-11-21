# Lab network team: questions and answers

**Track:** Hardware (facility, network, rack, purchasing). Security decisions are in the [Cyber Security package](../../cyber/README.md).

**Status: closed for purchasing.** All three rounds are answered and the Nexus note is sent. The network
parts were ordered in [Network and rack quote](quote-network-and-rack.md). The final layout is in
[Network and switch capacity](../3-network-and-switch-capacity.md), section 3. Questions deferred until after the order (VLANs,
subnets, cable route, port settings) are in [Hardware open questions](../open-questions.md), N5, N6, and N14.

This page keeps what we asked, what the team answered, and what we did with it, round by round. Several
answers changed between rounds; the options and why we chose as we did are in the
[decision log](../decision-log.md) (D3 to D6).

## Round 1 (email, answered 2026-11-05)

**Our plan at the time:** two 100G links from our switch (then a Dell S5248F-ON) to two ports on the new
C9500X-28C8D, bonded with LACP. The lab had said on 2026-11-04 that we may connect directly at 100G and that
we supply the optics for both ends.

| # | We asked | They answered | What we did |
|---|---|---|---|
| 1 | Patch panels: where do they go, and do they reach our racks? Multimode or single-mode, MPO-12 or LC, which MPO polarity? | Only the middle rack of row 2 and of row 3 gets one, for fiber back to the main building. Our switch most likely connects straight to the C9500X-28C8D. Fiber: single-mode, LC. | Planned single-mode LC optics. Later found the single-mode answer described the panels, not our link (round 3). |
| 2 | Must the C9500X-28C8D optics be Cisco-branded? Which IOS XE version? | IOS XE 17.15.06, the second-latest Cisco MD release (it will move up over time). Brand not answered. | Chose Cisco-branded optics. Check optics against 17.15 and the next MD train. |
| 3 | Which two racks in row 2 or 3 are ours? | Not answered. | Kept the two racks next to ACE 15 (row 4). |
| 4 | Where does the management switch (C1300-24T-4X) uplink go, fiber or copper? | Not answered. | Planned to uplink oob01 through sw01. Changed in round 3. |

## Round 2 (email, answered in a meeting 2026-11-06)

**We sent:** our layout for checking (2 x 100G single-mode to the C9500X-28C8D, management on its own VLAN
over the same links, 20 m cords), and asked for the cable route, our two ports, and VLAN IDs and subnets.

**They answered:**

- They don't know which rack "ACE 15" is.
- For data, we will most likely **not** connect directly to the C9500X. It is the core/aggregation layer and
  the link to the C9500X in the other building. The access layer is **Cisco N93180YC-FX3** switches.

**What we did:** treated the N93180YC-FX3 as our connection point, with 2 x 25G as the fallback, and asked
round 3. (This answer was withdrawn in round 3.)

## Round 3 (email, answered 2026-11-06)

**We asked**, to decide what we buy:

| # | We asked | They answered |
|---|---|---|
| 1 | What do you call our racks, which RHINO are they in, which N93180YC-FX3 serves them, and how far is it? | Connect directly to the C9500X. The N93180YC-FX3 answer was a mix-up: the engineer had taken our Dell switch for a server. About 12 ft between racks; 6-8 m should be enough. |
| 2 | May our own switch connect to yours, or should our servers plug straight into your switch? | Our switch, direct to the C9500X. |
| 3 | 2 x 100G QSFP28, or 2 x 25G SFP28? | 2 x 100G on the C9500X. A third port for management was confirmed later the same day. |
| 4 | Direct cord or patch panel? Single-mode or multimode, LC? Cisco optics required? Which version? | Multimode, LC. Second-latest Cisco MD release, currently 17.15.06. |
| 5 | May management traffic share the data links on its own VLAN, or should it be separate? Copper or fiber? | Ideally separate, so it does not depend on the data side. He recommends connecting the C1300 directly to the C9500X, which needs a 10G SFP in a QSFP port. |

**What we did** ([Network and switch capacity](../3-network-and-switch-capacity.md), section 3):

- Our switch became a Cisco Nexus N93180YC-FX3, so the 100G links use QSFP-40/100-SRBD (multimode LC, as he
  said) at both ends, listed for both switches in Cisco's matrix. A Dell switch had no confirmed match.
- Cords in 8 m and 15 m, because "about 12 ft" is an estimate.
- Management on its own link, with the QSA adapter (CVR-QSFP-SFP10G), which Cisco's matrix supports for
  SFP-10G-SR-S on this switch.

## Nexus note (sent)

He had mentioned the N93180YC-FX3 is rated for 25G. We sent this note so the team knew our switch had changed
(open questions, N15):

> **Subject:** RE: SI racks: our switch will be an N93180YC-FX3
>
> Thanks, that settles the connection. One change on our side: to keep every optic on Cisco's compatibility
> list, our top-of-rack switch will be a Cisco Nexus N93180YC-FX3 instead of the Dell.
>
> Agreed that its 48 server ports are 25G. It also has six 40/100G QSFP28 ports, and we will use two of them
> for the 2 x 100G links to your C9500X-28C8D, with Cisco QSFP-40/100-SRBD at both ends (multimode, LC, as you
> said; Cisco lists it for both switches). The management link stays as discussed: our C1300 to a third
> C9500X port with a CVR-QSFP-SFP10G adapter and SFP-10G-SR-S, which we supply.
>
> Is your team comfortable with us running an N93180YC-FX3 as our top-of-rack switch?

**Answer:** not recorded yet. Record it in the hardware open questions, N15.
