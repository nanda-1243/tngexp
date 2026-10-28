# MagPress M4 — design notes (Rev E, final)

A manual toggle press with a sliding two-station die table. It makes photo fridge magnets in two strokes (pickup, then crimp) in eight sizes: square and rectangular 50 × 50, 63.5 × 63.5, 53 × 80 and 65 × 90 mm, and round Ø44, Ø50, Ø56 and Ø58 mm (Rev D). Since Rev E the square and rectangular magnets have sharp corners and the photo continues round the edge and is folded twice, flat, onto the back: a two-layer hem that shows as a printed border with the cut tin edge hidden, as on bought tin photo magnets. Round magnets keep the Rev D rolled edge. Calculated values below come from [`calc/engineering_calcs.py`](../calc/engineering_calcs.py) ([output](../calc/results.txt)).

## Architecture

| Choice | Why |
|---|---|
| Toggle drive, crank 40, link 60, lever 320 to the grip | Force rises toward the end of the stroke, where crimping needs it: MA 6.6 at the start, 34.6 at the end. The stroke stops 8° before dead centre, so it can't lock over. |
| H-frame: two Ø25 hardened columns, crown, ram on bronze bushings | Symmetric, so the ram can't tilt under load the way a C-frame does. |
| Sliding die table, two stations ±80 mm | Load parts outside the press; no fingers under the ram. Stop blocks set coarse position and the station pilot locks it. |
| Grip lands over the base tongue | The press can't tip forward at the end of the stroke. |
| One universal die + a size kit per size (Rev C) | Springs, carriers and body are made once; a size is six small hardened parts. See [stepped-die-study.md](research/stepped-die-study.md). |
| Sharp corners, double flat fold, flat tin blanks (Rev E) | Bought sharp-cornered magnets start from a flat tin blank with clipped corners that the press folds, and their edge is folded flat under the back, not rolled ([market check](research/market-check-folds.md)). Tin, photo and film are all cut X + 12 (6 mm a side). Stroke 1 folds the blank round the pickup pedestal into 5.6 mm walls; in stroke 2 the crimp anvil's cove turns the edge inward under the back plate, its platform wall turns it back on itself and the floor presses both layers flat: a two-layer hem about 2.4 mm thick, a 2.8 mm printed border with mitred corners and the cut tin edge hidden. Round kits keep the Rev D roll channel: a round edge cannot be folded flat without wrinkling. |
| Round kits on the same die (Rev D) | Same 106 × 81 rings with a round bore; turned plug, pedestal and anvil. The square plug's dowels sit outside a Ø44 plug, so round plugs hang on a second, inner pattern in MP-201. |

## Key numbers

| Item | Value |
|---|---|
| Ram stroke | 38.9 mm; dies meet at 26.0; working travel 12.9 |
| Force at the die, 200 N on the grip | 6.2 kN (90% pin efficiency) |
| Force needed (estimate) | crimp 3.0 kN (50 × 50) to 4.7 kN (65 × 90); hand force at the stop 210–268 N square, 178–201 N round (Rev E: die and return springs counted, 84% efficiency) |
| Stroke 1 fold (Rev E) | 0.9–1.3 kN to fold a 0.20 mm soft tin blank, plus 0.23 kN of ring A springs at the fold peak; the upper springs' 1.57 kN preload holds it for every size (65 × 90 just at the preload); the carrier may give up to 2.5 mm before the plug reaches the face |
| Design load | 16 kN (500 N lean on the grip gives 15.6 kN) |
| Station pilot | Enters the table at 20.0 mm of travel, 6 mm before the dies meet |
| Return springs | Ø3.5 wire, OD 31.5, free 128, 4.25 N/mm: 80 N open, 245 N closed, ≥ 1.3 × the need at every angle |
| Mass | ≈ 48 kg with a kit fitted (base plate 17.5 kg) |

## Height stack (mm from the bench, handle up)

| Level | Height |
|---|---|
| Base plate (on 3 mm pads) | 3–18 |
| Die table | 18–30 |
| Station bases | 30–40 |
| Lower carriers (ledge 48–51, kit ring 51–66) | 48–66, 8 mm travel |
| Pickup pedestal / crimp anvil (platform, Rev E) | 40–63.0 square, 40–61.8 round / 40–57.0 |
| Upper carrier + upper ring | 92–106, 5.5 mm retraction |
| Plug | 97.5–112 (5.5 recess in the ring) |
| Upper die body (Rev E: 20 thick, Ø54 counterbore for the holder) | 112–132 |
| Die holder | 123–134 |
| Ram | 134–164 |
| Crown | 176–201 |
| Pivot O | 234.5 |

## Die system (Rev C, round kits Rev D)

**Universal die (once per press):** upper die body MP-201 + shank MP-202, upper carrier MP-210, lower carriers A and B MP-211, station bases MP-205. It also holds all the springs: 8 × ISO 10243 Ø12.5 × 44 red in the upper die (Rev E, was Ø10 × 32 blue), and 4 × Ø10 × 32 green under each lower carrier.

**Size kit (one per size):** plug MP-203 + stud MP-212, upper ring MP-204, pickup ring A MP-207, pickup pedestal MP-206, crimp ring B MP-209, crimp anvil MP-208. Rings are 106 × 81 outside for every size. Pockets are +0.01/0 and rings −0.01/−0.02. Key pins in each carrier stop a ring going into the wrong station.

