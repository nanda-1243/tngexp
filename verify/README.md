# Verification scripts (Rev E)

The checks behind [`docs/verification.md`](../docs/verification.md). All open source: CalculiX 2.21 (`ccx`), gmsh,
CadQuery/OpenCASCADE, NumPy, Numba and Matplotlib. Run from this folder.

| Script | What it checks | Output |
|---|---|---|
| `fitcheck.py` | Every screw, stud, nut, set screw, plunger and pin in the placed assembly: thread or pin length held in each part, head seating, screws threaded into two parts | `fitcheck.txt` |
| `sweep.py` | Interference of every moving part against every other part at 1° steps of the handle, up to the stop | `sweep.txt` |
| `fea.py` | Helper: gmsh C3D10 meshing, CalculiX input, results reader | – |
| `fea_crown.py`, `fea_base.py`, `fea_lever.py` | Linear-elastic CalculiX models of the crown, base plate and handle lever at the 16 kN design load | `fea_*.txt` |
| `xform.py` | Explicit 2D (plane-strain) strip-forming solver: layered tin/paper/film with fibre plasticity, penalty contact with moving rigid tools, self-contact, friction | – |
| `val1.py` | Validates `xform.py` against beam theory (elastic) and the plastic collapse load with large rotation | printed |
| `stroke1x.py` | Stroke 1: the flat blank folded round the pickup pedestal into the upper ring, plug press, springback | `<job>.pkl` |
| `stroke2x.py` | Stroke 2 as drawn: the shell pushed over the back plate into the anvil cove; the double flat fold | `<job>.pkl` |
| `stroke2y.py` | Stroke 2 with a back insert that fills the shell, in the Rev E die layout | `<job>.pkl` |
| `stroke2c.py` | Reference: a commercial-style crimp (pre-formed shell, tight rings, back insert) | `<job>.pkl` |
| `stroke2L.py` | Light press L1, stroke 2: shell pushed from the upper ring into the 18° taper cup onto the acrylic card and magnet; optional nose on the cup ring | `<job>.pkl` |
| `s1check.py` | Upper-carrier give and plug clearance along the stroke-1 force curve, per square kit | printed |
| `tsize.py` | Insert thickness for a target hem length from a stroke-1 shell | printed |
| `xplot.py`, `fplot1.py`, `fplot2.py` | Frames of a forming run; the report figures | PNG |
| `fea_plot.py` | Stress maps of the frame runs | PNG |
| `findings-log.md` | Running log of every finding, in order | – |

```sh
python fitcheck.py && python sweep.py                  # needs CadQuery (models/build_models.py)
python fea_crown.py && python fea_base.py && python fea_lever.py
python val1.py
python stroke1x.py x1 0.15 0.8 5.6 6.0                 # job, friction, pedestal edge radius, travel, blank edge (X/2 + 6)
python stroke2x.py x1 x2 0.15 0.10                     # from x1, job, friction, anvil rim land
python stroke1x.py s1_m25 0.15 0.8 5.6 6.0 2.5 0.10 5.25    # ... mouth radius, plug press, ring A opening (verified fix)
python s1check.py s1_m25                                # plug clearance per kit
python stroke2c.py c_ref 0.25 4.0 4.74                   # reference crimp: job, friction, insert, skirt
python stroke1x.py L1d_s1 0.15 0.3 7.275 4.0 2.5 0.10 3.25 0.175 -0.05 7.175 0.2   # light L1 stroke 1, 7.1 recess
python stroke2L.py L1d_s1 L1d_s2n 0.15 18 0.05 3.0 1.5 1.0 3.25 1.0 -0.05          # light L1 stroke 2 with the 1 mm nose
python xplot.py x2 x2.png 0.1 0.25 0.4 0.6 --lim -4.5 1.5 55.5 60
```
