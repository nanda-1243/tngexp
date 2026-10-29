"""Insert thickness for a target hem: python tsize.py shell r_i h_c d f -> t_i
Wall length below the face corner (mid-line, from the end of the R0.8 + T/2 corner arc) from the stroke-1 shell; final
shape: corner, vertical wall down to the cove top, 90 deg round the cove (mid radius R_c - T/2), then f flat along the floor."""
import math
import pickle
import sys

import numpy as np

S = pickle.load(open(sys.argv[1] + '.pkl', 'rb'))
r_i, h_c, d, f = (float(v) for v in sys.argv[2:6])
X = S['X']
T = S['T']
i0 = int(np.argmin(np.abs(X[:, 0] + 1.3)))
L = np.linalg.norm(np.diff(X[i0:], axis=0), axis=1).sum()
Lw = L - math.pi / 2 * (0.8 + T / 2)
R_c = r_i + h_c
arc = math.pi / 2 * (R_c - T / 2)
y_it = 97.5 - 38.9 - T
y_rim = (y_it - 0.8) - (Lw - arc - f)
y_ib = y_rim - r_i + d
print('%.3f' % (y_it - y_ib))
sys.stderr.write('wall below the corner %.2f mm; cove top %.3f; insert %.2f thick; magnet %.2f thick\n'
                 % (Lw, y_rim, y_it - y_ib, T + (y_it - y_ib) + h_c + d))
