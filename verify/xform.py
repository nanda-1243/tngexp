"""Explicit 2D (plane-strain) strip-forming solver: a layered discrete rod with fibre plasticity, penalty contact
against moving rigid polyline tools, self-contact, and Coulomb friction. Units mm, N, s, tonne; per mm of width.

Strip: nodes along a reference line (the laminate mid-plane). Axial strain per segment, curvature per interior node
(turning angle / tributary length). Fibres through the thickness at every node carry 1D elastic-plastic stress
(plane-strain modulus E/(1-nu^2), plane-strain yield 2/sqrt(3) sigma_y, isotropic hardening). Internal forces follow
from virtual work: f = sum_i w_i (N_i d(eps_i)/dx + M_i d(kappa_i)/dx).
Contact: the strip is a chain of discs of radius rc (half the laminate thickness) about its nodes. Tools are polylines
with their material on the LEFT of the polyline direction (outward normal = right normal).
"""
import math

import numba as nb
import numpy as np

PS = 2.0 / math.sqrt(3.0)


class Layer:
    def __init__(self, name, t, E, nu, sy_table, rho, nf):
        self.name, self.t, self.E, self.nu, self.rho, self.nf = name, t, E, nu, rho, nf
        self.sy = np.array(sy_table, float)            # (stress, plastic strain) uniaxial


TIN = lambda nf=10: Layer('tin', 0.20, 200000.0, 0.30, [(250, 0), (290, .02), (315, .05), (340, .10), (370, .20), (420, .50), (460, 1.0), (480, 2.0)], 7.85e-9, nf)
PAPER = lambda nf=3: Layer('paper', 0.12, 2500.0, 0.20, [(15, 0), (25, .2), (40, 1.0), (50, 3.0)], 0.9e-9, nf)
FILM = lambda nf=2: Layer('film', 0.075, 3500.0, 0.35, [(60, 0), (80, .2), (120, 1.0), (140, 3.0)], 1.4e-9, nf)


def section(layers):
    """fibre table about the laminate mid-plane: z (positive = left of the strip direction = 'top'), dz, E', mat id."""
    T = sum(L.t for L in layers)
    z0 = -T / 2
    zs, dzs, Es, mid, rhoA = [], [], [], [], 0.0
    tabs = []
    for k, L in enumerate(layers):
        for f in range(L.nf):
            dz = L.t / L.nf
            zs.append(z0 + (f + 0.5) * dz)
            dzs.append(dz)
            Es.append(L.E / (1 - L.nu ** 2))
            mid.append(k)
        z0 += L.t
        rhoA += L.rho * L.t
        tabs.append(L.sy)
    nt = max(len(t) for t in tabs)
    tab = np.zeros((len(layers), nt, 2))
    for k, t in enumerate(tabs):
        tab[k, :len(t), 0] = t[:, 0] * PS
        tab[k, :len(t), 1] = t[:, 1]
        tab[k, len(t):, 0] = t[-1, 0] * PS
        tab[k, len(t):, 1] = t[-1, 1] + np.arange(1, nt - len(t) + 1)
    return T, np.array(zs), np.array(dzs), np.array(Es), np.array(mid, dtype=np.int64), tab, rhoA


@nb.njit(cache=True)
def yield_stress(tab, m, a):
    n = tab.shape[1]
    for k in range(n - 1):
        if a <= tab[m, k + 1, 1]:
            s0, a0, s1, a1 = tab[m, k, 0], tab[m, k, 1], tab[m, k + 1, 0], tab[m, k + 1, 1]
            H = (s1 - s0) / (a1 - a0)
            return s0 + H * (a - a0), H
    return tab[m, n - 1, 0], 0.0


