"""Stroke-2 figure: rows of frames for the Rev E double fold as drawn, the back insert in the Rev E die layout, and the
commercial-style reference. python fplot2.py out.png row:job:t1,t2,..:x0,x1,y0,y1:title ..."""
import pickle
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

import xplot as XP  # noqa: E402

rows = [r.split(':', 3) for r in sys.argv[2:]]
ncol = max(len(r[1].split(',')) for r in rows)
fig, axs = plt.subplots(len(rows), ncol, figsize=(2.3 * ncol, 3.1 * len(rows)), squeeze=False)
for i, (job, ts, lim, title) in enumerate(rows):
    R = pickle.load(open(job + '.pkl', 'rb'))
    lim = [float(v) for v in lim.split(',')]
    for j, t in enumerate(ts.split(',')):
        XP.draw(axs[i][j], R, float(t), lim, 'ram travel %.1f' % (R['trav'][min(range(len(R['taus'])), key=lambda k: abs(R['taus'][k] - float(t)))]))
        axs[i][j].tick_params(labelsize=7)
    for j in range(len(ts.split(',')), ncol):
        axs[i][j].axis('off')
    axs[i][0].annotate(title, (0, 1.16), xycoords='axes fraction', fontsize=10, fontweight='bold', ha='left')
fig.subplots_adjust(left=0.04, right=0.99, top=0.93, bottom=0.04, hspace=0.62, wspace=0.28)
fig.savefig(sys.argv[1], dpi=100)
print('ok')
