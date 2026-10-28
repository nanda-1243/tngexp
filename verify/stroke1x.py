"""Stroke 1 (pickup fold) with the explicit strip solver, straight edge, frame of the rings (ring A top = 0, upper ring
bottom = 0). Pedestal (side x = -0.5, top edge R0.8) rises 5.6 through ring A into the upper ring (bore x = +0.175,
lead-in 0.3 x 30 deg). Blank: tin 0.20 + paper 0.12 + film 0.075, edge at x = +6.0 (X + 12), lying in ring A's 0.6 recess.
Then the plug (bottom 5.5 above the ring, R1 lip, edge x = +0.15) comes down 0.2 (travel 34 -> 34.2), and finally the
pedestal drops away so the shell springs back in the upper ring.

python stroke1x.py [job] [mu] [ped_r] [travel]
"""
import math
import pickle
import sys
import time

import numpy as np

import xform as XF

job = sys.argv[1] if len(sys.argv) > 1 else 'x1'
mu = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
ped_r = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8
travel = float(sys.argv[4]) if len(sys.argv) > 4 else 5.6
blank_edge = float(sys.argv[5]) if len(sys.argv) > 5 else 6.0

layers = [XF.TIN(10), XF.PAPER(3), XF.FILM(2)]
T = sum(L.t for L in layers)
y_mid = -0.6 + T / 2
dx = 0.04
xs = np.arange(-4.0, blank_edge + 1e-9, dx)
X0 = np.stack([xs, np.full_like(xs, y_mid)], 1)


def arc(cx, cy, r, a0, a1, ds=0.03):
    n = max(2, int(math.ceil(abs(a1 - a0) * r / ds)))
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


def dedup(pts):
    out = []
    for p in pts:
        if not out or math.dist(out[-1], p) > 1e-9:
            out.append(p)
    return out


y0 = -0.6
cx, cy = -0.5 - ped_r, y0 - ped_r
ped = dedup([(-0.5, y0 - 9)] + arc(cx, cy, ped_r, 0, math.pi / 2) + [(-5.0, y0)])
li = 0.3 * math.tan(math.radians(30))
upr = [(0.175, 9.0), (0.175, 0.3), (0.175 + li, 0.0), (7.5, 0.0)]
ra = dedup([(6.25, 0.0), (6.25, -0.6), (0.8, -0.6)] + arc(0.8, -1.1, 0.5, math.pi / 2, math.pi) + [(0.3, -6.0)])
plug = dedup([(-5.0, 5.5), (-0.85, 5.5)] + arc(-0.85, 6.5, 1.0, -math.pi / 2, 0) + [(0.15, 10.0)])

T1, T2, T3 = 0.40, 0.05, 0.10          # fold, plug press, release
s = lambda u: u * u * (3 - 2 * u)
tt = np.linspace(0, T1, 41)
ped_tab = [(t, 0.0, travel * s(t / T1)) for t in tt] + [(T1 + T2, 0.0, travel), (T1 + T2 + T3, 0.0, travel - 1.5), (9.0, 0.0, travel - 1.5)]
plug_tab = [(0.0, 0.0, 0.0), (T1, 0.0, 0.0), (T1 + T2, 0.0, -0.2), (T1 + T2 + T3 * 0.3, 0.0, 0.3), (9.0, 0.0, 0.3)]
fix_tab = [(t, None, y_mid + travel * s(t / T1)) for t in tt] + [(9.0, None, y_mid + travel)]
tools = [XF.Tool('PED', ped), XF.Tool('UPR', upr), XF.Tool('RINGA', ra), XF.Tool('PLUG', plug)]
sim = XF.Sim(X0, layers, tools, mass_scale=1e4, kn=2e4, mu=mu, vreg=0.5, damping=20.0, self_contact=True)
dt = sim.stable_dt()
sim.beta = 0.1 * dt
fixes = {0: XF.table([(t, xs[0], y) for (t, _, y) in fix_tab]), 1: XF.table([(t, xs[1], y) for (t, _, y) in fix_tab])}
ttabs = [XF.table(ped_tab), XF.table([(0, 0, 0), (9, 0, 0)]), XF.table([(0, 0, 0), (9, 0, 0)]), XF.table(plug_tab)]
t0 = time.time()
recT, recX, recF = XF.run_fast(sim, T1 + T2 + T3 + 0.05, ttabs, fixes, dt=dt, rec_every=max(1, int(0.002 / dt)))
print('%s: %d nodes, dt %.2e s, %d steps, %.0f s wall' % (job, len(xs), dt, int((T1 + T2 + T3 + 0.05) / dt), time.time() - t0))
pickle.dump(dict(recT=recT, recX=recX, recF=recF, tools=tools and {t.name: t.pts for t in tools}, ttabs=ttabs, X=sim.X, V=sim.V,
                 ep=sim.ep, alpha=sim.alpha, layers=[(L.name, L.t) for L in layers], T=T, mu=mu, ped_r=ped_r, travel=travel,
                 L0=sim.L0, eprev=sim.eprev, kprev=sim.kprev, times=(T1, T2, T3)), open(job + '.pkl', 'wb'))
# summary: peak pedestal force (N per mm of edge), wall depth, final shape
Fp = -recF[:, 0, 1]
k = np.argmax(Fp)
print('peak pedestal force %.2f N/mm at pedestal travel %.2f mm' % (Fp[k], np.interp(recT[k], [p[0] for p in ped_tab], [p[2] for p in ped_tab])))
Xf = sim.X
print('strip end (cut edge) at x %.3f, y %.3f; lowest point y %.3f; max plastic strain %.3f' % (Xf[-1, 0], Xf[-1, 1], Xf[:, 1].min(), sim.alpha.max()))