@nb.njit(cache=True)
def internal(X, L0, wt, zs, dzs, Es, mid, tab, ep, alpha, f, Nn, Mn, commit, eprev, kprev, beta_dt, EA, EI):
    n = X.shape[0]
    ns = n - 1
    eps_s = np.empty(ns)
    phi = np.empty(ns)
    ex = np.empty(ns)
    ey = np.empty(ns)
    ln = np.empty(ns)
    for s in range(ns):
        dx = X[s + 1, 0] - X[s, 0]
        dy = X[s + 1, 1] - X[s, 1]
        l = math.sqrt(dx * dx + dy * dy)
        ln[s] = l
        ex[s] = dx
        ey[s] = dy
        eps_s[s] = l / L0[s] - 1.0
        phi[s] = math.atan2(dy, dx)
    for i in range(n):
        f[i, 0] = 0.0
        f[i, 1] = 0.0
    nf = zs.shape[0]
    for i in range(n):
        # generalized strains at node i
        if i == 0:
            e = eps_s[0]
        elif i == n - 1:
            e = eps_s[ns - 1]
        else:
            e = 0.5 * (eps_s[i - 1] + eps_s[i])
        k = 0.0
        if 0 < i < n - 1:
            d = phi[i] - phi[i - 1]
            while d > math.pi:
                d -= 2 * math.pi
            while d < -math.pi:
                d += 2 * math.pi
            k = d / wt[i]
        N = 0.0
        M = 0.0
        for q in range(nf):
            m = mid[q]
            eps = e - k * zs[q]
            sig = Es[q] * (eps - ep[i, q])
            sy, H = yield_stress(tab, m, alpha[i, q])
            fy = abs(sig) - sy
            if fy > 0:
                dg = fy / (Es[q] + H)
                sgn = 1.0 if sig > 0 else -1.0
                sig -= Es[q] * dg * sgn
                if commit:
                    ep[i, q] += dg * sgn
                    alpha[i, q] += dg
            N += sig * dzs[q]
            M -= sig * zs[q] * dzs[q]
        if beta_dt > 0:
            N += EA * (e - eprev[i]) * beta_dt
            M += EI * (k - kprev[i]) * beta_dt
        eprev[i] = e
        kprev[i] = k
        Nn[i] = N
        Mn[i] = M
        # axial: d eps_i = 0.5 (d eps_{i-1} + d eps_i)  (ends: the single segment)
        if i == 0:
            segs = (0, 0)
            ws = (1.0, 0.0)
        elif i == n - 1:
            segs = (ns - 1, ns - 1)
            ws = (1.0, 0.0)
        else:
            segs = (i - 1, i)
            ws = (0.5, 0.5)
        for kk in range(2):
            s = segs[kk]
            w = ws[kk]
            if w == 0.0:
                continue
            c = N * wt[i] * w / (L0[s] * ln[s])
            f[s + 1, 0] += c * ex[s]
            f[s + 1, 1] += c * ey[s]
            f[s, 0] -= c * ex[s]
            f[s, 1] -= c * ey[s]
        if 0 < i < n - 1:
            # d kappa = (d phi_i - d phi_{i-1}) / wt ; M * wt * d kappa = M (d phi_i - d phi_{i-1})
            for kk in range(2):
                s = i if kk == 0 else i - 1
                sgn = 1.0 if kk == 0 else -1.0
                l2 = ln[s] * ln[s]
                gx = -ey[s] / l2
                gy = ex[s] / l2
                f[s + 1, 0] += sgn * M * gx
                f[s + 1, 1] += sgn * M * gy
                f[s, 0] -= sgn * M * gx
                f[s, 1] -= sgn * M * gy
    return f


