# MagPress L1: light press, 63.5 × 63.5 (rev L1-A, 29 Oct 2026)

A light hand press for one magnet size, the 2.5 inch square, made the way market magnets are made. The flat tin is
folded once, with a sharp crease at the face and a flap angled back onto the acrylic card. The photo and film wrap round
the crease.

This was designed after the owner chose to develop a lighter press than the heavy MagPress M4. The M4 stays as the
comparison design. The drawings, DXF cutting files, BOM and STEP files went to Vaishnavi Engineering Industries for quotes.

**Material sizes are assumed** until one pre-cut set from the chosen seller is measured: tin 71.5 × 71.5 × 0.23, photo
and film 79 × 79 octagons, acrylic card 60.5 × 60.5 × 3.0, magnet sheet 57 × 57 × 1.0. The parts marked MAT on the
drawings (pedestal, ring A, cup ring, riser, upper ring, plug) follow these sizes and change by a few tenths of a mm when
the real sizes come in. The frame does not change.

## How it works

Two stations sit on a sliding table, which clicks into position with a ball detent. One magnet takes two strokes:

1. **Station A, stroke 1.** Put the flat tin in ring A's small pocket, the photo face-up on it, and the film on top.
   - The upper ring lands on ring A and carries it 8.5 mm down round a fixed pedestal.
   - The upper ring is held by 4 heavy springs with 2.9 kN of preload, so the flat tin folds up its bore. The face goes
     7.1 mm into the ring, so the whole wall ends up in the straight part of the bore.
   - Ball plungers keep the shell in the upper ring when the ram goes up.
2. **Station B, stroke 2.** Put the acrylic card in the cup, with the magnet sheet already stuck on its back.
   - The upper ring lands on the cup ring, with a 1 mm nose on the cup ring filling the ring's mouth.
   - The plug pushes the shell down 7.1 mm onto the card.
   - The cup ring's 18° taper turns the tin flap in onto the back corner of the card.

Both strokes end with the plug face at the same height. Two handle-stop bolts in the head set that height
(1° = 0.08 mm), and plug shims set station B against station A.

## Main numbers (light/calcs.py, light/results.txt)

| | |
|---|---|
| Mass | 25.9 kg, from the 3D model (base 7.4, head 3.6, ram 2.0) |
| Footprint, height | 360 × 220 base; about 650 mm with the handle up |
| Toggle | crank 18, link 55, grip 400 from the pivot; ram stroke 14.1 mm |
| Force at the die | stroke 1 fold about 2.1 kN (2D forming model); stroke 2 2.9–4.6 kN of springs plus about 1 kN to turn the flap in |
| Hand force | peak about 190 N (20 kg) in stroke 2, about 120 N in stroke 1 |
| Upper springs | 4 × ISO 10243 red D20 × 76, 11.5 mm preload (2.87 kN, 19 % over the stroke-1 load), 24.5 % at full travel |
| Frame at the 15 kN abuse load | head 95 MPa, pins 145–154 MPa (EN8), cheek screws 102 MPa, columns 89 MPa in the thread |
| 3D interference check | none, at both stations, through the whole stroke and while the table slides |

The toggle is a lever fork: two lever plates turn on two 16 mm stub pins held in cheeks on the head, with one central link
to a clevis on the ram. An earlier single-plate layout put a 12 mm pin O in bending at 1100 MPa under the 15 kN load. That
layout was dropped.

## Forming checks (verify/, 2D plane-strain model)

Figure: `docs/verification/light_forming.png`.

- **Stroke 1 passes.** It uses a flat 71.5 blank on a 0.75 ledge, an R2.5 mouth on the upper ring, and a 63.85 bore.
  Peak 7.8–8.3 N/mm (µ 0.15–0.25), about 2.1 kN on the 254 mm edge.
  - With a 4.6 recess the wall ended in the mouth and sprang back into a 0.9 mm flare.
  - With the 7.1 recess the whole wall ends in the straight bore, with no flare.
- **Stroke 2: the deep recess alone is not enough.**
  - 4.6 recess, flat cup rim: the flared end lands on the rim and the wall buckles.
  - 4.6 recess with the nose: the flare is pinched between the nose and the mouth.
  - 7.1 recess, flat rim: the wall bows into the mouth as it passes, catches the rim and buckles.
  - Each time, as in the heavy design, the cause is the same: the wall must be held from outside all the way to the face.
- **Stroke 2 passes with the 7.1 recess and a 1 mm nose on the cup ring** (µ 0.15 and 0.25).
  - The nose fills the upper ring's mouth (0.05 clear) and carries the 18° taper up. It leaves at most about 0.2 mm of
    unsupported gap.
  - The wall slides into the taper and the flap turns in to end on the card's back corner.
  - Little force is needed until the face meets the card.
  - The plug is 63.4, so it passes inside the nose.
- **The flap is a little long for the cup in the model.** It reaches the cup floor about 0.2 mm before the face is fully
  down. Tune the tin blank (about 71.0) or the cup depth once the real material is measured.
- The photo and film tuck cannot be modelled in 2D. **Prove both strokes on the first die set with real material:**
  - make it in P20 (pre-hardened, no heat treatment);
  - then order hardened D2 if you need the die life.

## Files

| File | What |
|---|---|
| `l1.py` | All parameters, part outlines, features, bought parts (single source) |
| `build_models.py` | STEP of each part and the assembly, GLB, interference check, projections for the drawings |
| `render.js` | Renders of the assembly for the drawing set |
| `build_drawings.py` | A3 drawing set (28 sheets), DXF zip, BOM CSV |
| `calcs.py`, `results.txt` | Kinematics, hand force, springs, strength |
| `release/L1-A/` | The issued PDF, DXF zip, BOM, STEP zip |

Build: `python light/build_models.py OUT`, then `node light/render.js OUT/assembly OUT`, then
`python light/build_drawings.py DWG OUT`, then `node cad/render.js DWG MagPress-L1_Drawings_L1-A.pdf`. Use CadQuery's Python
for the two Python steps.
