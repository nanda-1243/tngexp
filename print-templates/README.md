# Print templates for the MagPress M4

Blank sheets and design guides for every magnet size, made by the Magnet Studio ([`web/magnet-studio.html`](../web/magnet-studio.html)).
The studio itself lays your photos out on these sheets for you; use these files when you design in another app (Canva, Inkscape, Photoshop, Word).

- **Grey line:** cut line (the paper size). Let the photo fill the whole cut area: the outer 6 mm folds over the rim.
- **Blue dashed line:** the edge of the magnet face.
- **Pink dotted line:** keep faces and text inside it (3 mm in from the face edge).
- **Print at 100 % ("Actual size"), never "Fit to page".** The bar at the foot of each sheet must measure 50 mm.
- Paper: 90–120 g/m² matte inkjet paper. Cut round sizes with a circle punch; the others with a trimmer or a rectangular punch (square corners, like the magnets).

| Size | Face (mm) | Paper cut (mm) | Keep text inside (mm) | Per A4 | Per Letter | Files |
|---|---|---|---|---|---|---|
| 50 × 50 | 50 × 50 | 62 × 62, square corners | 44 × 44 | 12 | 12 | [A4](A4/template_50x50_A4.pdf) · [Letter](Letter/template_50x50_Letter.pdf) · [SVG](svg/guide_50x50.svg) |
| 63.5 × 63.5 | 63.5 × 63.5 | 75.5 × 75.5, square corners | 57.5 × 57.5 | 6 | 6 | [A4](A4/template_63_5x63_5_A4.pdf) · [Letter](Letter/template_63_5x63_5_Letter.pdf) · [SVG](svg/guide_63_5x63_5.svg) |
| 53 × 80 portrait | 53 × 80 | 65 × 92, square corners | 47 × 74 | 9 | 6 | [A4](A4/template_53x80_portrait_A4.pdf) · [Letter](Letter/template_53x80_portrait_Letter.pdf) · [SVG](svg/guide_53x80_portrait.svg) |
| 53 × 80 landscape | 80 × 53 | 92 × 65, square corners | 74 × 47 | 8 | 8 | [A4](A4/template_53x80_landscape_A4.pdf) · [Letter](Letter/template_53x80_landscape_Letter.pdf) · [SVG](svg/guide_53x80_landscape.svg) |
| 65 × 90 portrait | 65 × 90 | 77 × 102, square corners | 59 × 84 | 4 | 4 | [A4](A4/template_65x90_portrait_A4.pdf) · [Letter](Letter/template_65x90_portrait_Letter.pdf) · [SVG](svg/guide_65x90_portrait.svg) |
| 65 × 90 landscape | 90 × 65 | 102 × 77, square corners | 84 × 59 | 3 | 6 | [A4](A4/template_65x90_landscape_A4.pdf) · [Letter](Letter/template_65x90_landscape_Letter.pdf) · [SVG](svg/guide_65x90_landscape.svg) |
| Ø44 | Ø44 | Ø56 | Ø38 | 15 | 12 | [A4](A4/template_D44_A4.pdf) · [Letter](Letter/template_D44_Letter.pdf) · [SVG](svg/guide_D44.svg) |
| Ø50 | Ø50 | Ø62 | Ø44 | 12 | 12 | [A4](A4/template_D50_A4.pdf) · [Letter](Letter/template_D50_Letter.pdf) · [SVG](svg/guide_D50.svg) |
| Ø56 | Ø56 | Ø68 | Ø50 | 8 | 6 | [A4](A4/template_D56_A4.pdf) · [Letter](Letter/template_D56_Letter.pdf) · [SVG](svg/guide_D56.svg) |
| Ø58 | Ø58 | Ø70 | Ø52 | 8 | 6 | [A4](A4/template_D58_A4.pdf) · [Letter](Letter/template_D58_Letter.pdf) · [SVG](svg/guide_D58.svg) |

Remake these files with `node web/tools/make_templates.js print-templates`.
