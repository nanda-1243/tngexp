# Independent design review of Rev D

Three independent reviews of the Rev D design, each working from the source dimensions (`cad/`, `models/`, `calc/`) and first principles, and treating the design notes, comments and manual as claims to check:

- **Structure, drive and safety:** kinematics, hand force, pins, bushings, crown, columns, springs, stability, pinch points.
- **Dies, forming and fits:** stroke timing, fit and alignment chain, forming, consumables.
- **Assembly drawing check:** hole alignment, fastener lengths, assembly order, BOM.

Date: 2026-10-27. The design has not been changed yet; these are the findings and the proposed fixes for a Rev E. The context is one press, built and used by its owner.

## Summary

The toggle drive, pins, links, bushings, lever, columns in tension and the base are sound, and the kinematics check out (stroke 38.85 mm, mechanical advantage 6.6 → 34.6, the toggle cannot lock over). The problems are in four areas:

1. **The dies**: how the crimp anvil catches the edge, the upper-to-lower alignment, the grip on the wrapped shell and the spring balance.
2. **Several fits and fastener details**: a few of them stop the press from being assembled at all.
3. **The crown and the column tops**: they are weaker than the 16 kN rating claims.
4. **Safety for a home build**: tipping, pinch points and the handle snapping back.

None of this needs a new concept. It needs a revision before any metal is cut, and a cheap prototype kit to prove the forming.

## Critical: fix before building

| # | Problem | Evidence | Proposed fix |
|---|---|---|---|
| 1 | **The plug's ball-lock pin cannot be fitted, and would not lock.** | Bore L runs front to back at X −11.2. The front column (Ø25 at X 0) is 41 mm in front of the die body, and the pin needs about 67 mm. L is blind (52 deep) while the pin's grip is 55, so the balls never reach free space. | Run the pin bore along X from an end face, as a through bore with a relief for the balls, or replace the pin with a quarter-turn cam lock. Re-place studs K / K2 on the new axis. |
| 2 | **The crimp anvil cannot catch the wrapped edge.** | The channel's outer edge sits exactly on the shell's metal line. The photo and film (0.2 mm) and the paper tails land on a 0.15 mm flat rim, with a 0.075 mm shear gap to ring B. The forming model ends the curl 1.1 mm below the back plate, so the back is not clamped. | Channel outer wall flush with ring B's bore and no flat rim. Anvil a sliding fit in ring B. Channel centre at platform level, radius about 1.3 so the curl reaches under the back. Prove it in aluminium first. |
| 3 | **The paper tails get pinched between the upper ring and ring B in stroke 2.** | The tails lie nearly flat (1.2–1.9 mm out from the wall), but ring B's lead-in is 0.69 wide. The tail is clamped at 0.06–1.4 kN while the shell is pushed 3.6 mm through. | Counterbore ring B's top (opening + 6, 1.0 deep) with a 45° bevel. Cut the paper 5 mm over the face instead of 6, which matches commercial cut sizes. |
| 4 | **Nothing sets the alignment between the upper and lower dies.** | The die body is located on the shank only by its M10 thread, and the station pilot only by an M6 thread. The rings meet flat face to flat face, and the station bases are dowelled with no adjustment. The forming tolerates about ±0.03 mm per side; the chain allows 0.1–0.3 mm. | Ground spigots (H7/g6) for the shank and the pilot. A register counterbore on rings A and B for the upper ring's nose. Align each station base with a setting plug, then ream its dowels in place. |
| 5 | **The die table cannot slide.** | The M5 ISO 10642 countersunk heads are Ø11.2 in Ø10.4 countersinks, so they stand about 0.4 proud, against 0.05 running clearance. | Countersinks Ø11.5 in the table and keepers, or use ISO 14581 screws. Check a real screw before machining. |
| 6 | **Pin A rubs on the cheeks.** | Pin A ends at X ±20, exactly at the cheek faces, from about 44° to 4° of handle angle. | Make MP-116 39.0 long. |
| 7 | **The crown is overstressed at the cheek-bolt line.** | The slot, bolt holes, counterbores and pin reliefs leave I ≈ 22,000 mm⁴: 373–426 MPa at 16 kN against C45 yield 305–340 MPa, and 150–170 MPa at working load with holes as stress raisers. | Crown 120 wide instead of 80, with no height change: 116 MPa at 16 kN. M8 10.9 cheek bolts at 35 N·m. |
| 8 | **The handle-stop hole weakens the column top thread.** | The M10 × 1 hole inside the M16 nut thread (on both columns) leaves a 2.1 mm wall: 317–457 MPa at 100 N·m nut torque. | Don't drill the columns. Put the handle stop on a post on the crown top. If the hole stays, limit the nut to 60 N·m. |

