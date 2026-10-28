# MagPress M4 — manual photo fridge-magnet press

Design pack for a hand-lever toggle press that makes square, rectangular and round photo fridge magnets in eight sizes. The square and rectangular ones have sharp corners and the photo folded twice, flat, onto the back, so it shows as a printed border with the cut tin edge hidden, like bought tin photo magnets; the round ones have a rolled edge. Sizes: 50 × 50, 63.5 × 63.5, 53 × 80 and 65 × 90 mm, and Ø44, Ø50, Ø56 and Ø58 mm. It has one universal die that stays on the press and a six-part size kit for each size.

**Status: Rev E, final design (sharp corners, double-fold back border, flat tin blanks, and the fixes from an independent review of Rev D). Build and test a prototype before production.**

Interactive build pack (3D model, how the magnet is formed, force chart, dimensions, BOM, assembly, tests, failure review): https://claude.ai/artifact/C4NaemzVJD5yDM3Ks2FCBi. The same page is [`web/magpress-m4.html`](web/magpress-m4.html).

## What's here

| Path | Contents |
|---|---|
| [`release/RevE/`](release/RevE/) | The current release: machine-shop drawing set (40 A3 sheets, PDF), DXF profiles for cutting and wire-EDM, the assembly manual (PDF) and the print packs. If a DXF and a drawing disagree, the drawing governs. |
| [`release/RevD/`](release/RevD/), [`release/RevC1/`](release/RevC1/) | Earlier releases, kept unchanged: Rev D (round corners, rolled edge, round kits added) and Rev C.1 (square and rectangular kits only). |
| [`docs/forming/`](docs/forming/README.md) | How a magnet is formed: stills of the finished magnet (front, back, edge cut open) and of each stage of both strokes, from the animated section in the build pack. |
| [`docs/assembly-manual.md`](docs/assembly-manual.md) | Assembly manual: 19 illustrated steps with parts, tools, torques and checks, then set-up, tests and kit changes. Printable PDF in [`release/RevE/`](release/RevE/MagPress-M4_Assembly-Manual_RevE.pdf). |
| Print packs in [`release/RevE/`](release/RevE/) | Every part as its own file for 3D printing, all eight kits included: `MagPress-M4_RevE_print-STL_half-scale.zip` (fits a 256 mm bed), `…_print-STL_full-size.zip` and `…_print-OBJ_full-size.zip`. Folders by group; the number to print is in each file name. |
| [`models/`](models/) | 3D models of every part, made and bought (STEP, STL, OBJ), the placed assembly (STEP, GLB, OBJ) and the interference check behind Rev C.1 to Rev E. Printing notes in [`models/README.md`](models/README.md). |
| [`web/magpress-m4.html`](web/magpress-m4.html) | The build-pack page (single file; three.js from a CDN). |
| [`web/magnet-studio.html`](web/magnet-studio.html) | **Magnet Studio**: lays your photos out for printing. Pick a size, add photos, choose an outline, pattern, signature, date, brand mark or caption (or one of 34 ready-made looks), on the photo or on the folded border on the back, and save an A4 or Letter print sheet at true size with cut lines (PDF or 300 dpi PNG). Open it in a browser; the style libraries are in [`web/studio/`](web/studio/). |
| [`print-templates/`](print-templates/README.md) | Blank print templates (A4 and Letter PDF) and SVG design guides for every size, for designing in other apps, with the paper and tin blank sizes. |
| [`cad/`](cad/) | Python source that generates every drawing and DXF (`build.py`), plus the PDF renderer (`render.js`) and cover images. |
| [`calc/`](calc/) | `engineering_calcs.py`, the calculations behind every number in the design, and its output `results.txt`. |
| [`docs/design-notes.md`](docs/design-notes.md) | Architecture, key numbers, height stack, die system and revision history. |
| [`docs/research/`](docs/research/) | Research: [sources](docs/research/sources.md), [failure review and FMEA](docs/research/failure-review.md), the [stepped-die study](docs/research/stepped-die-study.md), the [independent review of Rev D](docs/research/design-review-revD.md) with the fixes made in Rev E, and the [market check of how square tin magnets are folded](docs/research/market-check-folds.md). |
| [`web/tools/`](web/tools/) | Page smoke test, cover-image renderer, studio style gallery (`studio_gallery.js`) and template generator (`make_templates.js`). |

## Rebuild

Needs Python 3 with Pillow, and Node with Playwright (Chromium).

```sh
python3 calc/engineering_calcs.py > calc/results.txt          # calculations
node web/tools/cover_shots.js web/magpress-m4.html out          # optional: re-render cover images
python3 web/tools/crop_covers.py out cad
python3 cad/build.py out cad/img_assembled.png cad/img_exploded.png
node cad/render.js "$PWD/out" MagPress-M4_Drawings_RevE.pdf     # PDF from the SVG sheets
cp out/MagPress-M4_Drawings_RevE.pdf out/MagPress-M4_DXF_RevE.zip release/RevE/
node web/tools/check_page.js web/magpress-m4.html               # page smoke test
node web/tools/forming_stills.js web/magpress-m4.html docs/forming   # forming stills + README
python models/build_models.py                                   # 3D models (needs cadquery + trimesh)
python3 models/make_print_pack.py                               # print packs into release/RevE/
node web/tools/make_templates.js print-templates                # blank print templates
python3 docs/assembly/manual.py                                 # assembly manual: step images, Markdown, PDF
```

## Revisions

- **Rev A:** first design.
- **Rev B:** failure review: lever, pin O, bushings, return springs, station pilot, base, 16 kN design load.
- **Rev C:** universal die and size kits, crimp anvil with roll channel, re-rated springs, final consistency check.
- **Rev C.1:** seven fit fixes from the 3D interference check, checked at six handle angles with no clashes left. Files kept in [`release/RevC1/`](release/RevC1/).
- **Rev D:** four round size kits (Ø44, Ø50, Ø56, Ø58) for the same press and universal die; the upper die body gets a second, inner plug pattern. Files kept in [`release/RevD/`](release/RevD/).
- **Rev E:** sharp-cornered magnets like bought ones: R1 kit corners; the tin starts as a flat blank with clipped corners (tin, photo and film all X + 12) and stroke 1 folds it with the photo; the crimp folds the edge twice, flat, under the back plate (a two-layer hem, the cut tin edge hidden), so the photo shows as a 2.8 mm border on the back (mitred corners), where the Magnet Studio can print a date, name or brand. Round kits keep the Rev D rolled edge. Stronger upper die springs in a 20 mm die body. Fixes from the independent review: detent pin along the die body, shank and pilot spigots, F7 drop-in fits, 120 wide crown, handle stop on a post on the crown, screw lengths, plungers, sleeves, six pads. 0 overlaps in the 3D check.

Each revision is a separate commit, so `git log` and `git diff` show what changed. The details are in [`docs/design-notes.md`](docs/design-notes.md#revision-history).

The figures are hand calculations and starting values. Have a mechanical engineer review them, and prove the die fits, the stroke-1 fold of the tin blank, the double fold and the spring forces on a 7075 aluminium prototype kit before cutting tool steel.
