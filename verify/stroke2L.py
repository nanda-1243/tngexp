"""Light press, stroke 2: the market edge. The upper ring (bore x_u, mouth radius from stroke 1) sits on the rim of the
crimp cup (rim top y = 0, inner edge x_r). The plug pushes the shell's face from the stroke-1 position down to the rim
level. The cup's tapered wall (angle alpha from vertical) turns the tin wall in about the face crease, so it ends as a
straight flap angled back under, bearing on the back corner of the acrylic card. Acrylic card and magnet sheet sit in the
cup (rigid here). Ring frame: x = 0 at the face line, y = 0 at the rim / upper ring bottom.

python stroke2L.py src job mu alpha x_r t_a inset_a t_m inset_m
"""
import math
import pickle
import sys
import time

import numpy as np

import xform as XF

a = sys.argv
src = a[1] if len(a) > 1 else 'L1_s1'
job = a[2] if len(a) > 2 else 'L1_s2'
mu = float(a[3]) if len(a) > 3 else 0.15
alpha = float(a[4]) if len(a) > 4 else 18.0       # cup taper from vertical, deg
x_r = float(a[5]) if len(a) > 5 else 0.05         # cup rim inner edge
t_a = float(a[6]) if len(a) > 6 else 3.0          # acrylic card thickness
inset_a = float(a[7]) if len(a) > 7 else 1.5      # acrylic card edge inside the face line
t_m = float(a[8]) if len(a) > 8 else 1.0          # magnet sheet thickness
inset_m = float(a[9]) if len(a) > 9 else 3.25     # magnet sheet edge inside the face line
nose = float(a[10]) if len(a) > 10 else 0.0       # raised nose on the cup ring top (height), filling the upper ring's mouth
plug_xo = float(a[11]) if len(a) > 11 else None    # plug edge x (default: from stroke 1)

S1 = pickle.load(open(src + '.pkl', 'rb'))
layers = [XF.TIN(10), XF.PAPER(3), XF.FILM(2)]
T = S1['T']


def arc(cx, cy, r, a0, a1, ds=0.03):
    n = max(2, int(math.ceil(abs(a1 - a0) * r / ds)))
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


def dedup(pts):
    out = []
    for p in pts:
        if not out or math.dist(out[-1], p) > 1e-9:
            out.append(p)
    return out


