"""FEA of the crown MP-108 at the 16 kN design load (CalculiX, C3D10, linear elastic). Base plate: fea_base.py.

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


# ------------------------------------------------------------------------------------------------ crown
crown = B.at(0, 0, 176)(B.mp108())
st = export(crown, 'crown')
ref = [(x, y, z, 10, 2.0) for x in (-28, 28) for y in (-17, 17) for z in (184.5,)] + [(0, y, 201, 15, 2.5) for y in (-105, 105)] + \
      [(0, -13, 188, 40, 3.0)]
nodes, tets, surfs = fea.mesh(st, 7.0, refine=ref)
P = {t: np.array(p) for t, p in nodes.items()}
cb_faces = []
for s, d in surfs.items():
    c, n = d['com'], d['normal']
    if d['type'] == 'Plane' and abs(c[2] - 184.5) < 0.05 and n[2] < -0.9 and abs(abs(c[0]) - 28) < 1 and abs(abs(c[1]) - 17) < 1:
        cb_faces.append(s)
area = sum(surfs[s]['area'] for s in cb_faces)
faces = [f for s in cb_faces for f in fea.faces_of(tets, surfs[s]['tris'])]
p_cb = 16000.0 / area
top = [t for t, p in P.items() if abs(p[2] - 201) < 1e-3 and any(math.hypot(p[0], p[1] - yc) <= 12.7 for yc in (-105, 105))]
bores = []
for s, d in surfs.items():
    if d['type'] == 'Cylinder' and abs(abs(d['com'][1]) - 105) < 0.5 and abs(d['com'][0]) < 0.5:
        bores += list(d['nodes'])
fea.write_inp(os.path.join(HERE, 'crown.inp'), nodes, tets, 205000, 0.29,
              bcs=[(top, 3, 3, 0.0), (bores, 1, 2, 0.0)], dloads=[(faces, p_cb)])
rc = fea.run('crown', HERE)
U, S = fea.read_results(os.path.join(HERE, 'crown.frd'))
vm = {n: fea.mises(s) for n, s in S.items()}
# report peak and peak away from the loaded/supported faces (bearing peaks are local)
def peak(vm, exclude):
    k = max((n for n in vm if n not in exclude), key=lambda n: vm[n])
    return vm[k], P[k]
bearing = set(n for s in cb_faces for n in surfs[s]['nodes']) | set(top)
pk_all = peak(vm, set())
pk_body = peak(vm, bearing)
uz = max(U[n][2] for n in U)
out.append('CROWN MP-108 (C45, yield ~340 MPa): %d tets, counterbore floors %.0f mm^2 (bearing %.0f MPa), ccx rc %d' % (len(tets), area, p_cb, rc))
out.append('  peak von Mises %.0f MPa at (%.1f, %.1f, %.1f); away from bolt/nut seats %.0f MPa at (%.1f, %.1f, %.1f)' %
           (pk_all[0], *pk_all[1], pk_body[0], *pk_body[1]))
out.append('  largest upward deflection %.3f mm (hand calc for the crown: 121 MPa at the cheek-bolt line)' % uz)

open(os.path.join(HERE, 'fea_crown.txt'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