@nb.njit(cache=True)
def tool_contact(X, V, rc, P, seg_tool, tool_vel, convex, kn, mu, vreg, fc, Fsum, gapmin):
    """penalty contact of strip discs against all tool segments. P: (nseg, 4) x0,y0,x1,y1 (current positions).
    convex[s]: 1 if the start vertex of segment s is a convex corner (then vertex contact is checked there)."""
    n = X.shape[0]
    nseg = P.shape[0]
    for i in range(n):
        for s in range(nseg):
            x0 = P[s, 0]
            y0 = P[s, 1]
            dx = P[s, 2] - x0
            dy = P[s, 3] - y0
            L2 = dx * dx + dy * dy
            px = X[i, 0] - x0
            py = X[i, 1] - y0
            t = (px * dx + py * dy) / L2
            L = math.sqrt(L2)
            nx = dy / L          # outward (right) normal
            ny = -dx / L
            if 0.0 <= t <= 1.0:
                d = px * nx + py * ny
                if d < rc and d > -rc:
                    g = rc - d
                    gx, gy = nx, ny
                else:
                    continue
            elif t < 0.0 and convex[s] == 1:
                d = math.sqrt(px * px + py * py)
                if d < rc and d > 1e-12 and (px * nx + py * ny) > 0:
                    g = rc - d
                    gx, gy = px / d, py / d
                else:
                    continue
            else:
                continue
            if g > rc:
                continue
            Fn = kn * g
            tv = seg_tool[s]
            rvx = V[i, 0] - tool_vel[tv, 0]
            rvy = V[i, 1] - tool_vel[tv, 1]
            vt = rvx * (-gy) + rvy * gx
            Ft = -mu * Fn * math.tanh(vt / vreg)
            fx = Fn * gx - Ft * gy
            fy = Fn * gy + Ft * gx
            fc[i, 0] += fx
            fc[i, 1] += fy
            Fsum[tv, 0] -= fx
            Fsum[tv, 1] -= fy
            if rc - g < gapmin[0]:
                gapmin[0] = rc - g


@nb.njit(cache=True)
def self_contact(X, V, rc, pairs, npairs, kn, mu, vreg, fc):
    for p in range(npairs):
        i = pairs[p, 0]
        s = pairs[p, 1]
        x0 = X[s, 0]
        y0 = X[s, 1]
        dx = X[s + 1, 0] - x0
        dy = X[s + 1, 1] - y0
        L2 = dx * dx + dy * dy
        px = X[i, 0] - x0
        py = X[i, 1] - y0
        t = (px * dx + py * dy) / L2
        if t < 0.0:
            t = 0.0
        if t > 1.0:
            t = 1.0
        qx = px - t * dx
        qy = py - t * dy
        d = math.sqrt(qx * qx + qy * qy)
        if d < 2 * rc and d > 1e-12:
            g = 2 * rc - d
            gx = qx / d
            gy = qy / d
            Fn = kn * g
            vsx = (1 - t) * V[s, 0] + t * V[s + 1, 0]
            vsy = (1 - t) * V[s, 1] + t * V[s + 1, 1]
            rvx = V[i, 0] - vsx
            rvy = V[i, 1] - vsy
            vt = rvx * (-gy) + rvy * gx
            Ft = -mu * Fn * math.tanh(vt / vreg)
            fx = Fn * gx - Ft * gy
            fy = Fn * gy + Ft * gx
            fc[i, 0] += fx
            fc[i, 1] += fy
            fc[s, 0] -= (1 - t) * fx
            fc[s, 1] -= (1 - t) * fy
            fc[s + 1, 0] -= t * fx
            fc[s + 1, 1] -= t * fy


@nb.njit(cache=True)
def build_pairs(X, rc, skip, pairs):
    n = X.shape[0]
    m = 0
    lim = (2 * rc + 0.25) ** 2
    for i in range(n):
        for s in range(n - 1):
            if abs(i - s) <= skip or abs(i - s - 1) <= skip:
                continue
            dx = 0.5 * (X[s, 0] + X[s + 1, 0]) - X[i, 0]
            dy = 0.5 * (X[s, 1] + X[s + 1, 1]) - X[i, 1]
            if dx * dx + dy * dy < lim:
                if m < pairs.shape[0]:
                    pairs[m, 0] = i
                    pairs[m, 1] = s
                    m += 1
    return m


class Tool:
    def __init__(self, name, pts, motion=None):
        """pts: polyline (material on the left). motion(t) -> (dx, dy) offset from the drawn position."""
        self.name = name
        self.pts = np.array(pts, float)
        self.motion = motion or (lambda t: (0.0, 0.0))


