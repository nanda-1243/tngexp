# Verification findings (Rev E) — running list

## Fit check: fasteners and pins (fsim/fitcheck.py -> fitcheck.txt)
- 91 fasteners/pins: every screw threads >= 1.3 d into steel (M5 8.1–14.1 mm, M8 11.0, M10 13.2, M16 nut 13.0 full), every head/countersink seats on the clamped part, no screw threaded into two parts except the adjustable stop screws BUY-04 (by design, with lock nut).
- By design (not faults): key pins BUY-37 enter the kit ring slot 1.5 mm (keying only; rings are held by their pockets); spigot dowels BUY-47 enter the station base 7 mm (drop-in locator, lifts out).
- FIX (minor): orientation pin BUY-42 Ø4×10 enters the die holder MP-111 only 3.0 mm (less with shims). Change to Ø4×12 and deepen the MP-111 hole to 8 → 5–6 mm engagement.

## Solver validation (fsim/val1.py, explicit strip solver xform.py)
- Elastic cantilever tip deflection 0.02267 mm vs beam theory 0.02275 (-0.36 %).
- Plastic collapse: 0.95 x collapse load -> small deflection (0.74 mm, partly plastic); 1.05 x -> 3.049 mm vs rigid-plastic hinge estimate 3.034 mm (0.5 %).
- CalculiX implicit 2D contact model of the same fold did not converge (contact chattering at the lead-in), so the explicit solver is used for forming.

## Lateral alignment stack (worst case vs clearance)
- Ram bushing/column ±0.027, holder/shank ±0.015, upper carrier on shoulder screws ±0.02, upper ring in pocket ±0.015, station pilot ±0.015, station base dowels ±0.011, lower carrier ±0.02, ring in pocket ±0.015 → worst case ±0.14, RSS ±0.05.
- Slack: stroke 1 pedestal/upper-ring gap 0.675 per side minus 0.395 stack = 0.28; stroke 2 ring B X+0.45 vs shell X-0.21 = 0.33 per side + 1.2 lead-in. OK.

## Grip of the folded shell in the upper ring (to be answered by the forming sim)
- Shell outer = pedestal X-1.0 + 2 x 0.395 = X-0.21; upper ring bore X+0.35 → 0.28 per side slack if the walls stand vertical.
- Ball plungers 0.2-0.3 proud → tip at X/2-0.025..-0.125 vs wall outer X/2-0.105: -0.08..+0.02 interference. Grip depends on wall springback flare.

## Structural FEA (CalculiX C3D10, gmsh, fsim/fea_frame.py)
- Crown MP-108 (C45), 16 kN up through the 4 cheek bolts, held by the column nuts: peak von Mises 136 MPa at the inner bottom edge of the cheek-bolt counterbores (hand calc 121 MPa at that line); deflection 0.045 mm. SF ≈ 2.5 on C45 yield at the abuse load; ≈ 53 MPa at the normal 6.2 kN.

## Manufacturability and Indian materials (review)
- Material equivalents commonly stocked in India: C45 ≈ EN8D/EN9 (IS 45C8); 42CrMo4 ≈ EN19; 100Cr6 ≈ EN31; S355 ≈ IS 2062 E350; 6061-T6 (Hindalco/Jindal); CuSn8 ≈ phosphor bronze PB2; A2 (1.2363) is uncommon → use D2 (1.2379, "HCHCr") for the kit parts (vacuum hardened 58–60 HRC, double temper) or Böhler K340/K110 from voestalpine. OHNS (O1) is cheaper but oil-quenched → more distortion; avoid for wire-EDM'd openings.
- Columns: 100Cr6 hardened, ground, hard-chromed — or buy induction-hardened chrome-plated bar (CK45/EN8D IH, 50–58 HRC, ~₹150/kg) and order it ground to Ø25 h6 (hydraulic rod is usually f7: specify h6 or adjust the bushing bore).
- Matched hole pitch 210.00 in base (Ø20 H7), crown (Ø20 H7) and ram (Ø32 H7 bushing bores): machine each in one set-up with the same program/fixture, inspect on CMM; or line-bore crown+ram stacked.
- Die table 6061-T6 hard anodise: anodise adds ~0.025 per surface; mask the Ø10 H8 pilot holes and dowel holes, or ream after anodising.
- Pins A/B/O: EN31 ground dowel stock; cut ring grooves before hardening, or grind them.
- Kit openings (R1 corners, Ø1.2 corner reliefs): wire EDM after hardening, 1 main + 2 skim cuts, re-temper, lap Ra 0.2 — any wire-EDM shop.
- Crimp anvil cove R0.7 swept round the block perimeter: not a 2D wire-EDM profile. Rough soft, harden, then finish by hard milling (Ø1.4 ball nose, coated carbide, 58–60 HRC) or die-sink EDM with a graphite electrode; polish. Same for the pedestal top-edge R0.8 and the plug R1 lip.
- FIX: anvil rim knife edge — the cove R0.7 is tangent to the block side at the rim, leaving a zero-thickness cusp that will chip in hardened steel. Give the rim a 0.10 flat land (cove centre moved in 0.10) — check in the hem simulation.
- Base plate MP-101 (S355), columns pulling 2 x 8 kN up through the clamp washers, 16 kN down under station B: peak 155 MPa at the top edge of the column hole (SF ≈ 2.3 at the abuse load, ≈ 60 MPa at normal load); station area sinks 0.17 mm relative to the column seats (hand calc 0.26 mm, conservative).

