# MagPress M4 — design notes (Rev D, final)

A manual toggle press with a sliding two-station die table. It makes photo fridge magnets in two strokes (pickup, then crimp) in eight sizes: square and rectangular 50 × 50, 63.5 × 63.5, 53 × 80 and 65 × 90 mm, and round Ø44, Ø50, Ø56 and Ø58 mm (Rev D). Calculated values below come from [`calc/engineering_calcs.py`](../calc/engineering_calcs.py) ([output](../calc/results.txt)).

## Architecture

| Choice | Why |
|---|---|
| Toggle drive, crank 40, link 60, lever 320 to the grip | Force rises toward the end of the stroke, where crimping needs it: MA 6.6 at the start, 34.6 at the end. The stroke stops 8° before dead centre, so it can't lock over. |
| H-frame: two Ø25 hardened columns, crown, ram on bronze bushings | Symmetric, so the ram can't tilt under load the way a C-frame does. |
| Sliding die table, two stations ±80 mm | Load parts outside the press; no fingers under the ram. Stop blocks set coarse position and the station pilot locks it. |
| Grip lands over the base tongue | The press can't tip forward at the end of the stroke. |
| One universal die + a size kit per size (Rev C) | Springs, carriers and body are made once; a size is six small hardened parts. See [stepped-die-study.md](research/stepped-die-study.md). |
| Round kits on the same die (Rev D) | Same 106 × 81 rings with a round bore; turned plug, pedestal and anvil. The square plug's dowels sit outside a Ø44 plug, so round plugs hang on a second, inner pattern in MP-201. |

## Key numbers

| Item | Value |
|---|---|
| Ram stroke | 38.9 mm; dies meet at 26.0; working travel 12.9 |
| Force at the die, 200 N on the grip | 6.2 kN (90% pin efficiency) |
| Force needed (estimate) | 3.0 kN (50 × 50) to 4.7 kN (65 × 90) |
| Design load | 16 kN (500 N lean on the grip gives 15.6 kN) |
| Station pilot | Enters the table at 20.0 mm of travel, 6 mm before the dies meet |
| Return springs | Ø3.5 wire, OD 31.5, free 128, 4.25 N/mm: 80 N open, 245 N closed, ≥ 1.3 × the need at every angle |
| Mass | ≈ 45 kg with a kit fitted (base plate 17.5 kg) |

## Height stack (mm from the bench, handle up)

| Level | Height |
|---|---|
| Base plate (on 3 mm pads) | 3–18 |
| Die table | 18–30 |
| Station bases | 30–40 |
| Lower carriers (ledge 48–51, kit ring 51–66) | 48–66, 8 mm travel |
| Pickup pedestal / crimp anvil | 40–61.8 / 40–57 |
| Upper carrier + upper ring | 92–106, 5.5 mm retraction |
| Plug | 97.5–112 (5.5 recess in the ring) |
| Upper die body | 112–122 |
| Die holder | 123–134 |
| Ram | 134–164 |
| Crown | 176–201 |
| Pivot O | 234.5 |

## Die system (Rev C, round kits Rev D)

**Universal die (once per press):** upper die body MP-201 + shank MP-202, upper carrier MP-210, lower carriers A and B MP-211, station bases MP-205. It also holds all the springs: 8 × ISO 10243 Ø10 × 32 blue in the upper die, and 4 × Ø10 × 32 green under each lower carrier.

**Size kit (one per size):** plug MP-203 + stud MP-212, upper ring MP-204, pickup ring A MP-207, pickup pedestal MP-206, crimp ring B MP-209, crimp anvil MP-208. Rings are 106 × 81 outside for every size. Pockets are +0.01/0 and rings −0.01/−0.02. Key pins in each carrier stop a ring going into the wrong station.

**Round kit (Rev D, one per round size):** plug MP-223 + stud MP-212, upper ring MP-224, pickup ring A MP-227, pickup pedestal MP-226, crimp ring B MP-229, crimp anvil MP-228, for Ø44, Ø50, Ø56 and Ø58. Same fits and heights as the square kits (plug D + 0.30, upper ring D + 0.35, ring A D + 0.6 with a D + 12.5 film recess, ring B D + 0.45, pedestal D − 0.5, anvil platform D − 4.5). The round plug's two Ø5 dowels go in the inner holes D2 at (±12, −8) and its stud in K2 at (−4.4, 12), on the same ball-lock pin line as K. Round pedestals and anvils need no Ø4 anti-rotation pin. Peak force 2.1–2.8 kN, so the hand force at the end of the stroke stays under 90 N. Largest round size that fits the rings: about Ø65.

**Sequence.** Lower springs (75 → 380 N) are lighter than the upper springs (0.68 → 1.3 kN). At either station the lower ring is pushed down onto its stop first, and only then does the upper ring retract.
- **Station A:** the upper ring wraps the film over the shell, then grips the wrapped shell.
- **Station B:** the crimp ring sits rigid on its stop. The plug pushes the shell out of the upper ring over the back plate, and the anvil's R1.0 roll channel turns the shell edge under the back.

**Size change, about a minute, no tools:**
- **Upper:** 2 thumb screws release the upper ring, and 1 push-button pin releases the plug.
- **Lower:** each pedestal or anvil lifts out with the M5 T-handle puller, and each ring lifts out by its opening.

## Revision history

| Rev | Date | What changed |
|---|---|---|
| A | 2026-10-26 | First full design: toggle press, sliding table, four complete die sets; 30-sheet drawing set. |
| B | 2026-10-27 | Failure review ([failure-review.md](research/failure-review.md)): one-piece lever (MP-115 deleted), pin O Ø16, dry PTFE-composite bushings, stronger return springs, station pilot MP-120, 15 mm base on pads, adjustable handle stop, A2 dies re-tempered after EDM, 16 kN design load. |
| C | 2026-10-27 | Universal die + size kits (MP-201 to 212). Crimp anvil with roll channel (the Rev A/B flat pedestal could not roll the edge). Die springs re-rated to ISO 10243 limits (Rev B's red springs ran past the heavy-duty maximum). Final check: return springs lengthened to 128 mm free for ≥ 30% holding margin; mass estimate corrected to ≈ 45 kg. |
| D | 2026-10-27 | Four round size kits, Ø44, Ø50, Ø56, Ø58 (MP-223 to MP-229, 39 sheets). Upper die body MP-201 gets the inner plug pattern D2/K2. Round-kit swap checked in 3D: no clashes. Rev C.1 release kept in `release/RevC1/`. |
| C.1 | 2026-10-27 | Seven fit fixes from the 3D interference check ([models/README.md](../models/README.md#interference-check-and-the-rev-c1-fixes)): link pockets in the ram, slot-wall reliefs in the crown for pins A and B (crown 212 MPa at 16 kN), push knobs on the table top, flush column clamp (deeper base counterbore, shorter column spigot, low-head M10 × 16), handle stop without jam nut, stop screw M6 × 0.75 × 40. No heights or kinematics change. Build-pack operating steps: left and right corrected. |

## Open items for the prototype

These are start values to prove on a 7075 aluminium prototype kit before cutting tool steel:
1. Roll-channel profile on the crimp anvil (R1.0, 0.15 rim).
2. Grip fit of the upper ring (shell + 0.35) and the plunger protrusion (0.2–0.3).
3. Die-spring forces against the real pickup and crimp forces (load cell on station B).
4. A 16 kN proof load and a 10,000-stroke endurance run (build pack, section 10).

The calculations are hand calculations. A mechanical engineer should review them before production.
