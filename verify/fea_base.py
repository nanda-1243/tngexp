"""FEA of the crown MP-108 and the base plate MP-101 at the 16 kN design load (CalculiX, C3D10, linear elastic).

Crown (assembly frame, z 176-201): pin O pulls the cheeks up; the 4 M8 cheek bolts pull on the counterbore floors
(z = 184.5, facing down): 16 kN up in total. The column nuts hold the top face down round the column holes (annulus
Ø20-Ø25.4 at y = +-105); the column spigots hold the holes sideways.
Base plate (z 3-18): each column pulls up 8 kN through its clamp washer on the counterbore floor (Ø20-Ø32 at z = 11.5,
facing down); the die load pushes down 16 kN on the top face under station B (the station base footprint, spread
through the 12 mm die table: 110 x 90 mm at x = 0). Self-equilibrated: rigid modes removed at 3 points.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = '/home/user/tngexp'
sys.path[:0] = [os.path.join(ROOT, 'models'), os.path.join(ROOT, 'cad'), HERE]
os.chdir(os.path.join(ROOT, 'models'))
import build_models as B  # noqa: E402
import cadquery as cq  # noqa: E402
import fea  # noqa: E402

os.chdir(HERE)
out = []


def export(shape, name):
    p = os.path.join(HERE, name + '.step')
    cq.exporters.export(cq.Workplane().add(shape), p)
    return p


def peak(vm, exclude):
    k = max((n for n in vm if n not in exclude), key=lambda n: vm[n])
    return vm[k], P[k]
# ------------------------------------------------------------------------------------------------ base plate
base = B.at(0, 0, 3)(B.mp101())
st = export(base, 'base')
ref = [(0, y, 11.5, 20, 2.5) for y in (-105, 105)] + [(0, 0, 18, 70, 5.0)]
nodes, tets, surfs = fea.mesh(st, 10.0, refine=ref)
P = {t: np.array(p) for t, p in nodes.items()}
cbf = []
for s, d in surfs.items():
    c, n = d['com'], d['normal']
    if d['type'] == 'Plane' and abs(c[2] - 11.5) < 0.05 and n[2] < -0.9 and abs(abs(c[1]) - 105) < 1:
        cbf.append(s)
acb = sum(surfs[s]['area'] for s in cbf)
cb = [f for s in cbf for f in fea.faces_of(tets, surfs[s]['tris'])]
topf = [s for s, d in surfs.items() if d['type'] == 'Plane' and abs(d['com'][2] - 18) < 0.05 and d['normal'][2] > 0.9]
# die load: nodal forces on top-face nodes inside the 110 x 90 footprint (tributary-equal)
tnodes = sorted(set(n for s in topf for n in surfs[s]['nodes'] if abs(P[n][0]) <= 55 and abs(P[n][1]) <= 45))
cl = [(n, 3, -16000.0 / len(tnodes)) for n in tnodes]
# rigid-body removal: three far corner nodes (3-2-1)
def nearest(x, y, z):
    return min(P, key=lambda t: (P[t][0] - x) ** 2 + (P[t][1] - y) ** 2 + (P[t][2] - z) ** 2)
a, b, c = nearest(-230, -130, 3), nearest(230, -130, 3), nearest(-230, 130, 3)
fea.write_inp(os.path.join(HERE, 'base.inp'), nodes, tets, 205000, 0.29,
              bcs=[([a], 1, 3, 0.0), ([b], 2, 3, 0.0), ([c], 3, 3, 0.0)], dloads=[(cb, 8000.0 * 2 / acb)], cloads=cl)
rc = fea.run('base', HERE)
U, S = fea.read_results(os.path.join(HERE, 'base.frd'))
vm = {n: fea.mises(s) for n, s in S.items()}
bearing = set(n for s in cbf for n in surfs[s]['nodes'])
pk_all = peak(vm, set())
pk_body = peak(vm, bearing)
# deflection that matters: die-table seat under station B relative to the column feet
col = [n for n in P if abs(P[n][2] - 18) < 1e-3 and any(math.hypot(P[n][0], P[n][1] - yc) < 20 for yc in (-105, 105))]
mid = [n for n in tnodes]
rel = np.mean([U[n][2] for n in mid]) - np.mean([U[n][2] for n in col])
out.append('BASE PLATE MP-101 (S355, yield 355 MPa): %d tets, ccx rc %d' % (len(tets), rc))
out.append('  peak von Mises %.0f MPa at (%.1f, %.1f, %.1f); away from the clamp-washer seats %.0f MPa at (%.1f, %.1f, %.1f)' %
           (pk_all[0], *pk_all[1], pk_body[0], *pk_body[1]))
out.append('  station area sinks %.3f mm relative to the column seats (hand calc: 0.26 mm)' % (-rel))
open(os.path.join(HERE, 'fea_base.txt'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
