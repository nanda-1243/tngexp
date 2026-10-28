"""FEA of the handle lever MP-113 (C45, 20 thick) at the stop with a 500 N lean on the grip (the 16 kN abuse case).
Lever frame: O at the origin (Ø18 bore, held), A at (Az, Ay) (Ø14 bore), grip centre at x = 320. The grip force acts
perpendicular to the lever (-y). The link force at A (≈ 15.6 kN) is set so the lever is in moment balance about O:
its line passes d = 500 x 320 / F_A from O, on the side that opposes the grip moment. It is spread over the half of the
A bore that the link pin presses on."""
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
import parts as PP  # noqa: E402
import fea  # noqa: E402

os.chdir(HERE)
prof, (Az, Ay) = PP.lever_profile()
lev = B.mp113()
p = os.path.join(HERE, 'lever.step')
cq.exporters.export(cq.Workplane().add(lev), p)
ref = [(0, 0, 0, 22, 1.5), (Az, Ay, 0, 18, 1.5), (320, 0, 0, 40, 4.0)]
nodes, tets, surfs = fea.mesh(p, 6.0, refine=ref)
P = {t: np.array(v) for t, v in nodes.items()}
Fg, xg = 500.0, 320.0
FA = 15600.0
d = Fg * xg / FA
# link line through A, at distance d from O, oriented so its moment about O cancels the grip moment (grip: -y at +x -> clockwise)
OA = np.array([Az, Ay])
L = np.linalg.norm(OA)
beta = math.asin(d / L)
best = None
for sgn in (1, -1):
    for flip in (1, -1):
        ang = math.atan2(-Ay, -Az) + sgn * beta          # roughly from A toward O, turned by beta
        u = flip * np.array([math.cos(ang), math.sin(ang)])
        mom = Az * u[1] - Ay * u[0]                       # z-moment of a unit force at A about O
        if mom > 0 and (best is None or abs(mom * FA - Fg * xg) < abs(best[1] * FA - Fg * xg)):
            best = (u, mom)
u, mom = best
# nodes on the A bore surface facing the load (force pushes the lever along u: the pin presses on the bore side toward u)
bore = [s for s, dd in surfs.items() if dd['type'] == 'Cylinder' and np.linalg.norm(dd['com'][:2] - OA) < 1.0]
bn = sorted(set(n for s in bore for n in surfs[s]['nodes']))
bn = [n for n in bn if np.dot(P[n][:2] - OA, u) > 0]
cl = [(n, 1, FA * u[0] / len(bn)) for n in bn] + [(n, 2, FA * u[1] / len(bn)) for n in bn]
# grip: nodes on the grip zone top face (y max) between x 300 and 340
gn = [n for n in P if 300 <= P[n][0] <= 340 and P[n][1] > max(q[1] for q in P.values() if 300 <= q[0] <= 340) - 0.5]
cl += [(n, 2, -Fg / len(gn)) for n in gn]
obore = [s for s, dd in surfs.items() if dd['type'] == 'Cylinder' and np.linalg.norm(dd['com'][:2]) < 1.0]
on = sorted(set(n for s in obore for n in surfs[s]['nodes']))
fea.write_inp(os.path.join(HERE, 'lever.inp'), nodes, tets, 205000, 0.29, bcs=[(on, 1, 3, 0.0)], dloads=[], cloads=cl)
rc = fea.run('lever', HERE)
U, S = fea.read_results(os.path.join(HERE, 'lever.frd'))
vm = {n: fea.mises(s) for n, s in S.items()}
loaded = set(bn) | set(on)
k1 = max(vm, key=lambda n: vm[n])
k2 = max((n for n in vm if n not in loaded and np.linalg.norm(P[n][:2] - OA) > 10 and np.linalg.norm(P[n][:2]) > 12), key=lambda n: vm[n])
tip = max(abs(U[n][1]) for n in gn)
txt = ['LEVER MP-113 (C45, yield ~340 MPa), 500 N lean at the stop, link force %.1f kN at A (line %.1f mm from O): %d tets, rc %d'
       % (FA / 1000, d, len(tets), rc),
       '  peak von Mises %.0f MPa at (%.1f, %.1f, %.1f) (bore contact zone)' % (vm[k1], *P[k1]),
       '  peak away from the bores %.0f MPa at (%.1f, %.1f, %.1f); grip deflection %.2f mm' % (vm[k2], *P[k2], tip)]
open(os.path.join(HERE, 'fea_lever.txt'), 'w').write('\n'.join(txt) + '\n')
print('\n'.join(txt))
