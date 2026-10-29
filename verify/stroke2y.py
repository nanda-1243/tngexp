"""Stroke 2, single fold over a back INSERT that fills the shell (verification redesign of the Rev E hem).

Page coordinates (x = 0 at the face edge, y = mm above the bench). The stroke-1 shell keeps its formed size: wall outer
about x = -0.07, inner -0.47. Ring B bore x_rb (holds the wall outside, top lead-in straightens the flared wall bottom);
the anvil block side x_b = x_rb - 0.01 slides in it. The insert (rigid here) sits on the anvil platform: top at the face
underside at the stop (58.205), thickness t_i, edge x_e = x_b - land - h_c just inside the wall, top edge chamfer 0.8 x 45
(clears the R0.8 inside of the face fold), bottom outer edge radius r_i. The anvil cove (radius r_i + h_c) is concentric with
that edge: the wall runs down between insert and bore, turns 90 deg in the cove and runs inward under the insert in an
h_c channel (one layer of tin, photo and film). Only ~2 mm of wall is unsupported when the curl starts.

python stroke2y.py src job mu t_i land r_i h_c x_rb leadB leadA R_c step d
(d: the floor channel is h_c + d deep; the cove centre sits d below the insert edge's centre, so the bend widens downward)
(R_c: cove radius, default r_i + h_c, concentric with the insert's bottom edge; step: 0 = chamfered insert top edge, else the
insert is two laser-cut layers, the top one `step` thick and X - 2.7, clear of the R0.8 inside of the face fold)
"""
import math
import pickle
import sys
import time

import numpy as np

import xform as XF

a = sys.argv
src = a[1] if len(a) > 1 else 's1_n_r15'
job = a[2] if len(a) > 2 else 'y2'
mu = float(a[3]) if len(a) > 3 else 0.15
t_i = float(a[4]) if len(a) > 4 else 4.0
land = float(a[5]) if len(a) > 5 else 0.05
r_i = float(a[6]) if len(a) > 6 else 0.3
h_c = float(a[7]) if len(a) > 7 else 0.43
x_rb = float(a[8]) if len(a) > 8 else -0.05
leadB = float(a[9]) if len(a) > 9 else 2.0
leadA = float(a[10]) if len(a) > 10 else 30.0
R_c = float(a[11]) if len(a) > 11 and float(a[11]) > 0 else r_i + h_c
step = float(a[12]) if len(a) > 12 else 0.0
d = float(a[13]) if len(a) > 13 else 0.0
tstop, T0 = 38.9, 24.0

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


y_ring0 = 92.0 - T0
X = S1['X'].copy()
X[:, 1] += y_ring0
T = S1['T']
y_it = 97.5 - tstop - T          # insert top = face underside at the stop
y_ib = y_it - t_i
x_b = x_rb - 0.01
x_e = x_b - land - h_c
y_f = y_ib - h_c - d
x_c, y_rim = x_b - land - R_c, y_f + R_c   # cove centre (rim at the cove's top)
x_p = x_c - 3.5
anv = dedup([(x_b, 30.0), (x_b, y_rim), (x_b - land, y_rim)] + arc(x_c, y_rim, R_c, 0.0, -math.pi / 2) + [(x_p, y_f), (x_p, y_ib), (-9.0, y_ib)])
ch = 0.8
top = [(x_e, y_it - step), (-1.35, y_it - step), (-1.35, y_it), (-9.0, y_it)] if step > 0 else [(x_e, y_it - ch), (x_e - ch, y_it), (-9.0, y_it)]
ins = dedup([(-9.0, y_ib), (x_e - r_i, y_ib)] + arc(x_e - r_i, y_ib + r_i, r_i, -math.pi / 2, 0.0) + top)
li = leadB * math.tan(math.radians(leadA))
ringB = [(7.5, 58.0), (x_rb + li, 58.0), (x_rb, 58.0 - leadB), (x_rb, 40.0)]
mouth_r = S1.get('mouth_r', 0.0)
x_u, plug_x = S1.get('x_u', 0.175), S1.get('plug_x', 0.15)   # upper ring bore and plug edge, as in stroke 1
upr = dedup([(x_u, 72.0)] + arc(x_u + mouth_r, 58.0 + mouth_r, mouth_r, math.pi, 1.5 * math.pi) + [(7.5, 58.0)])
plug = dedup([(-6.0, 0.0), (plug_x - 1.0, 0.0)] + arc(plug_x - 1.0, 1.0, 1.0, -math.pi / 2, 0) + [(plug_x, 6.0)])

