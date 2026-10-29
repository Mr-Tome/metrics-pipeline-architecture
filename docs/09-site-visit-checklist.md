# 09. Site visit: look and ask

Bring: tape measure, flashlight, this page, a pen. **Ask before taking photos.** Many server rooms
need approval for cameras and phones.

## 1. Look

### The rack you will get

- [ ] Model label (rear door or frame, starts with VR, for example VR3300): ________
- [ ] Height in U (numbers are printed on the rails): ____ U
- [ ] Width: 600 mm (24") or 800 mm (31")
- [ ] **Hole type on the mounting rails:**
  - Square holes: needs cage nuts
  - Round threaded holes: screws go straight in
  - Round unthreaded holes
- [ ] **Depth between the front and rear mounting rails** (measure the outside faces): ____ in. Can the rails slide?
- [ ] Outside depth of the rack: ____ mm (1100 or 1200 expected)
- [ ] Already in the rack? These are the long vertical strips at the rear with outlets.
  - Rack PDUs: ____ (count)
  - Model label: ________
  - Input plug: ________
  - Outlets: C13 (small) ____, C19 (larger) ____
  - Marked A and B, or colored?
- [ ] Ground wire (green) from the rack to a ground bar?
- [ ] Doors perforated front and rear? Any blanking panels already installed?

### Power at the rack

- [ ] Where power arrives:
  - Under the floor (receptacles or cords)
  - Overhead cord drops ("whips")
  - Overhead busway (a metal track with plug-in boxes)
- [ ] The receptacle face. Write down the printed rating, or sketch the face:
  - NEMA L21-30R: twist-lock with 5 slots in a circle. This is what we asked for.
  - NEMA L6-30R: twist-lock with 3 slots
  - IEC 60309 pin-and-sleeve: round, blue or red
- [ ] **The label on each receptacle or cord drop**, for example `PDU-2A / panel 3 / CB 12,14,16`.
  The labels are how you will tell feed A from feed B. Copy every one: ________
- [ ] The large cabinets with transformers at the head of each aisle. These are floor power
  distribution units, not rack PDUs. Read the nameplate:
  - Model: ________
  - Output voltage, for example 208Y/120 V: ________
  - Marked A or B?
  - Is there one per row, or two (one A side, one B side)?

### Cooling and containment

- [ ] Which aisle do the glass doors close off?
  - Fronts of the racks face inside the glass: cold aisle containment. Server fronts face in.
  - Backs of the racks face inside the glass: hot aisle containment. Server backs face in.
- [ ] Where the CRV in-row coolers sit (the CR035RA units), and which racks are next to them
- [ ] Raised floor with perforated tiles, or concrete slab?

### Network

- [ ] Where the C9300-48S for this building sits, and how far it is from our rack
- [ ] On that switch: is there an uplink module on the right side with 8 SFP+ ports (C9300-NM-8X)?
  Are any of those ports empty?
- [ ] Fiber in our rack or row: patch panel present?
  - Connector: LC (small, in pairs) or MPO (wide, flat)
  - Cable color: aqua or violet means multimode, yellow means single-mode
- [ ] A copper Ethernet drop for the management switch?

### Getting equipment in

- [ ] Dock, elevator, and door sizes from the dock to the rack. Can a pallet jack make it?
- [ ] Is cardboard allowed in the room? Where do you unbox?
- [ ] Server lift available? Crash cart or console available?

## 2. Ask

### Facilities

1. Which rack can we have? We want one rack in a contained row, near a CRV unit. Please hold the rack
   next to it for growth.
2. Do the racks already have rack PDUs? If yes: model, input plug, outlet types, and is each rack fed
   from A and B?
3. Can you provide 2 x 208V 3-phase 30A circuits on NEMA L21-30R, one from source A and one from source B?
   If your standard is different, what is it? We will match our PDU plug to it.
4. Who switches the breakers on and off, and what is the lockout/tagout process? Will you label our
   two circuits A and B at the panel and at the receptacle?
5. Who bonds the rack to the ground bar?
6. Cooling: is containment hot aisle or cold aisle?

### Network team

1. Can our switch connect directly to the C9500X core, or must it go through the C9300-48S in this building?
2. Does that C9300-48S have free 10G SFP+ ports (C9300-NM-8X module)? Could you send `show inventory` and
   `show interfaces status` for it?
3. What fiber runs between that switch and our rack: multimode or single-mode, LC or MPO? Do you supply
   the optics on your side, or should we?
4. Where should our management switch connect?

### Security (ISSM)

1. Will we have internet access during the initial build and debug? (Plan assumes no.)
2. What transfer media is approved, and does the lab provide it?
3. Is a laptop allowed in the room for the first switch setup over a console cable? If not, what does
   the lab use?
4. Where may the staging server live, and may it have internet access?
5. May photos be taken of our rack for the as-built record?

### Lab IT

1. Does the lab's accreditation require a specific server OS (for example RHEL 9 with STIG)? If RHEL,
   who supplies the subscriptions and the package mirror?
