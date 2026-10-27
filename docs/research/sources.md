# Research sources

The research looked for published designs, patents, operating guides, vendor specifications and failure reports for manual badge and photo-magnet presses. No open-source CAD for this kind of press turned up. The design is built from expired patents, published operating guides and vendor specifications. Vendor pages are marketing claims, so they were used only for sizes, part lists and consumables.

## Patents (the two-stroke die principle; all expired)

- [US 4,696,086 — Die set apparatus for badges](https://patents.google.com/patent/US4696086A/en) (Dickerson, 1987). Pickup and crimp die sequence. Punch springs ≈ 100 lb, crimp springs ≈ 350 lb; the "7 N per mm of edge" force estimate is scaled from these.
- [US 6,938,518 — Two-stroke machine for buttons with coplanar shell flanges](https://patents.google.com/patent/US6938518B1/en) (Tecre, 2005). Rectangular shells 0.008–0.009 in thick, clipped corners, spring cells, scalloped bevel.
- [US 6,038,944 — Apparatus for manufacturing buttons](https://patents.google.com/patent/US6038944A/en) (Tecre, 2000). Box frame vs C/H frames, slide vs turntable, handle over the base so the press can't tip.
- [US 4,571,806 — Apparatus for assembling buttons](https://patents.google.com/patent/US4571806). Toggle-joint drive in a hand press.

## Operating guides (sequence, common faults)

- [BPL Maker button-maker guide](https://bpl.on.ca/sites/default/files/_content_files/page/PDF/BPLMaker-Button-Maker-Guide.pdf)
- [MacEwan button press guide](https://librarybeta.macewan.ca/sites/default/files/makerspace_images/Makerspace-Guides/Button-Press-Guide-Digital.pdf)
- [Emory TechLab handout](https://ats.emory.edu/_includes/documents/techlab_handouts/Assembling_1inch_buttons_2021.pdf)

## Product sizes and consumables (vendor pages)

- [JXMide square magnet machine](https://www.jxmide.com/wendy-63-563-5mm-square-shape-custom-photo-fridge-magnet-button-machine-with-cutter-and-1000pcs-magnets-2-product/) and the [Made-in-China listing](https://jxmide.en.made-in-china.com/product/QnvpmjWAJsrX/China-63-5X63-5-Custom-DIY-50X50-Magnetic-Rectangle-Square-Button-Photo-Fridge-Magnet-Making-Machine-Kit.html): the four standard sizes 50 × 50, 63.5 × 63.5, 53 × 80 and 65 × 90, plus consumable options.
- [63.5 mm kit](https://www.enters.cn/products/63-5-63-5mm-best-fridge-magnet-maker-kit) (press order: shell, mylar, paper, acrylic, magnet) and a [square kit listing](https://plastiquealaloupe.fondationtaraocean.org/products/square-magnet-button-maker-press-machine-with-100-sets-squar/213073541/) (mould A / mould B steps).
- [Grawerton 65 × 90 set](https://grawerton.pl/en/1116-set-for-making-magnets-65x90-mm-100-pcsop.html) (tin, cardboard, magnet, foil) and [IDGamax 78 × 53 supplies](https://factor.bg/en/product/4478/idgamax-78x53-mm-fridge-magnet-supplies-pack-500-pcs.html).
- [63.5 mm template guide](https://mybadgestudio.com/blog/63-5mm-square-fridge-magnet-template-guide), [Onlineprinters](https://onlineprinters.ie/p/fridge-magnets-round-%f8-7-5-cm) and [Tradeprint](https://replatform.tradeprint.co.uk/magnet-printing/fridge-magnets): bleed and safe-area guidance.
- [ISO 11949](https://online.standard.no/en/iso-11949-2026): electrolytic tinplate gauges.

## Mechanism

- [Toggle mechanism formulas](https://www.firgelliauto.com/blogs/mechanisms/toggle-mechanism) (FIRGELLI). The mechanical advantage in the design is derived directly from the linkage geometry (`calc/engineering_calcs.py`, section 1).

## Failure review (Rev B)

- [American Button Machines: common crimping issues](https://www.americanbuttonmachines.com/blogs/american-button-machines/button-making-questions-ask-abm-common-crimping-issues-solved): paper weight (24 lb copier paper, no card or photo paper), laser toner wax makes the film slip (silicone on the crimp lead-in, or a white border).
- [ABM: button maker stuck](https://www.americanbuttonmachines.com/pages/button-maker-stuck) and [how to un-jam a button maker](https://www.americanbuttonmachines.com/blogs/american-button-machines/how-to-unjam-a-button-maker-video-tutorial): double shells are the main jam cause; un-jam with a partial stroke on the crimp die.
- [Nebraska Library Commission button-maker maintenance](https://nlc.nebraska.gov/grants/innovationstudios/Documents/ButtonMaintenanceDocument.pdf): cleaning; over-oiling soils buttons.
- [Etsy "mylar not crimping" thread](https://community.etsy.com/t5/Pinback-Button-Lovers-of-Etsy/Mylar-not-crimping/td-p/35346065): film slip in practice.
- [MN Magnets fridge-magnet machine guide](https://mnmagnets.com/blogs/news/fridge-magnet-machine-guide): die sets that crack or warp after a few hundred uses; dies that arrive misaligned. Vendor-written.

## Tool steel, coatings and galling

- [A2 vs D2 (Sakysteel)](https://www.sakysteel.com/news/is-a2-tool-steel-better-than-d2-tool-steel) and [MW Alloys](https://www.mwalloys.com/a2-vs-d2-tool-steel/): A2 is roughly twice as tough as D2; D2 wears better. On these dies corner cracking, not wear, limits life, so A2 was chosen.
- [Micromachines 10(3):182](https://www.mdpi.com/2072-666X/10/3/182): PVD coatings against tinplate pick-up.
- [MISUMI punch coatings](https://us.misumi-ec.com/product/tech/info/press-die/punch-coating/index.html): TiCN / TiAlN; PVD runs at about 450 °C, so it needs a steel tempered above that.
- [The Fabricator: galling reduction through die surface treatment](https://www.thefabricator.com/thefabricator/article/bending/galling-reduction-through-die-surface-treatment).

## Die springs (ISO 10243)

- [Die spring colour codes (TEVEMA)](https://webshop.tevema.com/gb/blog/colours-die-springs) and [ISO 10243:2019](https://scc-ccn.ca/standardsdb/standards/8168099): green light, blue medium, red heavy, yellow extra heavy.
- [Accu die-spring colour charts](https://accu-components.com/us/p/496-die-spring-color-charts): light (green) 30% → 1.5 M strokes, 35% → 500 k, 40% → 200 k; medium (blue) 30% → 1.5 M, 33.75% → 500 k, 37.5% → 200 k. Light-duty rates: Ø10 × 32 = 9.4 N/mm. Medium: Ø10 × 32 = 14.2 N/mm.
- [Lesjöfors ISO 10243 Ø10 × 32 light](https://shop.lesjofors.com/at/en-US/all-products/compression-springs/1-10032-5093/) (8.5 N/mm) and [medium](https://shop.lesjofors.com/be/en-US/all-products/compression-springs/2-10032-5189/) (13 N/mm): a second check on the rates.
- [Berger heavy-load (red) die springs](https://www.berger-tools.co.uk/Die_Springs/R_-_Red_Die_Spring_Iso10243_-_Heavy_Load/PartPage/R20-305/): 20% of free length for long life, 25% medium, 30% maximum. This showed that Rev B's red springs worked to 37.5% were overloaded.
- [Barnes ISO die springs](https://pdf.directindustry.com/pdf/barnes-group/iso-die-springs/89659-634085.html): life against deflection.

## Not used

The first request in this project was for a fridge-magnet *printer*. That research (open-source inkjet projects) was dropped when the brief changed to a manual press, and it is not part of this design.
