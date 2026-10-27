# MagPress M4 — 3D models (Rev C.1)

Every part of the press as its own 3D file: the 52 machined parts (including all four size kits) and the 47 bought parts from the BOM. They come in three formats, plus an assembly that shows how they fit together.

![Assembled](assembly/preview_assembled.png) ![Exploded](assembly/preview_exploded.png)

## What's here

| Path | Contents |
|---|---|
| [`step/`](step/) | One STEP file per part: exact solids that any CAD program can open and measure. |
| [`stl/`](stl/) | One STL per part, for 3D printing. |
| [`obj/`](obj/) | One OBJ per part, for viewers and rendering. |
| [`assembly/`](assembly/) | The whole press with every part in place, each a separate, named, coloured body: `MagPress-M4_assembly.step` (CAD), `.glb` (opens in Windows 3D Viewer, Blender and online viewers), `.obj` + `.mtl`. Also `interference.txt` (clash check, below) and the preview images. |
| [`parts.csv`](parts.csv) | The full list: part number, name, make or buy, group, quantity in the assembly, size, volume and file name. |
| [`build_models.py`](build_models.py) | The script that makes all of the above from the drawing source in `cad/`. |
| [`make_print_pack.py`](make_print_pack.py) | Zips the part files for printing into [`release/`](../release/): STL at half scale and full size, and OBJ at full size, in folders by group with the number to print in each file name. |

**Names.** `MP-xxx` is the drawing number. Size-kit parts end in the size code: `5050` (50 × 50), `6363` (63.5 × 63.5), `5380` (53 × 80) and `6590` (65 × 90). `BUY-xx` is a bought part, named as in the BOM (BUY-11 was deleted in Rev C.1).

**Assembly pose.** The handle is up, station B is under the ram and kit 6363 is fitted. Units are mm. X runs along the die table, Z points up from the bench and the front of the press faces −Y. The other three kits are separate part files and are not placed.

**Part files** sit in their own frame, ready to print: plates lie flat, and turned parts stand on one end.

## Printing a visual model

- **Scale.** At 50% the whole press fits a 256 × 256 mm bed. The base plate is the largest part, at 230 × 235 mm. Print every part at the same scale so they still fit together.
- **Hole fit.** Holes and pins are modelled at their true nominal size, so printed pins won't go into printed holes. Use your slicer's hole compensation (+0.15 to +0.3 mm), or print pins and screws at 97–98%.
- **Die close-up.** The die alone is the most useful thing to print: the universal die plus one size kit. At full scale it fits a 220 mm bed, since the carriers are 144 × 116 mm.
- **Skip the small hardware.** At 50% the M4/M5 screws and Ø4 pins are about 2 mm across. Leave them out, or use real ones at full scale.
- **Springs** are modelled at their installed length (return spring 109.5 mm, die springs 30 and 26 mm), so they show where they sit. A printed spring is for looks only.

## Simplifications

- No threads. Threaded holes and studs are shown at the nominal thread diameter.
- No small chamfers or edge breaks. These are also left out: the plug's R1 working lip, the upper ring's 0.6 mm lead-in and the pickup ring's R0.5 edge.
- Bought parts are plain shapes at catalogue size, not supplier models.
- The size-kit plungers are shown for kit 6363.
- Not modelled: the optional bench screws and the foam kit case.

## Interference check and the Rev C.1 fixes

`build_models.py` checks every pair of placed parts for overlap, at the assembly pose (handle up) and at five more handle angles down to the 3° stop, with the ram, lever and links moved to match. It also checks that nothing reaches below the bench. The result is in [`assembly/interference.txt`](assembly/interference.txt): **no clashes**. Die parts are not checked against each other through the stroke, because the spring-loaded rings are meant to telescope.

The first check, on Rev C, found seven clashes. Rev C.1 fixes all of them in the drawings, BOM, build pack and these models:

| # | Rev C problem | Rev C.1 fix |
|---|---|---|
| 1 | The toggle links' R12 lower ends dipped 2 mm into the ram top beside the clevis. | Two link-clearance pockets in the ram top, X ±10 to ±19, 15 long, 3 deep (MP-109 L1/L2). Heights and toggle geometry unchanged. |
| 2 | Pin B (40 mm) was wider than the 38 mm crown slot, so with the handle up its ends hit the crown. | Reliefs in the slot walls on the crown underside, to X ±21, 14 long, 5 deep (MP-108 N1/N2). Shortening the pin would leave no land outside the ring grooves. |
| 3 | Pin A hit the crown the same way with the handle down. Found by the through-stroke check. | Reliefs in the slot walls from the top, to X ±21, along pin A's path, 13 deep (MP-108 N3/N4). Crown 212 MPa at the 16 kN design load (was 192). |
| 4 | The Ø24 push knobs on the table end faces reached 6 mm below the table, into the base. | Ø14 × 18 knobs with M5 studs on the table top at X ±163 (MP-105 K1/K2). |
| 5 | The M10 × 25 column clamp screw hung 6.5 mm below the base, into the bench, and was longer than the column thread. | Base counterbore 8.5 deep (MP-101) and column spigot 6.5 (MP-107), with an M10 × 16 DIN 7984 low-head screw and a Ø32 × 2.5 hardened washer, flush underneath. No heights change. |
| 6 | The handle-stop jam nut and cap needed 9 mm where there was 7 mm. | M10 × 1 × 12 set screw with a nylon patch and no jam nut. BUY-11 (jam nut) is deleted. |
| 7 | The M6 × 0.75 × 25 stop screw could not reach through the 30 mm stop block. | M6 × 0.75 × 40. |

## Rebuild

```sh
python3 -m venv .venv && .venv/bin/pip install cadquery trimesh
.venv/bin/python models/build_models.py           # writes into models/ (about a minute)
```
