"""Stroke 2 (crimp, double flat fold) with the explicit strip solver, page coordinates (x = 0 at the face edge, y = mm
above the bench). Starts from the stroke-1 result (shape, plastic strain) moved to station B at ram travel 33.5.

Tools (Rev E MP-208 square anvil): block side x = +0.215; cove R0.7 centre (-0.485, 56.85) from the rim (0.215, 56.85)
down to the floor 56.15; platform wall x = -3.3 up to 57.0. Back plate 57.0-58.2, edge x = -0.7. Ring B bore x = +0.225
with a 1.2 x 30 deg lead-in, top at 58 (on its stop from travel 34). Upper ring bottom = ring B top; plug bottom
97.5 - travel (R1 lip, edge x = +0.15). The shell's face is carried by the plug from travel 34.105 to the stop at 38.9.

python stroke2x.py [stroke1 job] [job] [mu] [rim_land]
"""
import math
import pickle
import sys
import time

import numpy as np

import xform as XF

src = sys.argv[1] if len(sys.argv) > 1 else 'x1'
job = sys.argv[2] if len(sys.argv) > 2 else 'x2'
mu = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
land = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0     # flat land on the anvil rim (0 = knife edge as drawn)
tstop = float(sys.argv[5]) if len(sys.argv) > 5 else 38.9
cove_r = float(sys.argv[6]) if len(sys.argv) > 6 else 0.7
plat_x = float(sys.argv[7]) if len(sys.argv) > 7 else -3.3
floor_y = float(sys.argv[8]) if len(sys.argv) > 8 else 56.15
wall_r = float(sys.argv[9]) if len(sys.argv) > 9 else 0.0   # radius at the floor / platform-wall corner

S1 = pickle.load(open(src + '.pkl', 'rb'))
layers = [XF.TIN(10), XF.PAPER(3), XF.FILM(2)]


def arc(cx, cy, r, a0, a1, ds=0.03):
    n = max(2, int(math.ceil(abs(a1 - a0) * r / ds)))
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


def dedup(pts):
    out = []
    for p in pts:
        if not out or math.dist(out[-1], p) > 1e-9:
            out.append(p)
    return out


T0 = 33.5                     # ram travel at the start
y_ring0 = 92.0 - T0            # upper ring bottom at the start (58.5)
X = S1['X'].copy()
X[:, 1] += y_ring0             # ring frame -> page frame
rim_x, rim_y = 0.215, 56.85
cx = rim_x - land - cove_r
anv = [(0.215, 50.0), (0.215, rim_y)]
if land > 0:
    anv.append((rim_x - land, rim_y))
# cove: from the rim end (angle 0) clockwise to the bottom (angle -90 deg)
anv += [(cx + cove_r * math.cos(-a), rim_y - cove_r * math.sin(a)) for a in np.linspace(0, math.pi / 2, 30)]
anv = dedup(anv)
cove_bot = (cx, rim_y - cove_r)
floor_end = plat_x + wall_r
anv += [(floor_end, floor_y)]
if wall_r > 0:
    anv += arc(plat_x + wall_r, floor_y + wall_r, wall_r, -math.pi / 2, -math.pi)[1:]
anv += [(plat_x, 57.0), (-9.0, 57.0)]
anv = dedup(anv)
li = 1.2 * math.tan(math.radians(30))
ringB = [(7.5, 58.0), (0.225 + li, 58.0), (0.225, 58.0 - 1.2), (0.225, 50.0)]
li2 = 0.3 * math.tan(math.radians(30))
upr = [(0.175, 72.0), (0.175, 58.3), (0.175 + li2, 58.0), (7.5, 58.0)]
back = [(-3.6, 57.0), (-0.7, 57.0), (-0.7, 58.2), (-9.0, 58.2)]
plug = dedup([(-6.0, 0.0), (-0.85, 0.0)] + arc(-0.85, 1.0, 1.0, -math.pi / 2, 0) + [(0.15, 6.0)])

