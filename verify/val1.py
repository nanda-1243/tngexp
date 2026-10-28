"""validation: elastic cantilever (beam theory) and plastic collapse load of a single-layer strip."""
import math, time, numpy as np, xform as XF
E, nu, t, Lc = 200000.0, 0.3, 0.2, 10.0
Ep = E / (1 - nu ** 2)
I = t ** 3 / 12
n = 201
X0 = np.stack([np.linspace(0, Lc, n), np.zeros(n)], 1)
fix = {0: XF.table([(0, 0.0, 0.0), (10, 0.0, 0.0)]), 1: XF.table([(0, Lc / (n - 1), 0.0), (10, Lc / (n - 1), 0.0)])}
out = []
def sim(sy, load, T=1.5):
    lay = XF.Layer('t', t, E, nu, [(sy, 0), (sy, 10.0)], 7.85e-9, 16)
    s = XF.Sim(X0, [lay], [], mass_scale=1e4, damping=20.0, self_contact=False)
    s.beta = 0.1 * s.stable_dt()
    s.fext[-1, 1] = -load
    t0 = time.time()
    XF.run_fast(s, T, [], fix, fext_ramp=0.5)
    return s, time.time() - t0
F = 0.01
s, w = sim(1e9, F)
exact = F * Lc ** 3 / (3 * Ep * I)
out.append('elastic tip deflection %.5f mm vs beam theory %.5f mm (%.2f %%), %.1f s' % (-s.X[-1, 1], exact, 100 * (-s.X[-1, 1] / exact - 1), w))
sy = 250.0
Mp = sy * 2 / math.sqrt(3) * t ** 2 / 4
arm = Lc - Lc / (n - 1)
for frac in (0.95, 1.05):
    s, w = sim(sy, frac * Mp / arm, T=1.5)
    d = -s.X[-1, 1]
    # large-rotation rigid-plastic estimate above collapse: hinge at node 1 rotates until arm*cos = arm/frac
    rp = arm * math.sin(math.acos(min(1.0, 1 / frac))) if frac > 1 else float('nan')
    out.append('load %.2f x collapse (M_p %.3f N.mm/mm): tip deflection %.3f mm (rigid-plastic hinge estimate %.3f)' % (frac, Mp, d, rp))
print('\n'.join(out))
