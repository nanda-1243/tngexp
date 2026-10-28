"""Stroke-1 figure: upper-ring force per mm of edge against pedestal travel for the drawn and the verified tooling, the
limit for the 65 x 90 kit (plug clear of the face while the upper carrier gives), and frames of the verified fold.
python fplot1.py out.png"""
import pickle
import sys

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

import xplot as XP  # noqa: E402

s = lambda u: u * u * (3 - 2 * u)
runs = [('s1_r0', 'as drawn: lead-in 0.3 × 30°, flange trapped on ring A', '#c0392b'),
        ('s1_n_r15', 'mouth R1.5, ring A ledge 0.5', '#e69f00'),
        ('s1_m25', 'mouth R2.5, ring A ledge 0.5 (μ 0.15)', '#2a9d8f'),
        ('s1_m25_mu25', 'mouth R2.5, ring A ledge 0.5 (μ 0.25)', '#1d6fa5')]
fig = plt.figure(figsize=(15, 8.4))
ax = fig.add_axes([0.06, 0.52, 0.55, 0.42])
for job, lab, c in runs:
    d = pickle.load(open(job + '.pkl', 'rb'))
    T1 = d['times'][0]
    t = d['recT']
    p = np.where(t <= T1, d['travel'] * s(np.clip(t / T1, 0, 1)), d['travel'])
    k = max(1, int(0.01 / (t[1] - t[0])))
    f = np.abs(np.convolve(d['recF'][:, 1, 1], np.ones(k) / k, mode='same'))
    m = t < T1 * 0.98
    ax.plot(p[m], f[m], color=c, lw=1.8, label=lab)
per = 2 * (90 + 65) - 8 + 2 * np.pi
pp = np.linspace(0, 5.3, 100)
ra = 75 + 305 * np.minimum(8, 2.4 + pp) / 8
allow = (1574.4 + 196.8 * np.maximum(0, 5.5 - pp - 0.3) - ra) / per
ax.plot(pp, allow, 'k--', lw=1.2, label='limit, 65 × 90 kit: plug stays 0.3 clear of the face')
ax.plot(pp, (1574.4 - ra) / per, 'k:', lw=1.0, label='65 × 90: upper carrier starts to give')
ax.set_xlabel('pedestal travel into the upper ring, mm (ram travel ≈ 28.4 + this)')
ax.set_ylabel('force on the upper ring, N per mm of edge')
ax.set_ylim(0, 20); ax.set_xlim(0, 5.6); ax.grid(alpha=0.3); ax.legend(fontsize=8.5, loc='upper right')
ax.set_title('Stroke 1: folding the flat blank (explicit model, tin 0.20 + photo 0.12 + film 0.075)', fontsize=10)
R = pickle.load(open('s1_m25_mu25.pkl', 'rb'))
for n, tt in enumerate([0.08, 0.16, 0.26, 0.40, 0.55]):
    a = fig.add_axes([0.03 + n * 0.195, 0.04, 0.18, 0.40])
    XP.draw(a, R, tt, (-2.5, 7.0, -4.5, 6.5), 'R2.5, μ 0.25: t = %.2f s' % tt)
ax2 = fig.add_axes([0.66, 0.52, 0.32, 0.42])
R0 = pickle.load(open('s1_r0.pkl', 'rb'))
XP.draw(ax2, R0, 0.40, (-2.5, 7.0, -4.5, 6.5), 'as drawn, end of the fold: flange drawn over the ring, tail flat')
fig.savefig(sys.argv[1] if len(sys.argv) > 1 else 'stroke1.png', dpi=110)
print('ok')
