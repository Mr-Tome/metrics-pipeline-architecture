# 01. Facility requirements (send to the lab)

This is the answer to the lab's request in the README: power, cooling, connectors, and anything non-standard.
It covers the 20-user build that fits the $250,000 budget, and it is sized so the rack does not need new
circuits when it grows to 100 users.

Status of each number:

- **Firm**: from the BOM or a vendor spec.
- **Confirm**: a planning figure. It must be checked against the final vendor quote before the facility does any work.

## 1. Summary for facilities

| Item | Lab (air-gapped) | Staging (unclassified) |
|---|---|---|
| Racks | 1 x 42U (use one of the existing Vertiv racks). Please hold the next rack in the same row for growth. | 1 x 42U, or a half rack |
| Power circuits | 2 circuits (A and B), each 208V 3-phase WYE, 30A, 60 Hz | Same as lab (2 circuits) so PDUs and spares are interchangeable |
| Receptacle | NEMA L21-30R, one per circuit, within 10 ft of the rack top or bottom | NEMA L21-30R x 2 |
| A and B source | From different panels or UPS paths if available | Same panel is acceptable |
| Peak draw, 20 users | about 3.6 kW | about 1.5 kW |
| Peak draw, 100 users (future) | about 8.3 kW | about 1.5 kW |
| Heat load, 20 users | about 12,200 BTU/hr (about 1.0 ton) | about 5,100 BTU/hr |
| Heat load, 100 users | about 28,300 BTU/hr (about 2.4 tons) | about 5,100 BTU/hr |
| Airflow | Front to back. Cold aisle intake, hot aisle exhaust. | Front to back |
| Intake air | 18 to 27 C (64.4 to 80.6 F), the ASHRAE recommended range | Same |
| Weight | under 200 kg (440 lb) of equipment in the rack | under 80 kg |
| Network | See section 5 | Unclassified LAN drop, 10G preferred |

Nothing in this build is non-standard: no liquid cooling, no 400V or 480V, no special connectors. The only
item to watch is the GPU server power cord type (section 3).

## 2. Why these circuits

The lab asked us not to question facility capacity. Two things set our ask:

1. **Redundancy.** Every device has two or more power supplies. Half go to PDU-A, half to PDU-B. If one
   feed is lost, the other carries the whole rack. So **each circuit must carry the full rack load by itself.**
2. **No re-work at 100 users.** One 208V 3-phase 30A circuit gives about 8.6 kW of usable power
   (30A x 208V x 1.732 x 0.8 continuous-load derating). That covers the 100-user rack (8.3 kW) on one feed.
   A single-phase L6-30 circuit (about 5.0 kW usable) would cover the 20-user build but would need to be
   replaced at 100 users. We would rather ask once.

## 3. Equipment power detail

From the BOM (`Assumptions` tab, section 4). Maximum draw, not typical draw. Typical inference load
runs well below this.

| Tag | Device | Qty (20 users) | Max W each | Input | Power cord (device end to PDU end) | Status |
|---|---|---|---|---|---|---|
| gpu01 | 2U GPU server, 2 x RTX PRO 6000 Server Edition | 1 | 2,100 (900 platform + 2 x 600 GPU) | 200-240V AC, 50/60 Hz, redundant PSUs | C20 to C19, or C14 to C13. Depends on PSU wattage. | **Confirm** with Thinkmate |
| svc01-03 | 1U service node | 3 | 400 | 100-240V AC, 2 PSUs | C14 to C13 | Confirm |
| sw01 | Dell S5248F-ON 25G switch | 1 | 250 | 100-240V AC, 2 PSUs | C14 to C13 | Firm (BOM) |
| oob01 | 1G management switch | 1 | 30 | 100-240V AC | C14 to C13 | Confirm |
| | **Lab total** | | **about 3,580 W** | | | |
| stg01 | Staging GPU server, 1 GPU | 1 | 1,500 | 200-240V AC | as gpu01 | Confirm |

The BOM total of 3,550 W lab and 1,500 W staging leaves out the small management switch. That is the
only difference.

**Why the PDU is "combination outlet":** Vertiv Geist rack PDUs come with combination C13/C19 outlets.
Each outlet takes either cord type. That way the PDU order does not have to wait on the final GPU
server PSU choice.

**GPU power cap.** NVIDIA rates the RTX PRO 6000 Server Edition at 600 W, and the limit can be set
down to 400 W. If power ever becomes tight, we can cap the GPUs with `nvidia-smi -pl 400` and lose
some throughput instead of tripping a breaker.

## 4. Cooling

- The equipment is air cooled, front to back. The GPUs are passive cards that rely on the server
  chassis fans.
- The model number we were given, **CR035RA1A7X...**, is a **Vertiv Liebert CRV in-row cooling unit**
  (35 kW, air cooled). It is not aisle containment. It is a cooler that sits in the row between racks.
  A 35 kW unit covers this rack many times over. See [07-open-questions.md](07-open-questions.md), item F1.
- Our asks:
  - Put the lab rack in a row served by a CRV and inside the containment.
  - Server fronts face the cold aisle.
  - We will install blanking panels in every empty U. Containment does not work without them.
- Approximate airflow: about 560 CFM at 20 users, about 1,300 CFM at 100 users.
  This uses CFM = 3.16 x W / delta-T(F), with an assumed 20 F rise.

## 5. Network ports needed from the lab network team

See [03-network-and-switch-capacity.md](03-network-and-switch-capacity.md) for the reasoning.

| Need | Preferred | Fallback |
|---|---|---|
| Uplink from our lab switch to the core | 2 free 100G QSFP28 ports on the C9500X core, in an LACP port-channel | 2 free 10G SFP+ ports on the C9300 access switches (network module), LACP |
| Fiber between the core and our rack | 1 x MPO-12 OM4 pair (100G-SR4), or 2 x LC single-mode pairs (100G-LR4 / CWDM4). Whichever the lab plant already uses. | LC OM4 multimode pairs for 10G-SR |
| IP space | One /27 for servers, one /28 for BMC (out-of-band) | |
| Services | DNS, NTP, and the lab's internal CA certificate (for HTTPS on the chat page) | |
| Management | Where the out-of-band switch uplink should land | |

## 6. Space and handling

- **Rack depth:** 2U GPU servers need a deep rack (servers of this class are 30 to 35 in deep, plus
  cable room). Vertiv VR racks are made 1100 and 1200 mm deep, which works. We need the rack model
  number to confirm (it is on a label on the rear door or the frame and starts with VR).
- **Delivery:** The GPU server ships at about 40 to 50 kg boxed. Two-person lift. A server lift is
  preferred above U20, but our layout keeps the heavy gear at U1 to U7.
- **Dock to rack:** Clear path for a pallet jack. Note any elevator or door limits.