# ram travel t(tau): 33.5 -> tstop over the forming time, smooth
TF = 0.45
sm = lambda u: u * u * (3 - 2 * u)
taus = np.linspace(0, TF, 91)
trav = T0 + (tstop - T0) * sm(taus / TF)
ring_dy = [34.0 - min(t, 34.0) for t in trav]                         # upper ring and ring B come down 0.5 to their stop at 34
plug_y = [97.5 - t for t in trav]
face0 = X[0, 1]
face_dy = [-(min(t, 34.0) - T0) - max(0.0, t - 34.105) for t in trav]
# release: plug up 2, ring B / upper ring up 2 (springs), then springback
TR = 0.1
tabs = {}
tabs['RINGB'] = [(ta, 0.0, d) for ta, d in zip(taus, ring_dy)] + [(TF + TR, 0.0, ring_dy[-1] + 3.0), (9.0, 0.0, ring_dy[-1] + 3.0)]
tabs['UPR'] = [(ta, 0.0, d) for ta, d in zip(taus, ring_dy)] + [(TF + TR, 0.0, ring_dy[-1] + 6.0), (9.0, 0.0, ring_dy[-1] + 6.0)]
tabs['PLUG'] = [(ta, 0.0, py) for ta, py in zip(taus, plug_y)] + [(TF + TR, 0.0, plug_y[-1] + 4.0), (9.0, 0.0, plug_y[-1] + 4.0)]
tabs['ANVIL'] = [(0, 0, 0), (9, 0, 0)]
tabs['BACK'] = [(0, 0, 0), (9, 0, 0)]
tools = [XF.Tool('ANVIL', anv), XF.Tool('RINGB', ringB), XF.Tool('UPR', upr), XF.Tool('BACK', back), XF.Tool('PLUG', plug)]
sim = XF.Sim(X, layers, tools, mass_scale=1e4, kn=2e4, mu=mu, vreg=0.5, damping=20.0, self_contact=True)
sim.L0 = S1['L0'].copy()
sim.wt[:] = 0
sim.wt[:-1] += sim.L0 / 2
sim.wt[1:] += sim.L0 / 2
sim.ep[:] = S1['ep']
sim.alpha[:] = S1['alpha']
dt = sim.stable_dt()
sim.beta = 0.1 * dt
fx = [(ta, X[0, 0], face0 + d) for ta, d in zip(taus, face_dy)]
fx1 = [(ta, X[1, 0], X[1, 1] + d) for ta, d in zip(taus, face_dy)]
fixes = {0: XF.table(fx), 1: XF.table(fx1)}
ttabs = [XF.table(tabs[t.name]) for t in tools]
t0 = time.time()
recT, recX, recF = XF.run_fast(sim, TF + TR + 0.05, ttabs, fixes, dt=dt, rec_every=max(1, int(0.002 / dt)))
print('%s: dt %.2e, %.0f s wall' % (job, dt, time.time() - t0))
pickle.dump(dict(recT=recT, recX=recX, recF=recF, tools={t.name: t.pts for t in tools}, ttabs=ttabs, X=sim.X, ep=sim.ep, alpha=sim.alpha,
                 taus=taus, trav=trav, TF=TF, layers=[(L.name, L.t) for L in layers], T=sum(L.t for L in layers), mu=mu, land=land,
                 tstop=tstop, cove_r=cove_r, plat_x=plat_x, floor_y=floor_y, wall_r=wall_r), open(job + '.pkl', 'wb'))
Fp = np.abs(recF[:, 4, 1])
print('peak plug force %.1f N/mm; final cut edge at (%.3f, %.3f); min y %.3f; max plastic strain %.2f'
      % (Fp.max(), sim.X[-1, 0], sim.X[-1, 1], sim.X[:, 1].min(), sim.alpha.max()))
