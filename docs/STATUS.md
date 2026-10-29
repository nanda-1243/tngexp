# Project status and decisions (as of 29 Oct 2026)

Read this first when resuming work. Branch `ccr-c817b2d6-3lgnb4`; build pack page `web/magpress-m4.html` (artifact
https://claude.ai/artifact/C4NaemzVJD5yDM3Ks2FCBi).

## Owner's decisions

- **Build our own press**, not a market machine. Goal: sell photo magnets with the lowest starting machine cost.
- **Develop the light design next** (slightly heavier than market machines: aluminium plates, two chrome columns, simple
  lever, unhardened steel dies, one size at a time; target about 15–20 kg, about ₹20,000–42,000 with one size). Keep
  the heavy MagPress M4 Rev E (48 kg, ₹0.85–1.45 lakh with one size) for comparison quotes.
- **Material:** the seller's pre-cut material only: flat tin sheet (always supplied flat), photo and film cut to the
  seller's size, acrylic back card, self-adhesive magnet sheet. Own raw materials later (Phase 2).
- **First size:** 2.5 inch square (63.5 × 63.5), the size of the market magnet the owner took apart.

## The product to make (market construction, confirmed with the owner)

See `docs/research/market/README.md` and `edge-section.png`:
- Tin folded **once**: sharp crease at the face edge (pointed, not a round bend), straight flap angled back under.
- Flat acrylic card inside the fold; the flap bears on its back edge.
- Photo and film folded **twice**: round the crease with the tin, then round the tin's cut edge and tucked back between
  the flap and the acrylic, for almost the full flap length. Film is an octagon (corners clipped).
- Magnet sheet on the back of the acrylic; the flap ends level with it.
- Pressing: side A presses the tin, photo and film; side B presses them onto the acrylic card with the magnet.

## Waiting for from the owner

For 63.5 × 63.5, from the seller's pre-cut set (ruler accuracy is enough):
tin sheet L × W; photo/film L × W; acrylic card L × W and 2 or 3 mm; magnet sheet L × W.
(Tin about 0.2–0.25 mm and magnet about 1 mm assumed unless told otherwise.)

## Fabricator request

Vaishnavi Engineering Industries asked for, for cost estimates of **both** the heavy and the light design:
- 2D AutoCAD drawings: unfolded / flat patterns for cutting and bending (DXF);
- an assembly PDF of the individual parts (they subcontract dies and parts).
Heavy design: drawings PDF, DXF zip and assembly manual exist in `release/RevE/`. Light design: to be produced.

## Verification findings to carry into the light design

`docs/verification.md` and `verify/`:
- Frame, fits and strength of the heavy design pass (CalculiX FEA at 16 kN, fastener and interference checks).
- Stroke 1 with a flat tin: the flange must slide off a narrow ledge and be wiped, not drawn (ring A opening X + 10.5),
  and the upper ring needs a large mouth radius (R2.5) or the upper springs give way on big sizes.
- Stroke 2: a long unsupported tin wall buckles. What works in the model: the wall held outside up to the face (tight
  rings, no big mouth or entry cone at the joint), a short skirt, and a back that fills the shell
  (`verify/stroke2c.py` reference passes). The market product does exactly this with the acrylic card.
- Heavy Rev E square kits are on hold (do not make). Orientation pin fix (Ø4 × 12) is in the sources, models not rebuilt.

## Costs

`docs/MagPress-M4_costs-India.pdf` (market vs light estimate vs heavy, Phase 1 / Phase 2 consumables, India sources).
