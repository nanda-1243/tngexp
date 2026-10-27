# MagPress M4 — manual photo fridge-magnet press

Design pack for a hand-lever toggle press that makes square and rectangular photo fridge magnets in four sizes (50 × 50, 63.5 × 63.5, 53 × 80, 65 × 90 mm). It has one universal die that stays on the press and a six-part size kit for each size.

**Status: Rev C.1, final design. Build and test a prototype before production.**

Interactive build pack (3D model, how the magnet is formed, force chart, dimensions, BOM, assembly, tests, failure review): https://claude.ai/artifact/C4NaemzVJD5yDM3Ks2FCBi. The same page is [`web/magpress-m4.html`](web/magpress-m4.html).

## What's here

| Path | Contents |
|---|---|
| [`release/`](release/) | Machine-shop drawing set (33 A3 sheets, PDF), DXF profiles for cutting and wire-EDM, and the assembly manual (PDF). If a DXF and a drawing disagree, the drawing governs. |
| [`docs/forming/`](docs/forming/README.md) | How a magnet is formed: stills of the finished magnet (front, back, edge cut open) and of each stage of both strokes, from the animated section in the build pack. |
| [`docs/assembly-manual.md`](docs/assembly-manual.md) | Assembly manual: 19 illustrated steps with parts, tools, torques and checks, then set-up, tests and kit changes. Printable PDF in [`release/`](release/MagPress-M4_Assembly-Manual_RevC1.pdf). |
| Print packs in [`release/`](release/) | Every part as its own file for 3D printing: `MagPress-M4_RevC1_print-STL_half-scale.zip` (fits a 256 mm bed), `…_print-STL_full-size.zip` and `…_print-OBJ_full-size.zip`. Folders by group; the number to print is in each file name. |
| [`models/`](models/) | 3D models of every part, made and bought (STEP, STL, OBJ), the placed assembly (STEP, GLB, OBJ) and the interference check behind Rev C.1. Printing notes in [`models/README.md`](models/README.md). |
| [`web/magpress-m4.html`](web/magpress-m4.html) | The build-pack page (single file; three.js from a CDN). |
| [`cad/`](cad/) | Python source that generates every drawing and DXF (`build.py`), plus the PDF renderer (`render.js`) and cover images. |
| [`calc/`](calc/) | `engineering_calcs.py`, the calculations behind every number in the design, and its output `results.txt`. |
| [`docs/design-notes.md`](docs/design-notes.md) | Architecture, key numbers, height stack, die system and revision history. |
| [`docs/research/`](docs/research/) | Research: [sources](docs/research/sources.md), [failure review and FMEA](docs/research/failure-review.md), and the [stepped-die study](docs/research/stepped-die-study.md). |
| [`web/tools/`](web/tools/) | Page smoke test and the cover-image renderer. |

## Rebuild

Needs Python 3 with Pillow, and Node with Playwright (Chromium).

```sh
python3 calc/engineering_calcs.py > calc/results.txt          # calculations
node web/tools/cover_shots.js web/magpress-m4.html out          # optional: re-render cover images
python3 web/tools/crop_covers.py out cad
python3 cad/build.py out cad/img_assembled.png cad/img_exploded.png
node cad/render.js "$PWD/out" MagPress-M4_Drawings_RevC1.pdf    # PDF from the SVG sheets
cp out/MagPress-M4_Drawings_RevC1.pdf out/MagPress-M4_DXF_RevC1.zip release/
node web/tools/check_page.js web/magpress-m4.html               # page smoke test
node web/tools/forming_stills.js web/magpress-m4.html docs/forming   # forming stills + README
python models/build_models.py                                   # 3D models (needs cadquery + trimesh)
python3 docs/assembly/manual.py                                 # assembly manual: step images, Markdown, PDF
```

## Revisions

- **Rev A:** first design.
- **Rev B:** failure review: lever, pin O, bushings, return springs, station pilot, base, 16 kN design load.
- **Rev C:** universal die and size kits, crimp anvil with roll channel, re-rated springs, final consistency check.
- **Rev C.1:** seven fit fixes from the 3D interference check, checked at six handle angles with no clashes left.

Each revision is a separate commit, so `git log` and `git diff` show what changed. The details are in [`docs/design-notes.md`](docs/design-notes.md#revision-history).

The figures are hand calculations and starting values. Have a mechanical engineer review them, and prove the die fits, the roll channel and the spring forces on a 7075 aluminium prototype kit before cutting tool steel.
