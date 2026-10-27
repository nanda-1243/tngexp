# Failure review (Rev B and Rev C)

This review asked how hand-lever badge and magnet presses fail in use, then checked the MagPress design at the loads a person can put on the grip: 200 N for a normal push, 500 N for someone leaning on it. Rev B came out of the first pass. Rev C added the problems found while designing the size kits (rows 8, 20, 21 and 22). The numbers come from [`calc/engineering_calcs.py`](../../calc/engineering_calcs.py), and its output is in [`calc/results.txt`](../../calc/results.txt).

## What goes wrong on presses already on the market

These come from user guides, vendor troubleshooting pages and user reports. Sources are in [sources.md](sources.md).

- **Jams from double shells or mis-loaded parts** are the most common stoppage. The usual cure is a gentle partial stroke on the crimp die, not force on the handle (American Button Machines).
- **Film slips and white paper shows at the edge** with laser prints (toner wax), heavy paper or card, or a worn crimp lead-in (ABM; Etsy forum).
- **Cheap die sets crack or warp after a few hundred uses**, and some presses arrive with the dies out of alignment (MN Magnets guide; vendor-written, so treat it as a viewpoint).
- **Over-oiling** soils the finished pieces (Nebraska Library Commission maintenance guide).
- **Handles that thread into soft fittings strip**, and one library review reports a mechanism that sticks in the down position. Both come from search summaries and were not confirmed at a primary source.

## What the Rev A stress check found

- The M12 stud joining handle bar and hub reached 465 MPa at 200 N and 1,161 MPa at 500 N, against C45 yield of about 340 MPa.
- The return springs gave 0.83 N·m at the closed position. Reopening needs about 3.5 N·m plus friction, so the handle would stay down.
- Pivot pin O (Ø12) reached 542 MPa at 8 kN and 1,085 MPa at a 16 kN overload.
- Nothing locked the die table on station, so a table 2 mm off station would land the upper frame on the lower frame's edge.
- The 12 mm base deflected 0.51 mm at 16 kN. The dies had 1.75 mm walls next to counterbores in hardened steel.

## FMEA

Sev. is how bad the effect is. Before is how likely it was before the fix (Rev A, or Rev B for rows 8, 20 and 21). H high, M medium, L low.

| # | Failure mode | Cause | Effect | Sev. | Before | Fix (Rev B / C) | Proof |
|---|---|---|---|---|---|---|---|
| 1 | Handle joint bends, strips or snaps | Bar screwed into the hub on an M12 stud; thread stress 465 MPa at 200 N | Handle breaks; operator falls forward | H | H | One-piece C45 lever MP-113: 14 MPa at 200 N, 36 MPa at 500 N | 16 kN proof load, no set |
| 2 | Handle stays down, ram sticks | Return springs too weak at the closed position (0.8 N·m against ≈ 3.5 N·m plus friction) | Operator pulls the ram up through the dies by hand | M | H | Return springs Ø3.5 wire, OD 31.5, free 128: 80 N open, 245 N closed, 4.5 N·m; ≥ 30% margin at every angle | Handle-return test, 20 of 20 |
| 3 | Pivot pin O bends | Ø12 pin at 542 MPa (8 kN), > 1,000 MPa at 16 kN | Handle play, short ram travel, uneven crimp | H | M | Ø16 g6 hardened pin: 229 MPa at 8 kN, 458 MPa at 16 kN | Stroke 38.9 ±0.3 after 10,000 |
| 4 | Pins and bores wear | Greased steel on steel; peak pin load near lockup; grease collects shell chips | Play, noise, toggle drifts toward dead centre | M | H | PTFE-composite bushings at O, A and B, run dry; bushings are the wear part | ≤ 1 mm play at the grip |
| 5 | Dies crash off station | Table not fully home; ball detent only | Chipped frames, crushed shell | H | M | Station pilot MP-120 enters at 20 mm of travel, 6 mm before the dies meet, and stops the stroke if the table is off station | 3 mm off-station test |
| 6 | Die corner cracks | D2's low toughness; EDM recast left on forming edges; thin walls | Die set scrapped; sharp fragments | H | M | A2 (about twice as tough), 2 skim cuts + re-temper, corner radii; kit-ring walls ≥ 7.7 mm, carrier walls ≥ 3.5 mm | Dye-penetrant check at 1,000 strokes |
| 7 | Tin pick-up (galling) on frames | Tinplate rubbing in the grip bore and crimp lead-in | Scratched shells, rising force, torn film | M | M | Lapped Ra 0.2 + thin dense chrome; PVD TiCN / TiAlN on high-temper steel for volume | Inspect at 25,000 strokes |
| 8 | Die springs break or sag | Rev B: red springs worked to 37.5%, past the heavy-duty maximum of about 30% | Rings stop returning; pickup or crimp fails | M | H | Rev C: universal springs, green 6–31% and blue 19–36%, within their life limits; light lower springs so the rings drop first | Stroke counter; free-length check at 250,000 |
| 9 | Shell drops out of the upper ring | Friction grip only; bore wears open | Double shell in die B → jam | M | H | 4 nylon-tip plungers, 0.6 × 20° lead-in, lapped bore | 50 fast table slides, no drops |
| 10 | Jam in die B | Two shells, or a dropped shell | Press stuck; forcing it damages dies | H | M | Fixes 5 and 9, plus the un-jam procedure below | Operator training |
| 11 | Film slips, white edge, wrinkles | Laser toner wax; paper too heavy | Rejects | L | H | 90–120 g/m² paper; inkjet, or a 3 mm white border for laser; silicone on die B's lead-in | 20-piece quality test |
| 12 | Ram binds on the columns | Bores out of line; uneven nut torque | Heavy handle, bushing wear | M | M | One datum and program for base, crown and ram; torque sequence | Ram falls under its own weight |
| 13 | Column nuts or cheek screws loosen | A shock load every stroke | Crown shifts; toggle out of line | H | L | Nord-Lock washers, set torques, threadlocker | Torque check at service |
| 14 | Base flexes, press walks | 12 mm base; feet only | Misalignment, press slides on the bench | M | M | 15 mm S355 (0.26 mm at 16 kN); rubber pads; six bench-mounting holes | Dial indicator under load |
| 15 | Toggle locks over | Fixed buffer worn or missing | Passes dead centre; force spike | H | L | Adjustable steel stop + urethane cap, set at 3° (8° before dead centre) | Check the setting at service |
| 16 | Overload from a lean or a pipe on the handle | 500 N at the grip gives 15.6 kN | Frame or pins yield | H | M | 16 kN design load on every frame and drive part | 16 kN proof load |
| 17 | Damage in shipping | Dies and handle loose in the box | Dies misaligned or cracked on arrival | M | M | Ship with dies boxed separately, handle strapped down, table taped | Alignment check on arrival |
| 18 | Table sticks short of station | Shell chips and dust on the slide | Off-station stroke | L | M | QPQ slide surface; pilot catches it; wipe each shift | Daily wipe |
| 19 | Oil marks on magnets | Over-oiling the dies and columns | Soiled product | L | M | Dry bushings; no oil on dies; light oil on rails only | Maintenance schedule |
| 20 | Shell edge not rolled under; back falls out | Flat crimp pedestal (Rev A/B) gave the edge nothing to turn on | Loose backs, returns | H | H | Rev C crimp anvil MP-208 with a R1.0 roll channel; the crimp ring is on its stop and guides the edge rigidly | Pull and twist test, 20 per size |
| 21 | Wrong ring in a station | Kit rings share one outside size | Crashed or scrapped kit | M | M | Key pins in each carrier, matching slots in its rings; U / A / B laser-marked; coloured bands | Try every wrong ring: none seats |
| 22 | Upper and lower rings out of line | Loose ring fit in a carrier pocket | Upper ring hits a lower ring edge | M | L | Pockets +0.01/0, rings −0.01/−0.02; the plug guides the upper ring; the pilot sets the table | Marker-blue contact check |