X = S1['X'].copy()
lift = 0.0
DROP, TL = 0.4 + nose, 0.05 + 0.15 * nose      # the cup and card start low and rise to the ring over TL: the ring landing on the cup (and its nose)
y_face = -T                                   # tin underside at the end = acrylic top
y_acr_b = y_face - t_a
y_floor = y_acr_b - t_m
x_floor = x_r - (0.0 - y_floor) * math.tan(math.radians(alpha))
cup = [(8.0, 0.0), (x_r, 0.0), (x_floor, y_floor), (-9.0, y_floor)]
if nose > 0:
    # nose: inner face = the taper carried up to y = nose, flat top, then a straight chamfer down to the flat at y = 0,
    # kept 0.04 clear of the upper ring's mouth arc (centre (x_u + R, R))
    tn = math.tan(math.radians(alpha))
    xi = x_r + nose * tn
    mr = S1.get('mouth_r', 2.5); xu = S1.get('x_u', 0.175)
    xo_top = xu + mr - math.sqrt((mr + 0.05) ** 2 - (mr - nose) ** 2)
    xo_bot = xo_top + 0.84 * nose / 1.0 * 1.0
    def fillet(pts, i, r):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        u = ((p0[0] - p1[0]) / math.dist(p0, p1), (p0[1] - p1[1]) / math.dist(p0, p1))
        v = ((p2[0] - p1[0]) / math.dist(p2, p1), (p2[1] - p1[1]) / math.dist(p2, p1))
        th = math.acos(max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1])))
        dd = r / math.tan(th / 2)
        a_ = (p1[0] + u[0] * dd, p1[1] + u[1] * dd)
        b_ = (p1[0] + v[0] * dd, p1[1] + v[1] * dd)
        bis = (u[0] + v[0], u[1] + v[1]); nb = math.hypot(*bis)
        c = (p1[0] + bis[0] / nb * r / math.sin(th / 2), p1[1] + bis[1] / nb * r / math.sin(th / 2))
        a0 = math.atan2(a_[1] - c[1], a_[0] - c[0]); a1 = math.atan2(b_[1] - c[1], b_[0] - c[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        n = 8
        return [(c[0] + r * math.cos(a0 + da * k / n), c[1] + r * math.sin(a0 + da * k / n)) for k in range(n + 1)]
    base = [(8.0, 0.0), (xo_bot, 0.0), (xo_top, nose), (xi, nose), (x_r - 1.0 * math.tan(math.radians(alpha)), -1.0)]
    cup = [base[0]] + fillet(base, 1, 0.3) + fillet(base, 2, 0.12) + fillet(base, 3, 0.12) + [(x_r, 0.0), (x_floor, y_floor), (-9.0, y_floor)]
    cup = dedup(cup)
    print('nose: inner top x %.3f, top flat to %.3f, chamfer to %.3f at y 0' % (xi, xo_top, xo_bot))
card = [(-inset_m, y_floor), (-inset_m, y_acr_b), (-inset_a, y_acr_b), (-inset_a, y_face), (-9.0, y_face)]
mouth_r = S1.get('mouth_r', 0.0)
x_u = S1.get('x_u', 0.175)
upr = dedup([(x_u, 12.0)] + arc(x_u + mouth_r, mouth_r, mouth_r, math.pi, 1.5 * math.pi) + [(8.0, 0.0)])
plug_x, plug_r = S1.get('plug_x', 0.15), S1.get('plug_r', 1.0)
if plug_xo is not None:
    plug_x = plug_xo
plug = dedup([(-6.0, 0.0), (plug_x - plug_r, 0.0)] + arc(plug_x - plug_r, plug_r, plug_r, -math.pi / 2, 0) + [(plug_x, 6.0)])

face_top0 = X[0, 1] + T / 2
TF, TR = 0.6, 0.1
sm = lambda u: u * u * (3 - 2 * u)
taus = np.linspace(0, TF, 121)
pb = [face_top0 + (0.0 - face_top0) * sm(t / TF) for t in taus]          # plug bottom = face top
taus = TL + taus
tabs = {'CUP': [(0, 0, -DROP), (TL, 0, 0), (9, 0, 0)], 'CARD': [(0, 0, -DROP), (TL, 0, 0), (9, 0, 0)], 'UPR': [(0, 0, 0), (9, 0, 0)],
        'PLUG': [(0, 0.0, pb[0])] + [(t, 0.0, p) for t, p in zip(taus, pb)] + [(TL + TF + TR, 0.0, 3.0), (9.0, 0.0, 3.0)]}
tools = [XF.Tool('CUP', cup), XF.Tool('CARD', card), XF.Tool('UPR', upr), XF.Tool('PLUG', plug)]
sim = XF.Sim(X, layers, tools, mass_scale=1e4, kn=2e4, mu=mu, vreg=0.5, damping=20.0, self_contact=True)
sim.L0 = S1['L0'].copy()
sim.wt[:] = 0
sim.wt[:-1] += sim.L0 / 2
sim.wt[1:] += sim.L0 / 2
sim.ep[:] = S1['ep']
sim.alpha[:] = S1['alpha']
dt = sim.stable_dt()
sim.beta = 0.1 * dt
dy = [p - pb[0] for p in pb]
fixes = {0: XF.table([(0, X[0, 0], X[0, 1])] + [(t, X[0, 0], X[0, 1] + d) for t, d in zip(taus, dy)] + [(9.0, X[0, 0], X[0, 1] + dy[-1])]),
         1: XF.table([(0, X[1, 0], X[1, 1])] + [(t, X[1, 0], X[1, 1] + d) for t, d in zip(taus, dy)] + [(9.0, X[1, 0], X[1, 1] + dy[-1])])}
ttabs = [XF.table(tabs[t.name]) for t in tools]
t0 = time.time()
recT, recX, recF = XF.run_fast(sim, TL + TF + 0.05, ttabs, fixes, dt=dt, rec_every=max(1, int(0.002 / dt)))
print('%s: dt %.2e, %.0f s wall' % (job, dt, time.time() - t0))
pickle.dump(dict(recT=recT, recX=recX, recF=recF, tools={t.name: t.pts for t in tools}, ttabs=ttabs, X=sim.X, ep=sim.ep, alpha=sim.alpha,
                 taus=taus, trav=np.array(pb), TF=TF, layers=[(L.name, L.t) for L in layers], T=T, mu=mu, alpha_deg=alpha, x_r=x_r,
                 t_a=t_a, inset_a=inset_a, t_m=t_m, inset_m=inset_m), open(job + '.pkl', 'wb'))
Fp = np.abs(recF[:, 3, 1])
e = sim.X[-1]
print('shell lifted %.3f at the start' % lift)
print('peak plug force %.1f N/mm; cut edge at (%.3f, %.3f); min y %.3f; max plastic strain %.2f'
      % (Fp.max(), e[0], e[1], sim.X[:, 1].min(), sim.alpha.max()))
