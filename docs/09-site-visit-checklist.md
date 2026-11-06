# 09. Site visit: look and ask

Bring: tape measure, flashlight, this page, a pen. **Ask before taking photos.** Many server rooms
need approval for cameras and phones.

## 1. What visit 1 found

| Item | Found |
|---|---|
| Rack model | Vertiv VR3300: 42U, 600 mm wide, 1200 mm deep (Vertiv spec) |
| Hole type | Square (cage nuts for anything without tool-less rails) |
| Vertical rails | Adjustable, currently 29 in apart front to rear |
| Rack PDUs | Already installed: Vertiv Geist, one on the left and one on the right. Each has circuits 1, 2, and 3. Mostly C13 outlets (smaller, slots vertical), plus one C19 per circuit (larger, slots horizontal): three C19 per PDU, six per rack. 208V. Not marked A or B. |
| Where power arrives | Through those PDU strips. No separate receptacles needed. |
| Ground | Green bonding wires on the rear split doors. No rack-to-ground-bar wire seen. |
| Doors | Perforated front and rear. No blanking panels installed. |
| Containment | Glass doors close off the rear of the racks, where the PDUs are: **hot aisle containment** |
| Floor | Raised floor, no perforated tiles. Cooling comes from the in-row CRV units. |
| Row layout | One CRV cooler in a rack position, then three racks to its left |
| Requested racks | Two racks next to ACE 15 |
| Access | Wide single-story front door |
| On site | No server lift, crash cart, or console. Room is empty except power, racks, and cooling. |

What this changed:

- No rack PDUs to buy for the lab.
- Blanking panels for both racks are in the quote.
- The rack console stays in the quote.
- The GPU server needs C14 or C20 power cords. Each PDU has only three C19 outlets, so the cord type is a vendor question.

## 2. Look (next visit)

### Each rack PDU

- [ ] The label on the PDU (side, top, or the input end). Model number, for example MN3E...: ________
- [ ] Input rating printed on the label, for example `208V 3PH 30A` or `24A`: ________
- [ ] How many C13 outlets per PDU: ____
- [ ] Display on the PDU showing amps? (Metered PDUs show current per circuit.)
- [ ] Where the PDU input cord goes: under the floor, or overhead. Any label on it, for example
      `RPP-2A CB 12,14,16`: ________

### Ground

- [ ] Under the raised floor, or at the bottom of the rack: a green or bare copper wire from the rack
      frame to the floor grid or a ground bar?

### Network

- [ ] Confirm our racks next to ACE 15 are in row 4
- [ ] Where the C9500X-28C8D sits above rows 2 and 3 (which rack, what height)
- [ ] The cable path from our racks to the C9500X-28C8D: overhead tray or under the raised floor? Pace it
      out: ____ m (we ordered 8 m and 15 m cords; the network team estimates about 12 ft between racks)
- [ ] Fiber in our racks: no patch panels (visit 1; the lab confirmed only the middle racks of rows 2 and 3 get one)
- [ ] If there is fiber anywhere nearby, note:
  - Connector: LC (small, in pairs) or MPO (wide, flat)
  - Cable color: aqua or violet means multimode, yellow means single-mode

## 3. Ask

### Facilities

1. Are the left and right PDUs in each rack fed from separate sources (A and B), for example different
   panels or UPS paths? If yes, which side is A?
2. What is each PDU's input rating? We need each PDU to carry about 5.1 kW by itself (one side down).
3. Who switches the PDU circuits off and on upstream, and what is the lockout/tagout process?
4. Is the rack frame bonded to the facility ground? The door straps are, but we didn't see the frame wire.
5. Please hold the two racks next to ACE 15 for us.

### Network team

Answered 2026-11-04 and 2026-11-05 (see [07](07-open-questions.md)): direct 100G to the C9500X-28C8D, we
supply the optics, IOS XE 17.15.06, a third port for management (2026-11-06). Still to confirm on site:

1. Which route should our cords take to the C9500X-28C8D, and who runs them?
2. Which three ports on the C9500X-28C8D are ours (two 100G data, one 10G management with our QSA adapter)?
3. VLAN IDs and subnets for data and management.

### Security (ISSM)

1. Will we have internet access during the initial build and debug? (Plan assumes no.)
2. What transfer media is approved, and does the lab provide it?
3. Is a laptop allowed in the room for the first switch setup over a console cable? If not, what does
   the lab use?
4. May the build workstation's rehearsal VM run on the unclassified side with internet access? (There is no staging server.)
5. May photos be taken of our racks for the as-built record?

### Lab IT

1. Does the lab's accreditation require a specific server OS (for example RHEL 9 with STIG)? If RHEL,
   who supplies the subscriptions and the package mirror? (Subscriptions are about $1,400 per server
   per year and are not in the BOM. Rocky Linux 9 is free.)
