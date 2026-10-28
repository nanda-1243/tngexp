"""Stroke-1 carrier check from a stroke1x run: upper-ring force per mm along the fold, carrier give and plug clearance
for each square kit (upper springs 8 x 24.6 N/mm, 1574 N preload; ring A springs 75 N + 38 N/mm from 2.4 mm before the fold)."""
import sys, pickle, numpy as np
s = lambda u: u * u * (3 - 2 * u)
for job in sys.argv[1:]:
    d = pickle.load(open(job + '.pkl', 'rb'))
    T1 = d['times'][0]; trav = d['travel']; t = d['recT']; F = d['recF']
    p = np.where(t <= T1, trav * s(np.clip(t / T1, 0, 1)), trav)
    k = max(1, int(0.01 / (t[1] - t[0])))
    fu = np.abs(np.convolve(F[:, 1, 1], np.ones(k) / k, mode='same'))
    m = (t < T1 * 0.97)
    i = np.argmax(fu * m)
    print('%s: mouth R%.1f mu %.2f  peak %.2f N/mm at pedestal %.2f; mean %.2f; end %.2f; wall end at x %.2f'
          % (job, d['mouth_r'], d['mu'], fu[i], p[i], fu[m].mean(), fu[np.searchsorted(t, T1) - 5], d['X'][-1, 0]))
    for X, Z, cd in [(50, 50, '5050'), (63.5, 63.5, '6363'), (80, 53, '5380'), (90, 65, '6590')]:
        per = 2 * (X + Z) - 8 + 2 * np.pi
        ra = 75 + 305 * np.minimum(8, 2.4 + p) / 8
        g = np.maximum(0, (fu * per + ra - 1574.4) / 196.8)
        clear = 5.5 - p - g
        sel = m & (g > 0)
        print('   %s  max give %.2f mm, min plug clearance while giving %s' % (cd, g[m].max(), ('%.2f mm' % clear[sel].min()) if sel.any() else 'n/a (no give)'))