## Major: likely trouble in the prototype

| # | Problem | Proposed fix |
|---|---|---|
| 9 | **The upper ring barely grips the wrapped shell.** It covers only 1.35 mm of straight wall. The plungers sit on the corner radius and push the shell out. No M4 nylon-tip plunger is short enough for the 7.8–8.6 mm ring walls. | Ring A travel 9 so the shell goes fully in. Plungers about 2 mm above the face, or M3 ball plungers. Opening corners R4.6–5. |
| 10 | **The upper ring is held only by two cone-point thumb screws**, which take 0.3–1.4 kN every stroke. | A 3 mm lip in the upper carrier pocket takes the load. The thumb screws only retain the ring. |
| 11 | **The spring balance between the upper and lower dies is too fine.** With catalogue rates and tolerances, the worst-case margin is about 57 N, so the order of events can flip. The blue upper springs run at 34–36 % of free length. | Softer or longer lower springs (about 200 N at the stop) and more upper preload with shims. Measure on the prototype. |
| 12 | **The crimp end point has zero margin.** The handle stop and the back-plate contact coincide, and a ±1° stop or a 0.1 mm paper difference changes the result. | Let the back plate end the stroke: handle stop 1–2° beyond. Set the curl depth with the shim pack. |
| 13 | **Consumables.** Real shell depth, corner radius and back thickness differ between vendors. Standard round Ø44–58 sets use a metal back with the magnet attached, not a flat ABS disc. | Buy consumables first, measure them and size the kits to them. Pedestal X − 1.0. For round magnets, consider a commercial round badge mould plus its consumables instead of the four custom round kits. |
| 14 | **Rolling the edge at R4 corners compresses the metal about 42 %.** Expect wrinkled or loose corners. | Test on the first kit. Clipped shell corners, as commercial machines use, help. |
| 15 | **Hand force is higher than stated.** The die and return springs add 1.6 kN at the end of the stroke, and pin efficiency is about 0.84. Square kits need 157–215 N at the stop, and 230–316 N just before it. | Measure it on the prototype: a bathroom scale under the grip works. If it is high, use a longer grip (about 400 mm) or lighter upper springs. |
| 16 | **The press tips over if it isn't bolted down.** A 330 N pull at the grip tips it forward, and 162 N sideways tips it sideways. | Bolt it down or clamp it to the bench. Fit two front pads at (±60, −300). |
| 17 | **The return springs are marginal and unguided.** The lift margin is 0.97–1.11 with friction. The installed length is below the EN 13906-1 minimum. They have 7 mm of radial play and overhang the crown. | Centring spigots at both ends, the wider crown, and a lighter lever (the handle part can be 12 mm thick). |
| 18 | **Pinch points.** These are the lever onto the stop (3 × hand force), the ram-to-crown gap, the toggle scissor and the die gap. The handle springs back at 4–5 m/s if released at the bottom. | Covers over the toggle and the ram/crown gap, sleeves on the springs, and a clear shield between the columns. Keep fingers outside 25 mm gaps. |
| 19 | **The columns bow inward** about 0.04–0.05 mm each under load, against 0.02–0.05 mm bushing clearance. | One ram bushing 0.15 mm looser, so one column guides and the other only stops rotation. |
| 20 | **Fits and fastener details.** | "Drop-in" kit dowels are transition fits: ream the drop-in ends F7/G7, and use a diamond pin for the second plug dowel. Shoulder-screw patterns: transfer-drill. Key pins: move 1 mm into the wall. Pin O stack: spacers 9.75 for end float. Column clamps: Ø20 section 24.5 long, spigot 6.2, thread 20. Die-holder lock screw: 1.5 mm higher. Rail screws M5 × 30. Station-base screws M5 × 20, tapped through. MP-109 V1/V2: tap 10 deep. Station pilot: Ø10 in 42CrMo4, with the table stops set just past each station. |