## Rev A against Rev B / C, by calculation

| Check | Load | Rev A | Rev B / C | Limit or target |
|---|---|---|---|---|
| Handle joint bending | 200 N / 500 N at the grip | 465 / 1,161 MPa | 14 / 36 MPa | C45 yield ≈ 340 MPa |
| Force at die, 200 N push | End of stroke | 5.6 kN | 6.2 kN | Largest set needs ≈ 4.7 kN |
| Hand force for the largest set | 4.7 kN at die | 166 N | 150 N | Lower is easier |
| Pin O bending | 8 / 16 kN | 542 / 1,084 MPa | 229 / 458 MPa | Hardened 100Cr6, keep under ≈ 800 MPa |
| Pins A and B bending | 16 kN | 425 MPa | 425 MPa | Unchanged, OK |
| Crown bending | 8 / 16 kN | 96 / 192 MPa | 96 / 192 MPa | C45 normalised yield ≈ 340 MPa; Rev B states it at 16 kN |
| Base deflection | 5 / 16 kN | 0.16 / 0.51 mm | 0.08 / 0.26 mm | Under 0.3 mm at overload |
| Return-spring torque, closed | Needs ≈ 3.5 N·m (lever and ram weight) + friction | 0.83 N·m | 4.51 N·m | ≥ 1.3 × the need at every handle angle |
| Return-spring shear stress | Handle down | — | ≈ 480 MPa | Shot-peened music wire (Rm ≈ 1,900 MPa), long fatigue life |
| Die spring travel, % of free length | Per stroke | Not set | B: red 12.5–37.5% · C: green 6–31%, blue 19–36% | Red max ≈ 30%; green 35% and blue 33.75% for 500,000 strokes |

These are hand calculations: simple beam and pin bending with peak toggle loads, and no fatigue factors except where noted. A mechanical engineer should check them, and the prototype must pass the proof-load and endurance tests in the build pack (section 10) before more presses are built.

## Maintenance schedule

| When | Task |
|---|---|
| Each shift | Wipe the die table, rails and dies. Blow shell chips out of the frames. No oil on the dies. |
| Weekly or 5,000 strokes | Check the thumb screws, the die lock screw and the handle-stop setting. Light oil on the rails only. |
| 25,000 strokes | Check handle play (≤ 1 mm at the grip) and the column nut torque. Look for tin pick-up on the die edges; clean it with a brass brush and re-polish. |
| 250,000 strokes | Replace the die springs and return springs. Inspect the bushings and pins. Dye-penetrant check the die corners. |

## Un-jam procedure

1. Stop. Don't force the handle past the point where it stops.
2. Lift the handle back to its open stop.
3. If a shell is stuck in the upper ring, slide station B under the ram with no back plate. Make a slow partial stroke; the plug pushes the shell out into station B.
4. Lift stuck parts out of station B by hand, wearing gloves. Near the rings, use a brass or plastic rod, never a screwdriver.
5. Check the ring bores and lead-ins for scratches before you restart.
