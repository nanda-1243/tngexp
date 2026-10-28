# Print templates for the MagPress M4

Blank sheets and design guides for every magnet size, made by the Magnet Studio ([`web/magnet-studio.html`](../web/magnet-studio.html)).
The studio itself lays your photos out on these sheets for you; use these files when you design in another app (Canva, Inkscape, Photoshop, Word).

- **Grey line:** cut line (the paper size). Let the photo fill the whole cut area. Square and rectangular sizes have their corners clipped at 45°: the paper folds round the edge and onto the back, and the clipped corners meet in a neat mitre there.
- **Green lines (square and rectangular sizes):** the back border. Between the dark green and the light green line the paper lies flat on the back of the magnet (about 2.8 mm wide), so text printed there is read on the back. Print it upside down at the top and bottom (the Magnet Studio does this for you). Beyond the light green line the edge folds back on itself under the back plate, out of sight. Round sizes roll the edge under, so nothing shows on the back.
- **Blue dashed line:** the edge of the magnet face.
- **Pink dotted line:** keep faces and text inside it (3 mm in from the face edge).
- **Print at 100 % ("Actual size"), never "Fit to page".** The bar at the foot of each sheet must measure 50 mm.
- Paper: 90–120 g/m² matte inkjet paper. Cut round sizes with a circle punch; the others with a trimmer, then snip the corners off along the short diagonals. Cut the mylar film the same size.
- **Tin (square and rectangular sizes, Rev E):** a flat blank of 0.20 mm soft tinplate, the same size and shape as the paper (the Tin blank column). Stroke 1 folds it round the edge together with the photo; stroke 2 folds the edge twice, flat, onto the back. Round sizes use drawn round cups instead.
- These templates use the press design's 6 mm bleed (the paper reaches 6 mm past the face). To try another bleed, set it in the Magnet Studio and save a blank template from there.

| Size | Face (mm) | Paper cut (mm) | Tin blank (mm) | Keep text inside (mm) | Per A4 | Per Letter | Files |
|---|---|---|---|---|---|---|---|
| 50 × 50 | 50 × 50 | 62 × 62, corners clipped 45° | 62 × 62, flat | 44 × 44 | 12 | 12 | [A4](A4/template_50x50_A4.pdf) · [Letter](Letter/template_50x50_Letter.pdf) · [SVG](svg/guide_50x50.svg) |
| 63.5 × 63.5 | 63.5 × 63.5 | 75.5 × 75.5, corners clipped 45° | 75.5 × 75.5, flat | 57.5 × 57.5 | 6 | 6 | [A4](A4/template_63_5x63_5_A4.pdf) · [Letter](Letter/template_63_5x63_5_Letter.pdf) · [SVG](svg/guide_63_5x63_5.svg) |
| 53 × 80 portrait | 53 × 80 | 65 × 92, corners clipped 45° | 65 × 92, flat | 47 × 74 | 9 | 6 | [A4](A4/template_53x80_portrait_A4.pdf) · [Letter](Letter/template_53x80_portrait_Letter.pdf) · [SVG](svg/guide_53x80_portrait.svg) |
| 53 × 80 landscape | 80 × 53 | 92 × 65, corners clipped 45° | 92 × 65, flat | 74 × 47 | 8 | 8 | [A4](A4/template_53x80_landscape_A4.pdf) · [Letter](Letter/template_53x80_landscape_Letter.pdf) · [SVG](svg/guide_53x80_landscape.svg) |
| 65 × 90 portrait | 65 × 90 | 77 × 102, corners clipped 45° | 77 × 102, flat | 59 × 84 | 4 | 4 | [A4](A4/template_65x90_portrait_A4.pdf) · [Letter](Letter/template_65x90_portrait_Letter.pdf) · [SVG](svg/guide_65x90_portrait.svg) |
| 65 × 90 landscape | 90 × 65 | 102 × 77, corners clipped 45° | 102 × 77, flat | 84 × 59 | 3 | 6 | [A4](A4/template_65x90_landscape_A4.pdf) · [Letter](Letter/template_65x90_landscape_Letter.pdf) · [SVG](svg/guide_65x90_landscape.svg) |
| Ø44 | Ø44 | Ø56 | drawn cup Ø44 × 4.5 | Ø38 | 15 | 12 | [A4](A4/template_D44_A4.pdf) · [Letter](Letter/template_D44_Letter.pdf) · [SVG](svg/guide_D44.svg) |
| Ø50 | Ø50 | Ø62 | drawn cup Ø50 × 4.5 | Ø44 | 12 | 12 | [A4](A4/template_D50_A4.pdf) · [Letter](Letter/template_D50_Letter.pdf) · [SVG](svg/guide_D50.svg) |
| Ø56 | Ø56 | Ø68 | drawn cup Ø56 × 4.5 | Ø50 | 8 | 6 | [A4](A4/template_D56_A4.pdf) · [Letter](Letter/template_D56_Letter.pdf) · [SVG](svg/guide_D56.svg) |
| Ø58 | Ø58 | Ø70 | drawn cup Ø58 × 4.5 | Ø52 | 8 | 6 | [A4](A4/template_D58_A4.pdf) · [Letter](Letter/template_D58_Letter.pdf) · [SVG](svg/guide_D58.svg) |

Remake these files with `node web/tools/make_templates.js print-templates`.
