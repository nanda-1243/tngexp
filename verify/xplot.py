"""Plot frames of an explicit forming run: python xplot.py job out.png t1 t2 ... [--lim x0 x1 y0 y1]
The strip is drawn as its three layers (tin grey, paper cream, film blue) offset from the reference line."""
import math
import pickle
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import xform as XF


def interp_tab(tab, t):
    k = np.searchsorted(tab[:, 0], t)
    if k <= 0:
        return tab[0, 1:]
    if k >= len(tab):
        return tab[-1, 1:]
    w = (t - tab[k - 1, 0]) / (tab[k, 0] - tab[k - 1, 0])
    return tab[k - 1, 1:] + w * (tab[k, 1:] - tab[k - 1, 1:])


def layer_polys(X, layers, T):
    d = np.gradient(X, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    nl = np.stack([-d[:, 1], d[:, 0]], 1)
    z = -T / 2
    out = []
    for name, t in layers:
        a = X + nl * z
        b = X + nl * (z + t)
        out.append((name, np.vstack([a, b[::-1]])))
        z += t
    return out


COL = {'tin': '#7f8a96', 'paper': '#efe3c2', 'film': '#3d9be0'}


def draw(ax, R, t, lim, title=None):
    k = int(np.argmin(np.abs(R['recT'] - t)))
    X = R['recX'][k]
    for name, poly in layer_polys(X, R['layers'], R['T']):
        ax.fill(poly[:, 0], poly[:, 1], color=COL[name], lw=0)
    for (name, pts), tab in zip(R['tools'].items(), R['ttabs']):
        off = interp_tab(tab, R['recT'][k])
        p = np.array(pts) + off
        ax.plot(p[:, 0], p[:, 1], 'k-', lw=1.1)
    ax.set_aspect('equal')
    ax.set_xlim(lim[0], lim[1])
    ax.set_ylim(lim[2], lim[3])
    ax.grid(alpha=0.25)
    ax.set_title(title or 't = %.3f s' % R['recT'][k], fontsize=9)


if __name__ == '__main__':
    job, out = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    lim = None
    if '--lim' in args:
        i = args.index('--lim')
        lim = [float(v) for v in args[i + 1:i + 5]]
        args = args[:i] + args[i + 5:]
    R = pickle.load(open(job + '.pkl', 'rb'))
    ts = [float(a) for a in args] or list(np.linspace(0, R['recT'][-1], 6))
    lim = lim or [-2.5, 7.0, -1.5, 6.5]
    fig, axs = plt.subplots(1, len(ts), figsize=(3.6 * len(ts), 4.2))
    axs = np.atleast_1d(axs)
    for ax, t in zip(axs, ts):
        draw(ax, R, t, lim)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    print('saved', out)