def convex_flags(pts):
    """1 at vertex k (start of segment k) if the turn there is convex as seen from outside (right side)."""
    n = len(pts)
    flags = np.zeros(n - 1, dtype=np.int64)
    flags[0] = 1
    for k in range(1, n - 1):
        a = pts[k] - pts[k - 1]
        b = pts[k + 1] - pts[k]
        cr = a[0] * b[1] - a[1] * b[0]
        flags[k] = 1 if cr > 1e-12 else 0     # left turn = convex for material on the left
    return flags


class Sim:
    def __init__(self, X0, layers, tools, mass_scale=1e4, kn=2e4, mu=0.15, vreg=1.0, damping=20.0, self_contact=True):
        self.X = np.array(X0, float)
        n = len(self.X)
        self.V = np.zeros_like(self.X)
        self.T, self.zs, self.dzs, self.Es, self.mid, self.tab, rhoA = section(layers)
        self.rc = self.T / 2
        seg = np.diff(self.X, axis=0)
        self.L0 = np.linalg.norm(seg, axis=1)
        self.wt = np.zeros(n)
        self.wt[:-1] += self.L0 / 2
        self.wt[1:] += self.L0 / 2
        self.m = rhoA * self.wt * mass_scale
        nf = len(self.zs)
        self.ep = np.zeros((n, nf))
        self.alpha = np.zeros((n, nf))
        self.f = np.zeros_like(self.X)
        self.Nn = np.zeros(n)
        self.Mn = np.zeros(n)
        self.eprev = np.zeros(n)
        self.kprev = np.zeros(n)
        self.EA = float(np.sum(self.Es * self.dzs))
        self.EI = float(np.sum(self.Es * self.zs ** 2 * self.dzs))
        self.beta = 0.0           # stiffness-proportional damping time (s); set to ~0.5 dt
        self.tools = tools
        self.kn, self.mu, self.vreg, self.c = kn, mu, vreg, damping
        self.do_self = self_contact
        self.pairs = np.zeros((40000, 2), dtype=np.int64)
        self.npairs = 0
        self.fixed = {}           # node -> function t -> (x, y) or None per component
        self.fext = np.zeros_like(self.X)   # external nodal loads (can be a function of t via self.fext_fn)
        self.fext_fn = None
        self.t = 0.0
        segs, owner, conv = [], [], []
        for k, tl in enumerate(tools):
            for j in range(len(tl.pts) - 1):
                segs.append((j, k))
            conv.append(convex_flags(tl.pts))
        self.seg_index = segs
        self.seg_tool = np.array([k for j, k in segs], dtype=np.int64)
        self.convex = np.concatenate(conv) if conv else np.zeros(0, dtype=np.int64)
        self.P = np.zeros((len(segs), 4))
        self.Ftool = np.zeros((len(tools), 2))

    def tool_state(self, t, dt):
        vel = np.zeros((len(self.tools), 2))
        for k, tl in enumerate(self.tools):
            a = np.array(tl.motion(t))
            b = np.array(tl.motion(t + dt))
            vel[k] = (b - a) / dt
        j = 0
        for k, tl in enumerate(self.tools):
            off = np.array(tl.motion(t))
            p = tl.pts + off
            for s in range(len(p) - 1):
                self.P[j, :2] = p[s]
                self.P[j, 2:] = p[s + 1]
                j += 1
        return vel

    def stable_dt(self):
        E = self.Es.max()
        A = self.T
        I = self.T ** 3 / 12
        l = self.L0.min()
        mpl = self.m.min() / self.wt[np.argmin(self.m)]
        w_ax = 2 * math.sqrt(E * A / l / (self.m.min()))
        w_b = 4 * math.sqrt(E * I / mpl) / l ** 2
        w_c = 2 * math.sqrt(self.kn * 2 / self.m.min())
        return 0.8 * 2 / max(w_ax, w_b, w_c)

    def run(self, t_end, dt=None, record_every=None, callback=None):
        dt = dt or self.stable_dt()
        nsteps = int(math.ceil((t_end - self.t) / dt))
        rec = []
        fc = np.zeros_like(self.X)
        Fsum = np.zeros((len(self.tools), 2))
        Fmax = np.zeros((len(self.tools), 2))
        gapmin = np.array([1e9])
        hist = []
        for step in range(nsteps):
            t = self.t
            vel = self.tool_state(t, dt)
            internal(self.X, self.L0, self.wt, self.zs, self.dzs, self.Es, self.mid, self.tab, self.ep, self.alpha, self.f, self.Nn, self.Mn, True, self.eprev, self.kprev, self.beta / dt, self.EA, self.EI)
            fc[:] = 0.0
            Fsum[:] = 0.0
            tool_contact(self.X, self.V, self.rc, self.P, self.seg_tool, vel, self.convex, self.kn, self.mu, self.vreg, fc, Fsum, gapmin)
            if self.do_self:
                if step % 20 == 0:
                    self.npairs = build_pairs(self.X, self.rc, int(math.ceil(3 * self.rc / self.L0.min())) + 2, self.pairs)
                self_contact(self.X, self.V, self.rc, self.pairs, self.npairs, self.kn, self.mu, self.vreg, fc)
            fe = self.fext_fn(t) if self.fext_fn else self.fext
            a = (fc + fe - self.f) / self.m[:, None] - self.c * self.V
            self.V += a * dt
            for i, fn in self.fixed.items():
                tgt = fn(t + dt)
                for c in (0, 1):
                    if tgt[c] is not None:
                        self.V[i, c] = (tgt[c] - self.X[i, c]) / dt
            self.X += self.V * dt
            self.t += dt
            Fmax = np.maximum(Fmax, np.abs(Fsum))
            if record_every and step % record_every == 0:
                hist.append((self.t, Fsum.copy()))
                rec.append((self.t, self.X.copy()))
            if callback and step % 2000 == 0:
                callback(self, step, nsteps)
        return rec, hist, Fmax