## Interference sweep (fsim/sweep.py -> sweep.txt)
- 63 positions, handle 64.9° (up) to 3° (stop) in 1° steps, every moving part (ram group, lever group, links) against every placed part: no overlaps anywhere (previous check covered 6 positions).
- Lever MP-113 (C45, 20 thick), 500 N lean at the stop (link force 15.6 kN at A): 127 MPa in the lug beyond pin A (SF ≈ 2.7; ≈ 51 MPa at 200 N); 295 MPa only where the pin load was applied as point loads on the bore (modelling artefact; real bushing pressure ≈ 56 MPa); grip deflection 0.49 mm.

## Corner geometry (3D, by hand from the clip line)
- Blank/photo clip line |x|+|y| = W/2+H/2+1.7. At distance a from a face corner, along the side, the flat flange is 1.7 + a long (full 6.0 from a ≈ 4.3). Finished edge needs ≈ 2.0 of flat length (bend + 2.4 side), so the edge is covered right to the corner and the back border starts mitred at 45° — the commercial look. The stroke-1 walls (5.6 deep) are notched at 45° near each corner (intended; the upper ring grips the straight runs).
- Excess material at a corner (both flanges claim it) after the clip: a 1.7 x 1.7 / 2 ≈ 1.45 mm² triangle plus the bend-zone compression → a small gusset; corner reliefs Ø1.2 in the rings give it room.