## Minor

- **Clearances:**
  - The clevis counterbores break out of the end faces.
  - The die holder has a 0.5 mm wall at its counterbores.
  - Some blind dowels and studs bottom out in their holes.
  - The ball-lock pin is tangent to the stud groove with zero clearance.
- **Missing features:**
  - Return rods, shank and stud have no wrench flats.
  - Rings have no pull holes, so they cock when lifted from their pockets.
- **Mistakes in the documents:**
  - The page BOM leaves out BUY-29.
  - MP-212 needs 8 pieces, not 4.
  - Shoulder screws take a 3 mm key, not 5 mm.
  - Upper carrier travel is 6.0, not 5.5.
  - The page's assembly step 8 fits the station bases after the table is in the press.
- **Kit parts:**
  - A ring A turned upside down fits carrier B.
  - On 6590 ring A the key slot breaks into the film recess.
  - The 5050 plug has a 2.65 mm wall at its dowel.
- **Manufacturing:**
  - Skip chrome on the 0.05 mm sliding fit for the prototype.
  - Rough out the ring windows before hardening.

## For a one-off build: cheaper and simpler

- **Kits:**
  - Build one square kit first (50 × 50 or 63.5 × 63.5) and leave the round kits for later. For round magnets, a commercial badge mould and its consumables are cheap.
  - Make the first kit from 1.2312 prehardened steel or C45, with no hardening, wire EDM or chrome. Mill the corners with a Ø6 cutter and polish the forming edges. 7075 aluminium is fine for the plug, pedestal and ring A.
- **Frame:**
  - Buy chromed, induction-hardened Ø25 h6 linear shafts for the columns.
  - The ram can be 20–25 mm thick. The lever can be lighter.
- **Prove the forming early:**
  - Print the kit in PLA or resin at full size to test stroke 1 (the wrap and pickup) with real shells and paper. The print packs already have the files.
  - Measure the crimp force on the aluminium kit before cutting steel.

## Checked and OK

- **Kinematics:**
  - Stroke 38.85 mm.
  - Mechanical advantage 6.6 → 34.6.
  - The stop is 8.0° before dead centre.
  - With no stop fitted, the lever lands on the column nut 4.2° before dead centre, so it can't lock over.
- **Pins:**
  - Pin O 183 MPa working.
  - Pins A/B 170–245 MPa working.
  - Fine for hardened pins in fatigue.
- **Bushings:** 44 MPa working on the links (DU-type limit 140).
- **Links:** buckling at 395 kN.
- **Lever:** 14–36 MPa at 200–500 N.
- **Columns:** 16 MPa in tension.
- **Base:** 80–107 MPa at 16 kN.
- **Grip:** moves 524 → 251 mm above the bench, which is comfortable.
- **Hole alignment:**
  - Rails, keepers, base, stop blocks, cheeks, crown, die holder, return rods and station bases all line up.
  - The plug D/K and D2/K2 holes match the body.
- **Stroke timing (nominal):**
  - Rings meet at 26.0.
  - Lower rings reach their stop at 34.0.
  - Plug on the film at 35.3.
  - Push-out 3.6.
- **Other:**
  - Spring travel within ISO 10243 for the green springs.
  - Paper excess 17 % (Ø58) and 21 % (Ø44).
  - Page BOM quantities match the 3D parts list.
