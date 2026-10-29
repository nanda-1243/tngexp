"""MagPress L1: kinematics, hand force, springs and strength. Prints a report (light/results.txt).

Run:  python light/calcs.py [fold1_N_per_mm] [fold2_N_per_mm]
fold1 / fold2: peak forming force per mm of magnet edge for stroke 1 and stroke 2, from the 2D forming runs
(verify/stroke1x.py and verify/stroke2L.py). Defaults: 8.3 (stroke 1, 7.1 recess) and a 4 N/mm stroke-2 allowance.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l1 as G   # noqa: E402

F1 = float(sys.argv[1]) if len(sys.argv) > 1 else 8.3
F2 = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
EDGE = 4 * G.FACE                       # 254 mm of edge
ETA = 0.85                              # pin friction in the toggle
L_H = G.GRIP_C
out = []


def p(s=''):
    out.append(s)


def hr(t):
    p(''); p('=' * 100); p(t); p('=' * 100)


hr('1. TOGGLE AND STROKE')
p('Crank O-A %g, link A-B %g, pivot O at Z %g. Crank angle on the stop %.2f deg, handle up %g deg.' % (G.R_CRANK, G.L_LINK, G.Z_O, G.THETA_STOP, G.THETA_UP))
p('Ram stroke %.2f mm. Handle from %+.1f deg (up) to %+.1f deg (on the stop), grip centre %g mm from O.'
  % (G.STROKE, G.handle_angle(G.THETA_UP), G.handle_angle(G.THETA_STOP), L_H))
p('Handle stop: 2 x M8 bolts in the head at X %g, Y +-12, tip at Z %.2f (%.2f above the head). 1 deg of stop = %.3f mm of plug height.'
  % (G.STOP_X, G.STOP_Z, G.STOP_Z - G.Z_HEAD - G.HEAD_T, G.dB_dtheta(G.THETA_STOP) * math.pi / 180))
p()
p(' crank deg   ram down mm   dB/dtheta mm/rad   ram force kN per 100 N on the grip')
for th in (70, 60, 50, 40, 35, 30, 25, 20, 15, G.THETA_STOP):
    down = G.drop(th) - G.drop(G.THETA_UP)
    k = G.dB_dtheta(th)
    p('   %5.1f       %6.2f          %6.2f              %6.2f' % (th, down, k, 100 * L_H * ETA / k / 1000))


def theta_at_up(x):
    """crank angle with the ram x mm above the bottom of the stroke."""
    return G.theta_for_drop(G.drop(G.THETA_STOP) - x)


hr('2. FORCES AND HAND FORCE')
up = G.UP_SPR
ra = G.RA_SPR
k_up, k_ra = up['n'] * up['k'], ra['n'] * ra['k']
p('Upper ring springs: %d x ISO 10243 red D%g x %g, about %g N/mm each; installed %g, preload %g mm = %.2f kN;'
  % (up['n'], up['d'], up['L0'], up['k'], up['inst'], up['pre'], k_up * up['pre'] / 1000))
p('  at stroke 2 (ring retracted %.1f): %.1f mm = %.1f%% of free length (red: 25%% max), %.2f kN.'
  % (G.RECESS, up['pre'] + G.RECESS, 100 * (up['pre'] + G.RECESS) / up['L0'], k_up * (up['pre'] + G.RECESS) / 1000))
p('Ring A springs: %d x ISO 10243 green D%g x %g, about %g N/mm; preload %g mm, %.1f mm = %.0f%% at the stop (green: 40%% max).'
  % (ra['n'], ra['d'], ra['L0'], ra['k'], ra['pre'], ra['pre'] + G.RA_TRAVEL, 100 * (ra['pre'] + G.RA_TRAVEL) / ra['L0']))
f1 = F1 * EDGE / 1000
f2 = F2 * EDGE / 1000
p()
p('Stroke 1 fold (2D model, peak %.1f N/mm x %g mm of edge): %.2f kN; plus ring A springs up to %.2f kN.'
  % (F1, EDGE, f1, k_ra * (ra['pre'] + G.RA_TRAVEL) / 1000))
need = f1 + k_ra * (ra['pre'] + G.RA_TRAVEL) / 1000
p('  The upper ring must not lift: preload %.2f kN against %.2f kN -> margin %.0f%%.' % (k_up * up['pre'] / 1000, need, 100 * (k_up * up['pre'] / 1000 / need - 1)))
p('Stroke 2 (2D model): the turn-in takes little force until the face meets the card; allowance %.1f N/mm = %.2f kN on top of the upper springs.' % (F2, f2))
p()
p(' station  ram above the bottom  crank deg  force at the die kN  hand force N (grip at %g, 85%% efficiency)' % L_H)
worst = 0.0
for st in ('A', 'B'):
    for x in ([G.RA_TRAVEL * f for f in (1.0, 0.75, 0.5, 0.25, 0.0)] if st == 'A' else [G.RECESS * f for f in (1.0, 0.75, 0.5, 0.25, 0.0)]):
        th = theta_at_up(x)
        if st == 'A':
            s = (G.RA_TRAVEL - x) / G.RA_TRAVEL
            F = f1 * min(1.0, 2.2 * s) * (1.0 if s < 0.6 else max(0.25, 1 - (s - 0.6) * 1.8)) + k_ra * (ra['pre'] + G.RA_TRAVEL - x) / 1000
        else:
            r = G.RECESS - x
            F = k_up * (up['pre'] + r) / 1000 + f2 * min(1.0, 1.6 * r / G.RECESS)
        F += 2 * G.RET_SPR['k'] * (G.RET_SPR['L0'] - (G.Z_RAM + x - G.Z_SEAT)) / 1000      # return springs (weights ignored)
        hf = F * 1000 * G.dB_dtheta(th) / (L_H * ETA)
        worst = max(worst, hf)
        p('   %s          %5.2f             %5.1f        %5.2f             %5.0f' % (st, x, th, F, hf))
p('Highest hand force about %.0f N (%.0f kg on the grip).' % (worst, worst / 9.81))
p('Includes the two return springs; the weight of the ram and lever (which helps) is ignored. Stroke-1 force shape over the')
p('travel from the 2D run: rises to the peak in the first 40%, falls to about 25% at the end.')

hr('3. RETURN SPRINGS AND WEIGHT ON THE HANDLE')
rs = G.RET_SPR
L_up = G.Z_RAM_UP - G.Z_SEAT
L_dn = G.Z_RAM - G.Z_SEAT
p('2 x compression springs ID %g, wire %g, L0 %g, rate about %g N/mm on the columns, seated on collars (top at Z %g).'
  % (rs['id'], rs['wire'], rs['L0'], rs['k'], G.Z_SEAT))
p('Installed %.1f (handle up) -> %.1f (stop): %.0f N -> %.0f N each.' % (L_up, L_dn, rs['k'] * (rs['L0'] - L_up), rs['k'] * (rs['L0'] - L_dn)))
m_ram = 1.99 + 0.95 + 0.76 + 0.47 + 0.15 + 0.21 + 0.2 + 0.1 + 0.4      # ram, die body, upper ring, plug, clevis, link, screws, bushes, springs
m_lever = 2 * 0.86 + 0.40 + 0.08 + 0.15
cg = 210.0
th = G.THETA_UP
lever_eq = m_lever * 9.81 * cg * math.cos(math.radians(G.handle_angle(th))) / G.dB_dtheta(th)
lift = 2 * rs['k'] * (rs['L0'] - L_up)
p('Ram side about %.1f kg (%.0f N); lever about %.1f kg, CG about %g from O: %.0f N at the ram with the handle up.'
  % (m_ram, m_ram * 9.81, m_lever, cg, lever_eq))
p('Spring lift with the handle up %.0f N against %.0f N: margin %.0f%% (the handle stays up by itself).' % (lift, m_ram * 9.81 + lever_eq, 100 * (lift / (m_ram * 9.81 + lever_eq) - 1)))

hr('4. STRENGTH AT THE 15 kN ABUSE LOAD (200 N leaning on the grip at the stop)')
Fab = 15000.0
span = 2 * G.COL_Y
net = G.HEAD_W - (G.HEAD_SLOT['x1'] - G.HEAD_SLOT['x0'])
Zh = net * G.HEAD_T ** 2 / 6
p('Head: S275 %gx%g, window %g long -> %g net, M = F L / 4 = %.0f N.m, %.0f MPa (yield 275).' % (G.HEAD_W, G.HEAD_T, G.HEAD_SLOT['x1'] - G.HEAD_SLOT['x0'], net, Fab * span / 4 / 1000, Fab * span / 4 / Zh))
dsh = 0.55 * 1.0
Zp = math.pi * G.PIN_D ** 3 / 32
arm = G.LEVER_T / 2 + (G.CHEEK_Y[0] - G.LEVER_Y[1]) + G.CHEEK['T'] / 2
p('Stub pins O (2 x D%g, single shear): bending about %.0f MPa, shear %.0f MPa (EN8 Re 430).' % (G.PIN_D, Fab / 2 * arm / 2 / Zp, Fab / 2 / (math.pi * G.PIN_D ** 2 / 4)))
p('Pins A, B (D%g, double shear, link %g between two %g plates): bending %.0f MPa, shear %.0f MPa.'
  % (G.PIN_D, G.LINK_T, G.LEVER_T, Fab / 2 * (G.LEVER_T / 2 + 0.5 + G.LINK_T / 4) / Zp, Fab / 2 / (math.pi * G.PIN_D ** 2 / 4)))
p('Link (S355, 15 thick, eyes R14): tension beside the eye %.0f MPa; bearing %.0f MPa.' % (Fab / (2 * (G.LINK_R - G.PIN_D / 2) * G.LINK_T), Fab / (G.PIN_D * G.LINK_T)))
p('Lever plates at pin A (2 x 8): bearing %.0f MPa. Cheeks (2 x 18) at pin O: bearing %.0f MPa.' % (Fab / (2 * G.PIN_D * G.LEVER_T), Fab / (2 * G.PIN_D * G.CHEEK['T'])))
p('Cheek screws: 4 x M8 8.8 carry the 15 kN lift-off: %.0f MPa in the thread (proof 580).' % (Fab / 4 / 36.6))
p('Columns D20 in tension, 7.5 kN each: %.0f MPa in the body, %.0f MPa in the M12 thread (8.8 equivalent).' % (Fab / 2 / (math.pi * 100), Fab / 2 / 84.3))
Zb = 200 * G.BASE_T ** 2 / 6
p('Base plate S275 %g (200 wide effective under the station), span %g: about %.0f MPa.' % (G.BASE_T, span, Fab / 2 * (G.COL_Y - G.ST / 4) / Zb))
p('Lever plates at the hub under 200 N x %g: %.0f MPa.' % (L_H, 200 * L_H / (2 * G.LEVER_T * G.LEVER_W ** 2 / 6)))

hr('5. STATION HEIGHTS (bottom of the stroke)')
p('Table top %g. Station A: base block %g-%g, pedestal top %.3f, ring A on its stop %g-%g, face top %.3f.'
  % (G.Z_TABLE, G.Z_TABLE, G.Z_BB, G.Z_BB + G.PED_H, G.Z_BB, G.Z_BB + G.RA_T, G.Z_BB + G.PED_H + G.T_STACK))
p('Station B: riser %g-%.3f, cup ring %.3f-%g. Plug face at %g in both; upper ring bottom %g (A) / %g (B).'
  % (G.Z_TABLE, G.Z_TABLE + G.RIS_T, G.Z_FACE - G.CUP_T, G.Z_FACE, G.Z_FACE, G.Z_BB + G.RA_T, G.Z_FACE))
p('Handle up: upper ring bottom at %.2f, %.1f above ring A and %.1f above the cup ring: the table slides under it.'
  % (G.Z_RAM_UP - G.DB_T - G.UR_GAP - G.UR_T, G.Z_RAM_UP - G.DB_T - G.UR_GAP - G.UR_T - (G.Z_RA_REST + G.RA_T),
     G.Z_RAM_UP - G.DB_T - G.UR_GAP - G.UR_T - G.Z_FACE))

txt = '\n'.join(out) + '\n'
print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.txt'), 'w').write(txt)