@nb.njit(cache=True)
def build_tool_pairs(X, P, rc, margin, tpairs):
    n = X.shape[0]
    nseg = P.shape[0]
    m = 0
    lim = rc + margin
    for s in range(nseg):
        x0 = min(P[s, 0], P[s, 2]) - lim
        x1 = max(P[s, 0], P[s, 2]) + lim
        y0 = min(P[s, 1], P[s, 3]) - lim
        y1 = max(P[s, 1], P[s, 3]) + lim
        for i in range(n):
            if X[i, 0] < x0 or X[i, 0] > x1 or X[i, 1] < y0 or X[i, 1] > y1:
                continue
            if m < tpairs.shape[0]:
                tpairs[m, 0] = i
                tpairs[m, 1] = s
                m += 1
    return m


@nb.njit(cache=True)
def tool_contact_pairs(X, V, rc, P, seg_tool, tool_vel, convex, kn, mu, vreg, fc, Fsum, tpairs, ntp):
    for p in range(ntp):
        i = tpairs[p, 0]
        s = tpairs[p, 1]
        x0 = P[s, 0]
        y0 = P[s, 1]
        dx = P[s, 2] - x0
        dy = P[s, 3] - y0
        L2 = dx * dx + dy * dy
        px = X[i, 0] - x0
        py = X[i, 1] - y0
        t = (px * dx + py * dy) / L2
        L = math.sqrt(L2)
        nx = dy / L
        ny = -dx / L
        if 0.0 <= t <= 1.0:
            d = px * nx + py * ny
            if d < rc and d > -rc:
                g = rc - d
                gx, gy = nx, ny
            else:
                continue
        elif t < 0.0 and convex[s] == 1:
            d = math.sqrt(px * px + py * py)
            if d < rc and d > 1e-12 and (px * nx + py * ny) > 0:
                g = rc - d
                gx, gy = px / d, py / d
            else:
                continue
        else:
            continue
        Fn = kn * g
        tv = seg_tool[s]
        rvx = V[i, 0] - tool_vel[tv, 0]
        rvy = V[i, 1] - tool_vel[tv, 1]
        vt = rvx * (-gy) + rvy * gx
        Ft = -mu * Fn * math.tanh(vt / vreg)
        fx = Fn * gx - Ft * gy
        fy = Fn * gy + Ft * gx
        fc[i, 0] += fx
        fc[i, 1] += fy
        Fsum[tv, 0] -= fx
        Fsum[tv, 1] -= fy