## Stroke 1 forming (explicit solver, x1_* runs, design as drawn: upper-ring lead-in 0.3 x 30°)
- The flange is DRAWN over the upper ring's mouth (bent and straightened), not wiped: force per mm of edge 14.5 (µ 0.10) to 16.8 N/mm (µ 0.25), sustained to the end of the fold. Hand calc assumed a single wiping bend: 3.4–4.4 N/mm. → 63.5: ≈ 3.8 kN, 65x90: ≈ 4.5–5 kN on the upper ring.
- The drawing force lasts to the end of the fold, so the upper ring may not give at all (plug only 0.105 above the face): fold + ring A springs (0.38 kN) must stay below the 1.57 kN preload → allowed 3.9 N/mm (65x90) to 6.1 N/mm (50x50). DESIGN FAILS STROKE 1 AS DRAWN.
- Pedestal 5.0 above the ring at the end: 1.2–1.3 mm of the 6 mm flange is still flat outside the bore (tail at x ≈ 1.4). With ring B's 1.2 x 30° lead-in (reaches x 0.92) the tail would be pinched between the upper ring and ring B in stroke 2.
- Blank X+13 does not fit the X+12.5 ring A recess: blank tolerance must stay ≤ X+12.4.
- Model limitation found: the plug pressing 0.2 into the stack on the rigid pedestal crushes the non-compressible laminate → numerical blow-up; plug now stops at touching.
- Upper-ring mouth radius sweep (µ 0.15, flange trapped on ring A's recess floor): chamfer 15.3 N/mm; R1.0 10.3; R1.5 8.6; R2.0 7.4 (mean over the fold). Helps, not enough; the trapped flange makes it a draw.
- After release (as drawn) the walls stand 0.18–0.30 off the upper-ring bore: no friction grip; the shell is held only by the 4 ball plungers (0.2–0.3 proud reach the wall: 0.07–0.12 interference).
- Ring A opened under the blank (opening X+7, 2.25 mm ledge): once the flange slides off the ledge it swings down (wiping): upper-ring force falls to 1.5–2 N/mm at the end of the fold (65x90 ≈ 0.6 kN + ring A 0.38 < 1.57 preload). Early phase while the flange still lies on the wide ledge: 8–14 N/mm (too high: the carrier would give > 5 mm). Walls hang 1.4–1.6 below the upper ring, flared out to x ≈ 0.5–1.0.
- Stroke 2 from the AS-DRAWN shell: the flat tail (to x 1.6, 0.4 below the upper ring) lies across ring B's top face → pinched between the upper ring and ring B (simulation blows up at contact). Confirms the tail problem.
- Narrow ledge (ring A opening X+10.5, 0.5 ledge) + upper-ring mouth R1.0: upper-ring force peaks 7.8 N/mm early (t≈0.12 s, pedestal ~1.2 mm into the fold), then 1–3 N/mm, ending < 1 N/mm. Carrier give at the peak: 50x50 0.6 mm, 63.5 2.7, 53x80 3.1 (plug stays clear), 65x90 4.7 (plug reaches the face: marginal). Walls hang 1.6 below the ring, flared to x ≈ 0.4.
- Shell retention: the formed wall stands ~0.2–0.3 inside the upper-ring bore → set the M3 ball plungers 0.4–0.5 proud (adjustable) so they reach it.
- Mouth R1.5 + narrow ledge: upper-ring force peak 6.3–6.5 N/mm (µ 0.15), 7.0 (µ 0.25), early in the fold; 1.1–1.6 N/mm at the end. Carrier give at the peak for 65x90 2.4–3.4 mm, plug stays 0.4–1.6 mm clear of the face; all smaller kits clearer. End force + ring A < preload: carrier back home at the end. Peak hand force in stroke 1 ≈ 260 N (65x90), 220 N (63.5), 175 N (50x50), briefly at ram travel ≈ 30.
- Walls flare to x ≈ 0.73 + 0.2 at their bottom → ring B lead-in 1.2 x 30° (reaches 0.918) is too small: make it 2.0 x 30° (reaches 1.38).
- Stroke 2 with ring B lead-in 2.0 x 30° (s2_fix): the lead-in cone opens BELOW the anvil rim (cone foot at 56.0, rim at 56.85), so the wall end slides out along the cone past the rim instead of entering the cove, then the wall buckles into an S above the back plate. The 2.0 lead-in recommendation was wrong. Rule: ring B's straight bore must reach above the anvil rim (lead-in depth ≤ 1.15, ring B top 58 vs rim 56.85). Use 1.2 deep at 35° (reaches X/2 + 1.07, clears the flared wall at 0.93) — re-run s2b_*.
- Stroke 2 with ring B 1.2 x 35° (bore guides at the rim), land 0.10 / 0, mu 0.15 / 0.25, from R1.5 and R1.0 stroke-1 shells (s2b_*): ALL FAIL the same way. The wall end meets the land/cove and is pushed INWARD; on a straight wall nothing resists that (no hoop stiffness as on round shells, the back plate edge is 0.53 inside the wall), so the whole lower wall moves 0.6 inward and lands vertically on the floor at the cove bottom; the curl never starts; plug force ~13 N/mm; the 4.5 mm free wall between the back plate top (58.2) and the face (springback bow 0.2-0.3) buckles inward into an S at y 59-60.5, folds over itself, blows up at travel ~38.2.
- Root cause: the double flat fold needs the 5.6 mm wall to carry the curling force as a column with no inside support over 4.5 mm (the void between the 1.2 back plate and the face). Plastic collapse of a bowed wall ~ M_p / e = 2.5 N·mm/mm / 0.25 mm ≈ 10 N/mm, about the curl force. Plane strain is right for the straight runs of a square shell (50-90 mm).
- Fix to test: commercial practice — a back INSERT that fills the shell (thickness ≈ shell depth − hem), edge just inside the wall, so the wall is held between the insert and ring B's bore and only ~2-3 mm is free when the curl starts; single fold under the insert into a 0.42 channel.
- Stroke-1 carrier check over the whole force curve (fsim/s1check.py: give = (F x edge + ring A springs - 1574 N preload) / 197 N/mm; plug clearance = 5.5 - pedestal travel - give, must stay > 0 while the carrier gives):
  R1.5 mu 0.15: 6590 0.22 mm (marginal); mu 0.25 (film on steel): 6590 -0.55 mm → PLUG HITS THE FACE mid-fold = jam. R1.5 IS NOT ENOUGH.
  R2.0: 6590 0.69 (0.15) / 0.34 (0.25). R2.5 mu 0.25: 6590 1.05 mm, 5380 2.33, 6363 2.68, 5050 no give. → upper ring mouth R2.5 (peak 5.8 N/mm, end 1.2). Wall bottom flares to x 1.69 (ring B lead-in must reach ~2.0).
- Insert redesign, first pass (stroke2y.py, insert 4.0/3.5 thick, edge 0.07 inside the wall, concentric cove R0.73 / insert edge R0.3, channel 0.43): the insert DOES let the cove curl the wall (y_t40: end turns 90° and runs 1.3 mm inward under the insert). But (a) the 0.035-clearance channel jams at the cove entry with mu 0.25, land 0.10 or a 3.5 insert, and the hem stops sliding after 1.3 mm even at mu 0.15 (plug 30-40, anvil 40-70 N/mm); (b) the leftover wall then bulges OUTWARD at the junction of the upper ring's mouth radius and ring B's lead-in (y 58-59.5), which has no outside support; the face corner gets a lip. The free wall during the hem is always above the insert top (58.2), i.e. inside the upper ring's mouth zone.
- Next: larger concentric radii, tight vertical channel (0.43) but a deeper floor channel (+0.15), and a SHORT hem (~1.2 mm beyond the cove) so the curl happens in the last mm of the stroke; shorter flange (blank X + 10) to keep the insert ~4 mm.
- Shorter flange (blank X + 10, ring A opening X + 8.5) makes stroke 1 WORSE, not better: peak at the mouth is the same bend (R2.5 mu 0.25: 6.43 N/mm, 6590 margin 0.05 mm; R1.5: -1.08). Keep X + 12 with mouth R2.5 (6590 worst 1.05 mm).