**Round kit (Rev D, one per round size):** plug MP-223 + stud MP-212, upper ring MP-224, pickup ring A MP-227, pickup pedestal MP-226, crimp ring B MP-229, crimp anvil MP-228, for Ø44, Ø50, Ø56 and Ø58. Same fits and heights as the square kits (plug D + 0.30, upper ring D + 0.35, ring A D + 0.6 with a D + 12.5 film recess, ring B D + 0.45, pedestal D − 0.5, anvil platform D − 4.5). The round plug's two Ø5 dowels go in the inner holes D2 at (±12, −8) and its stud in K2 at (−4.4, 12), on the same ball-lock pin line as K. Round pedestals and anvils need no Ø4 anti-rotation pin. Peak force 2.1–2.8 kN, so the hand force at the end of the stroke stays under 90 N. Largest round size that fits the rings: about Ø65.

**Sequence.** Lower springs (75 → 380 N) are much lighter than the upper springs (1.57 → 2.54 kN). At either station the lower ring is pushed down onto its stop first, and only then does the upper ring retract.
- **Station A (Rev E):** the flat tin blank, photo and film (all X + 12) lie in ring A's 0.6 mm recess. The upper ring pushes ring A down; the pedestal lifts the middle into the upper ring and folds the tin, photo and film down together round its R0.8 edge into 5.6 mm walls (fold 1). The upper ring grips the folded shell. Round kits start from a drawn cup instead.
- **Station B (Rev E):** the crimp ring sits rigid on its stop. The plug pushes the shell out of the upper ring over the back plate; the anvil's R0.7 cove turns the edge inward under the back plate (fold 2), the platform wall turns it back on itself (fold 3) and the floor presses the two layers flat: a hem. Round kits roll the edge in the Rev D channel.

**Size change, about a minute, no tools:**
- **Upper:** 2 thumb screws release the upper ring, and 1 detent pin (pulled out to the left) releases the plug.
- **Lower:** each pedestal or anvil lifts out with the M5 T-handle puller, and each ring lifts out by its opening.

## Revision history

| Rev | Date | What changed |
|---|---|---|
| A | 2026-10-26 | First full design: toggle press, sliding table, four complete die sets; 30-sheet drawing set. |
| B | 2026-10-27 | Failure review ([failure-review.md](research/failure-review.md)): one-piece lever (MP-115 deleted), pin O Ø16, dry PTFE-composite bushings, stronger return springs, station pilot MP-120, 15 mm base on pads, adjustable handle stop, A2 dies re-tempered after EDM, 16 kN design load. |
| C | 2026-10-27 | Universal die + size kits (MP-201 to 212). Crimp anvil with roll channel (the Rev A/B flat pedestal could not roll the edge). Die springs re-rated to ISO 10243 limits (Rev B's red springs ran past the heavy-duty maximum). Final check: return springs lengthened to 128 mm free for ≥ 30% holding margin; mass estimate corrected to ≈ 45 kg. |
| D | 2026-10-27 | Four round size kits, Ø44, Ø50, Ø56, Ø58 (MP-223 to MP-229, 39 sheets). Upper die body MP-201 gets the inner plug pattern D2/K2. Round-kit swap checked in 3D: no clashes. Rev C.1 release kept in `release/RevC1/`. |
| C.1 | 2026-10-27 | Seven fit fixes from the 3D interference check ([models/README.md](../models/README.md#interference-check-and-the-rev-c1-fixes)): link pockets in the ram, slot-wall reliefs in the crown for pins A and B (crown 212 MPa at 16 kN), push knobs on the table top, flush column clamp (deeper base counterbore, shorter column spigot, low-head M10 × 16), handle stop without jam nut, stop screw M6 × 0.75 × 40. No heights or kinematics change. Build-pack operating steps: left and right corrected. |
| E | 2026-10-27 | Sharp-cornered magnets like bought ones (R1 kit corners). Flat tin blanks folded in stroke 1; tin, photo and film all X + 12 with the corners clipped 45°; ring A gets a 0.6 mm recess; pedestal 23.0 high (was 21.8) with an R0.8 edge. Double-fold crimp anvil (cove R0.7, platform wall and floor under the back plate) folds the edge twice, flat: a two-layer hem, a 2.8 mm printed border on the back, mitred at the corners, the cut tin edge hidden. Round kits keep the Rev D roll-channel anvil and drawn cups. Upper springs 8 × Ø12.5 × 44 red in a 20 mm die body. Independent-review fixes ([design-review-revD.md](research/design-review-revD.md)): detent pin along X, shank and pilot spigots (pilot Ø10 42CrMo4), F7 drop-in fits, crown 120 wide (426 → 121 MPa at the cheek bolts, 16 kN), handle-stop post MP-121 on the crown, pins 39, spacers 9.75, csk Ø11.5, screws M5 × 30 / × 20, M3 ball plungers, dog-point thumb screws, POM spring sleeves, six pads, hand force counts the springs. 40 sheets; 3D check: no overlaps. Rev D release kept in `release/RevD/`. |

## Open items for the prototype

These are start values to prove on a 7075 aluminium prototype kit before cutting tool steel:
1. Rev E stroke 1: the flat 0.20 mm tin blank (X + 12) folds fully (5.6 mm walls, flat corner gussets) without the upper carrier giving way. The walls hang about 1.4 mm below the upper ring until the crimp: check they come out of ring A square.
2. Rev E double fold: cove R0.7, platform wall and floor. Check that the edge, pushed inward round the cove and back along the floor, lies flat in two layers with neat mitres and does not buckle; check the 65 × 90 fold force against the upper springs. Adjust the blank size (X + 11 to X + 13) to the real hem width.
3. Grip fit of the upper ring (shell + 0.35) and the plunger protrusion (0.2–0.3).
4. Die-spring forces against the real fold and crimp forces (load cell on station B).
5. A 16 kN proof load and a 10,000-stroke endurance run (build pack, section 10).

The calculations are hand calculations. A mechanical engineer should review them before production.
