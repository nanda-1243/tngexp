"""Stress maps of the crown, base plate and lever runs (crown.frd, base.frd, lever.frd) -> fea_frame.png."""
import sys

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

import fea  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else 'fea_frame.png'


def load(job):
    U, S = fea.read_results(job + '.frd')
    P = {}
    f = open(job + '.inp')
    for l in f:
        if l.startswith('*NODE'):
            break
    for l in f:
        if l.startswith('*'):
            break
        a = l.split(',')
        P[int(a[0])] = np.array([float(x) for x in a[1:4]])
    return P, {n: fea.mises(s) for n, s in S.items()}


fig, axs = plt.subplots(1, 3, figsize=(15, 5.2))
runs = [('crown', 176.0, 'Crown MP-108, underside (z 176), 16 kN'), ('base', 18.0, 'Base plate MP-101, top face (z 18), 16 kN'),
        ('lever', -10.0, 'Handle lever MP-113, face, 500 N lean')]
for ax, (job, zf, title) in zip(axs, runs):
    P, vm = load(job)
    ns = [n for n in vm if abs(P[n][2] - zf) < 1e-3]
    x = np.array([P[n][0] for n in ns]); y = np.array([P[n][1] for n in ns]); c = np.array([min(vm[n], 160) for n in ns])
    sc = ax.scatter(x, y, c=c, s=2, cmap='turbo', vmin=0, vmax=160)
    ax.set_aspect('equal'); ax.set_title(title, fontsize=10); ax.set_xlabel('x, mm'); ax.set_ylabel('y, mm')
    if job == 'base':
        ax.set_xlim(x.min() - 10, x.max() + 10); ax.set_ylim(y.min() - 10, y.max() + 10)
    if job == 'lever':
        ax.set_xlim(-30, 390)
fig.colorbar(sc, ax=axs, shrink=0.8, label='von Mises stress, MPa (capped at 160)')
fig.savefig(out, dpi=110, bbox_inches='tight')
print('ok', out)
