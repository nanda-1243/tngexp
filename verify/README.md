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
| `stroke2x.py` | Stroke 2: the shell pushed over the back plate into the anvil cove; the double flat fold | `<job>.pkl` |
| `xplot.py` | Frames of a forming run | PNG |

```sh
python fitcheck.py && python sweep.py                  # needs CadQuery (models/build_models.py)
python fea_crown.py && python fea_base.py && python fea_lever.py
python val1.py
python stroke1x.py x1 0.15 0.8 5.6 6.0                 # job, friction, pedestal edge radius, travel, blank edge (X/2 + 6)
python stroke2x.py x1 x2 0.15 0.10                     # from x1, job, friction, anvil rim land
python xplot.py x2 x2.png 0.1 0.25 0.4 0.6 --lim -4.5 1.5 55.5 60
```