# ------------------------------------------------------------------------------------------------ fully compiled loop
@nb.njit(cache=True)
def interp_tab(tab, t, out):
    """tab: (k, 3) rows (time, a, b), piecewise linear, clamped."""
    k = tab.shape[0]
    if t <= tab[0, 0]:
        out[0] = tab[0, 1]
        out[1] = tab[0, 2]
        return
    for j in range(k - 1):
        if t <= tab[j + 1, 0]:
            w = (t - tab[j, 0]) / (tab[j + 1, 0] - tab[j, 0])
            out[0] = tab[j, 1] + w * (tab[j + 1, 1] - tab[j, 1])
            out[1] = tab[j, 2] + w * (tab[j + 1, 2] - tab[j, 2])
            return
    out[0] = tab[k - 1, 1]
    out[1] = tab[k - 1, 2]


@nb.njit(cache=True)
def run_jit(X, V, m, L0, wt, zs, dzs, Es, mid, tab, ep, alpha, eprev, kprev, EA, EI,
            P0, seg_tool, convex, ttabs, fix_idx, fix_tabs, fext, fext_ramp,
            kn, mu, vreg, c, beta, rc, do_self, t0, dt, nsteps, rec_every, recX, recF, recT):
    n = X.shape[0]
    nt = ttabs.shape[0]
    nseg = P0.shape[0]
    f = np.zeros((n, 2))
    fc = np.zeros((n, 2))
    Nn = np.zeros(n)
    Mn = np.zeros(n)
    P = np.zeros((nseg, 4))
    vel = np.zeros((nt, 2))
    Fsum = np.zeros((nt, 2))
    gapmin = np.array([1e9])
    off = np.zeros(2)
    off2 = np.zeros(2)
    pairs = np.zeros((60000, 2), dtype=np.int64)
    npairs = 0
    tpairs = np.zeros((400000, 2), dtype=np.int64)
    ntp = 0
    skip = int(math.ceil(3 * rc / L0.min())) + 2
    r = 0
    t = t0
    for step in range(nsteps):
        # tools
        for k in range(nt):
            interp_tab(ttabs[k], t, off)
            interp_tab(ttabs[k], t + dt, off2)
            vel[k, 0] = (off2[0] - off[0]) / dt
            vel[k, 1] = (off2[1] - off[1]) / dt
        for s in range(nseg):
            k = seg_tool[s]
            interp_tab(ttabs[k], t, off)
            P[s, 0] = P0[s, 0] + off[0]
            P[s, 1] = P0[s, 1] + off[1]
            P[s, 2] = P0[s, 2] + off[0]
            P[s, 3] = P0[s, 3] + off[1]
        internal(X, L0, wt, zs, dzs, Es, mid, tab, ep, alpha, f, Nn, Mn, True, eprev, kprev, beta / dt, EA, EI)
        for i in range(n):
            fc[i, 0] = 0.0
            fc[i, 1] = 0.0
        for k in range(nt):
            Fsum[k, 0] = 0.0
            Fsum[k, 1] = 0.0
        if step % 25 == 0:
            ntp = build_tool_pairs(X, P, rc, 0.15, tpairs)
        tool_contact_pairs(X, V, rc, P, seg_tool, vel, convex, kn, mu, vreg, fc, Fsum, tpairs, ntp)
        if do_self:
            if step % 20 == 0:
                npairs = build_pairs(X, rc, skip, pairs)
            self_contact(X, V, rc, pairs, npairs, kn, mu, vreg, fc)
        ramp = 1.0
        if fext_ramp > 0:
            ramp = min(1.0, (t - t0) / fext_ramp)
        for i in range(n):
            for d in range(2):
                a = (fc[i, d] + ramp * fext[i, d] - f[i, d]) / m[i] - c * V[i, d]
                V[i, d] += a * dt
        for j in range(fix_idx.shape[0]):
            i = fix_idx[j]
            interp_tab(fix_tabs[j], t + dt, off)
            if not math.isnan(off[0]):
                V[i, 0] = (off[0] - X[i, 0]) / dt
            if not math.isnan(off[1]):
                V[i, 1] = (off[1] - X[i, 1]) / dt
        for i in range(n):
            X[i, 0] += V[i, 0] * dt
            X[i, 1] += V[i, 1] * dt
        t += dt
        if rec_every > 0 and step % rec_every == 0 and r < recX.shape[0]:
            for i in range(n):
                recX[r, i, 0] = X[i, 0]
                recX[r, i, 1] = X[i, 1]
            for k in range(nt):
                recF[r, k, 0] = Fsum[k, 0]
                recF[r, k, 1] = Fsum[k, 1]
            recT[r] = t
            r += 1
    return t, r