TF = 0.8
sm = lambda u: u * u * (3 - 2 * u)
taus = np.linspace(0, TF, 161)
trav = T0 + (tstop - T0) * sm(taus / TF)
upr_bot = lambda t: 92.0 - min(t, 34.0)
ringB_top = lambda t: 66.0 if t <= 26.0 else upr_bot(t)
plug_y = [97.5 - t for t in trav]
face0 = X[0, 1]
# ring B's lead-in meets the flared wall bottom from about travel 24.4 and pushes the shell up onto the plug
lift = lambda t: 0.105 * min(1.0, max(0.0, (t - T0) / 0.3))
face_y = [97.5 - t - T / 2 - 0.105 + lift(t) for t in trav]
face_dy = [y - face_y[0] for y in face_y]
TR = 0.1
tabs = {}
tabs['RINGB'] = [(ta, 0.0, ringB_top(t) - 58.0) for ta, t in zip(taus, trav)] + [(TF + TR, 0.0, 3.0), (9.0, 0.0, 3.0)]
tabs['UPR'] = [(ta, 0.0, upr_bot(t) - 58.0) for ta, t in zip(taus, trav)] + [(TF + TR, 0.0, 6.0), (9.0, 0.0, 6.0)]
tabs['PLUG'] = [(ta, 0.0, py) for ta, py in zip(taus, plug_y)] + [(TF + TR, 0.0, plug_y[-1] + 4.0), (9.0, 0.0, plug_y[-1] + 4.0)]
tabs['ANVIL'] = [(0, 0, 0), (9, 0, 0)]
tabs['INSERT'] = [(0, 0, 0), (9, 0, 0)]
tools = [XF.Tool('ANVIL', anv), XF.Tool('RINGB', ringB), XF.Tool('UPR', upr), XF.Tool('INSERT', ins), XF.Tool('PLUG', plug)]
sim = XF.Sim(X, layers, tools, mass_scale=1e4, kn=2e4, mu=mu, vreg=0.5, damping=20.0, self_contact=True)
sim.L0 = S1['L0'].copy()
sim.wt[:] = 0
sim.wt[:-1] += sim.L0 / 2
sim.wt[1:] += sim.L0 / 2
sim.ep[:] = S1['ep']
sim.alpha[:] = S1['alpha']
dt = sim.stable_dt()
sim.beta = 0.1 * dt
fx = [(ta, X[0, 0], face0 + d) for ta, d in zip(taus, face_dy)] + [(TF + TR, X[0, 0], face0 + face_dy[-1]), (9.0, X[0, 0], face0 + face_dy[-1])]
fx1 = [(ta, X[1, 0], X[1, 1] + d) for ta, d in zip(taus, face_dy)] + [(TF + TR, X[1, 0], X[1, 1] + face_dy[-1]), (9.0, X[1, 0], X[1, 1] + face_dy[-1])]
fixes = {0: XF.table(fx), 1: XF.table(fx1)}
ttabs = [XF.table(tabs[t.name]) for t in tools]
t0 = time.time()
recT, recX, recF = XF.run_fast(sim, TF + TR + 0.05, ttabs, fixes, dt=dt, rec_every=max(1, int(0.002 / dt)))
print('%s: dt %.2e, %.0f s wall' % (job, dt, time.time() - t0))
pickle.dump(dict(recT=recT, recX=recX, recF=recF, tools={t.name: t.pts for t in tools}, ttabs=ttabs, X=sim.X, ep=sim.ep, alpha=sim.alpha,
                 taus=taus, trav=trav, TF=TF, layers=[(L.name, L.t) for L in layers], T=T, mu=mu, t_i=t_i, land=land, r_i=r_i, h_c=h_c,
                 x_rb=x_rb, leadB=leadB, leadA=leadA, R_c=R_c, step=step, d=d, x_e=x_e, y_ib=y_ib, y_it=y_it, y_f=y_f, x_c=x_c, tstop=tstop, T0=T0), open(job + '.pkl', 'wb'))
Fp = np.abs(recF[:, 4, 1])
print('peak plug force %.1f N/mm; final cut edge at (%.3f, %.3f); min y %.3f; max plastic strain %.2f'
      % (Fp.max(), sim.X[-1, 0], sim.X[-1, 1], sim.X[:, 1].min(), sim.alpha.max()))
print('insert edge %.3f, bottom %.3f, top %.3f; floor %.3f; cove centre (%.3f, %.3f)' % (x_e, y_ib, y_it, y_f, x_c, y_rim))