def table(points):
    """[(t, a, b), ...] -> array; None -> nan."""
    return np.array([[p[0], np.nan if p[1] is None else p[1], np.nan if p[2] is None else p[2]] for p in points], float)


def run_fast(sim, t_end, ttabs, fixes, dt=None, rec_every=200, fext_ramp=0.0):
    """ttabs: list of per-tool motion tables (same order as sim.tools); fixes: {node: table}."""
    dt = dt or sim.stable_dt()
    nsteps = int(math.ceil((t_end - sim.t) / dt))
    P0 = np.zeros((len(sim.seg_tool), 4))
    j = 0
    for tl in sim.tools:
        for s in range(len(tl.pts) - 1):
            P0[j, :2] = tl.pts[s]
            P0[j, 2:] = tl.pts[s + 1]
            j += 1
    kmax = max(len(t) for t in ttabs) if ttabs else 1
    TT = np.zeros((max(1, len(ttabs)), kmax, 3))
    for k, tb in enumerate(ttabs):
        TT[k, :len(tb)] = tb
        TT[k, len(tb):] = tb[-1]
        TT[k, len(tb):, 0] = tb[-1, 0] + np.arange(1, kmax - len(tb) + 1)
    fidx = np.array(sorted(fixes), dtype=np.int64)
    fmax = max([len(fixes[i]) for i in fixes] + [1])
    FT = np.zeros((max(1, len(fidx)), fmax, 3))
    for j, i in enumerate(fidx):
        tb = fixes[i]
        FT[j, :len(tb)] = tb
        FT[j, len(tb):] = tb[-1]
        FT[j, len(tb):, 0] = tb[-1, 0] + np.arange(1, fmax - len(tb) + 1)
    nrec = nsteps // rec_every + 2
    recX = np.zeros((nrec, len(sim.X), 2))
    recF = np.zeros((nrec, max(1, len(sim.tools)), 2))
    recT = np.zeros(nrec)
    seg_tool = sim.seg_tool if len(sim.seg_tool) else np.zeros(0, dtype=np.int64)
    t, r = run_jit(sim.X, sim.V, sim.m, sim.L0, sim.wt, sim.zs, sim.dzs, sim.Es, sim.mid, sim.tab, sim.ep, sim.alpha,
                   sim.eprev, sim.kprev, sim.EA, sim.EI, P0, seg_tool, sim.convex.astype(np.int64), TT, fidx, FT,
                   sim.fext, fext_ramp, sim.kn, sim.mu, sim.vreg, sim.c, sim.beta, sim.rc, sim.do_self, sim.t, dt, nsteps,
                   rec_every, recX, recF, recT)
    sim.t = t
    return recT[:r], recX[:r], recF[:r]
