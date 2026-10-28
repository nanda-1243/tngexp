"""MagPress M4 - engineering calculations behind the design (Rev C).

Run:  python3 calc/engineering_calcs.py > calc/results.txt
Hand calculations only: simple beams, pin bending, static spring sizing and mass estimates.
Every number on the build-pack page and the drawings that comes from a calculation comes from here.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'cad'))
import parts as P          # lever profile (MP-113)

STEEL, AL, BRONZE, TPR = 7.85e-6, 2.70e-6, 8.80e-6, 1.20e-6   # kg/mm^3
G_ACC = 9.81

# ----------------------------------------------------------------------------------------------
# 1. Toggle kinematics (crank O->A = a, link A->B = b, crank angle phi from straight down)
# ----------------------------------------------------------------------------------------------
a, b, Oy = 40.0, 60.0, 234.5
PHI_OPEN, PHI_END, OFF = 70.0, 8.0, 5.0      # handle angle psi = phi - OFF
ETA = 0.90                                    # efficiency through the three pins
L_REV_A, L_REV_BC = 290.0, 320.0              # pivot to grip centre


def yB(phi):
    p = math.radians(phi)
    return Oy - a * math.cos(p) - math.sqrt(b * b - (a * math.sin(p)) ** 2)


def travel(phi):
    return yB(PHI_OPEN) - yB(phi)


def dyd(phi):
    """ram movement per radian of crank, mm/rad"""
    p = math.radians(phi)
    s, c = math.sin(p), math.cos(p)
    return a * s + a * a * s * c / math.sqrt(b * b - a * a * s * s)


def MA(phi, L):
    return L / dyd(phi)


def phi_for_travel(t):
    lo, hi = PHI_END, PHI_OPEN
    for _ in range(80):
        m = (lo + hi) / 2
        if travel(m) > t:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def section(title):
    print()
    print('=' * 96)
    print(title)
    print('=' * 96)


section('1. TOGGLE KINEMATICS AND FORCE AT THE DIE')
STROKE = travel(PHI_END)
print('Ram stroke                         %.2f mm' % STROKE)
print('Die contact at travel 26.0; working travel %.2f mm' % (STROKE - 26.0))
print('dy/dphi at 8 / 20 / 70 deg          %.2f / %.2f / %.2f mm/rad' % (dyd(8), dyd(20), dyd(70)))
for L, tag in ((L_REV_A, 'Rev A (L 290)'), (L_REV_BC, 'Rev B/C (L 320)')):
    print('%-16s MA open %.1f, MA end %.1f; force at 200 N %.2f kN; at 500 N lean %.1f kN'
          % (tag, MA(PHI_OPEN, L), MA(PHI_END, L), 200 * ETA * MA(PHI_END, L) / 1000, 500 * ETA * MA(PHI_END, L) / 1000))
print('Pickup stops at travel 34.2 (Rev E: pedestal 23.0, the plug meets the face as ring A reaches its stop) -> handle angle %.1f deg' % (phi_for_travel(34.2) - OFF))
print('Station pilot (tip 84 below the ram, table top at 30, ram bottom at 134 open): enters the table at travel %.1f mm'
      % (134 - 84 - 30))
print()
print(' travel mm   handle deg     MA    force kN @200 N')
for t in (0, 10, 20, 26, 30, 34.2, 38, STROKE):
    ph = phi_for_travel(t) if t > 0 else PHI_OPEN
    print('   %6.2f       %5.1f     %5.1f      %5.2f' % (t, ph - OFF, MA(ph, L_REV_BC), 200 * ETA * MA(ph, L_REV_BC) / 1000))

# ----------------------------------------------------------------------------------------------
# 2. Peak force needed per size (estimate, includes the die springs)
# ----------------------------------------------------------------------------------------------
section('2. FORCE NEEDED PER SIZE (ESTIMATE)')
SIZES = [('5050', 50, 50), ('6363', 63.5, 63.5), ('5380', 80, 53), ('6590', 90, 65)]
print('Basis: 7 N per mm of shell edge (scaled from the round-badge figures in US 4,696,086) x 2.2 for the final crimp. Prove it on the prototype.')
# Rev E (independent review): at the stop the toggle also pushes against the upper die springs and the two return springs
# (2 x 245 N), and the pin friction makes the efficiency about 0.84, not 0.9. Rev E flat tin blanks: the upper springs are
# 8 x ISO 10243 D12.5 x 44 red (24.6 N/mm) in 36 mm cavities, 12.9 mm compressed at the stop (section 7).
UP_N, UP_K, UP_L0, UP_CAV = 8, 24.6, 44.0, 36.0
UP_PRE = UP_N * UP_K * (UP_L0 - UP_CAV)
UP_END = UP_N * UP_K * (UP_L0 - UP_CAV + STROKE - 26.0 - 8.0)
F_SPRINGS, ETA_END = UP_END + 2 * 245, 0.84
print('Hand force at the stop = (crimp + %.2f kN of springs) / (%.2f x MA %.1f). Rev E corners R1 (sharp-cornered magnets).' % (F_SPRINGS / 1000, ETA_END, MA(PHI_END, L_REV_BC)))
def hand_end(peak):
    return (peak + F_SPRINGS) / (ETA_END * MA(PHI_END, L_REV_BC))
for cd, X, Z in SIZES:
    r = 1.0
    perim = 2 * (X + Z) - 8 * r + 2 * math.pi * r
    peak = 2.2 * 7 * perim
    print('%s  edge %.0f mm  crimp %.2f kN  hand force at the stop %.0f N' % (cd, perim, peak / 1000, hand_end(peak)))
ROUND = [('D44', 44), ('D50', 50), ('D56', 56), ('D58', 58)]     # Rev D round kits
for cd, Dm in ROUND:
    perim = math.pi * Dm
    peak = 2.2 * 7 * perim
    print('%s  edge %.0f mm  crimp %.2f kN  hand force at the stop %.0f N' % (cd, perim, peak / 1000, hand_end(peak)))

# Rev E: the tin is a flat blank (X + 12, corners clipped 45 deg, as sold for square photo magnets). Stroke 1 folds its edges
# down round the pickup pedestal (top edge R0.8) into the upper ring (0.3 x 30 deg lead-in, about R0.3): a wiping bend. Two
# plastic hinges, M = sy t^2 / 4 per mm, over an arm of r_punch + r_die + stack (0.8 + 0.3 + 0.4), x 1.3 for friction and the
# corner gussets.
# The bend force peaks about 1.5 mm after the blank meets the pedestal (ram travel about 30, ring A 4 mm down, its springs
# about 0.23 kN). The plug is then still 4.1 mm clear of the face (it meets the face at travel 34.1), so the upper carrier may
# give up to about 2.5 mm there. Once the walls stand, only wall friction and the ring A springs (0.38 kN at its stop) are
# left, under the preload: the carrier comes back and ring A reaches its stop before the pickup stop at 34.2.
print()
print('Stroke 1, flat tin blank: fold force (wiping bend round the pedestal, tin 0.20 soft T2, sy 250 MPa; 0.22 T3, sy 300 MPa)')
FOLD_ARM = 0.8 + 0.3 + 0.4
def fold_force(perim, t, sy):
    return 1.3 * 2 * (sy * t * t / 4) / FOLD_ARM * perim
GIVE_OK, RINGA_PEAK, UP_RATE = 2.5, 75 + (380 - 75) * 4 / 8, UP_N * UP_K
def give(f):
    return max(0.0, (f + RINGA_PEAK - UP_PRE) / UP_RATE)
print('Upper springs: preload %.2f kN, %.0f N/mm. At the fold peak the carrier may give %.1f mm (plug 4.1 mm clear of the face); ring A springs %.2f kN there'
      % (UP_PRE / 1000, UP_RATE, GIVE_OK, RINGA_PEAK / 1000))
for cd, X, Z in SIZES:
    perim = 2 * (X + Z) - 8 + 2 * math.pi
    f20, f22 = fold_force(perim, 0.20, 250), fold_force(perim, 0.22, 300)
    g20, g22 = give(f20), give(f22)
    print('%s  fold 0.20: %.2f kN (+%.2f = %.2f, carrier gives %.1f mm, %s)   0.22 T3: %.2f kN (+%.2f = %.2f, gives %.1f mm, %s)'
          % (cd, f20 / 1000, RINGA_PEAK / 1000, (f20 + RINGA_PEAK) / 1000, g20, 'OK' if g20 <= GIVE_OK else 'too far',
             f22 / 1000, RINGA_PEAK / 1000, (f22 + RINGA_PEAK) / 1000, g22, 'OK' if g22 <= GIVE_OK else 'too far'))
print('Use 0.20 mm soft tinplate (T2) for the flat blanks. Round kits keep drawn round cups (a flat round blank cannot be folded).')
print('Hand force at the fold peak (travel 30, MA %.1f): about %.0f N for 65 x 90 with 0.20 tin.'
      % (MA(phi_for_travel(30.0), L_REV_BC), (fold_force(2 * 155 - 8 + 2 * math.pi, 0.20, 250) + RINGA_PEAK) / (ETA * MA(phi_for_travel(30.0), L_REV_BC))))

# ----------------------------------------------------------------------------------------------
# 3. Handle joint
# ----------------------------------------------------------------------------------------------
section('3. HANDLE: REV A SCREWED BAR vs REV B/C ONE-PIECE LEVER')
z_m12 = math.pi * 10.2 ** 3 / 32              # M12 minor diameter 10.2
for F in (200, 280, 500):
    print('Rev A M12 stud root (arm 290 - 48 = 242 mm): %3d N -> %.0f MPa' % (F, F * 242 / z_m12))
z_lever = 20 * (2 * 16.77) ** 2 / 6            # 20 thick, 33.5 deep at u = 50
for F in (200, 500):
    print('Rev B/C lever at u = 50 (arm 270 mm, 20 x 33.5): %3d N -> %.1f MPa' % (F, F * 270 / z_lever))
print('C45 yield about 340 MPa (normalised).')

# ----------------------------------------------------------------------------------------------
# 4. Pins, crown, base
# ----------------------------------------------------------------------------------------------
section('4. PINS, CROWN AND BASE (DIE FORCE F AT THE CENTRE)')
def pin_sigma(F, d, arm):
    return (F / 2) * arm / (math.pi * d ** 3 / 32)
for F in (8000, 16000):
    print('F %2d kN: pin O d12 %.0f MPa, d16 %.0f MPa (arm 23); pins A/B d12 %.0f MPa (arm 9)'
          % (F / 1000, pin_sigma(F, 12, 23), pin_sigma(F, 16, 23), pin_sigma(F, 12, 9)))
E = 210000.0
span = 210.0
I_cr = 42 * 25 ** 3 / 12                     # crown 80 wide minus the 38 slot, 25 deep
Z_cr = 42 * 25 ** 2 / 6
for F in (8000, 16000):
    M = F * span / 4
    print('Crown at %2d kN: %.0f MPa, %.2f mm' % (F / 1000, M / Z_cr, F * span ** 3 / (48 * E * I_cr)))
# Rev C.1: slot-wall reliefs take 2 mm off each flange at the centre section: bottom 5 mm (pin B) and top 13 mm (pin A)
layers = [(38, 0, 5), (42, 5, 12), (38, 12, 25)]          # (net width, from, to) up from the crown underside
A_l = [(w, a, b, w * (b - a), (a + b) / 2) for (w, a, b) in layers]
yc = sum(ar * c for (_, _, _, ar, c) in A_l) / sum(ar for (_, _, _, ar, _) in A_l)
I_rel = sum(w * (b - a) ** 3 / 12 + ar * (c - yc) ** 2 for (w, a, b, ar, c) in A_l)
Z_rel = I_rel / max(yc, 25 - yc)
for F in (8000, 16000):
    print('Crown at the slot-wall reliefs (Rev C.1), %2d kN: %.0f MPa' % (F / 1000, F * span / 4 / Z_rel))
# Rev E (independent review): the critical section is the cheek-bolt line (Z = +-17): slot 38, two Ø9 holes with Ø14 x 8.5
# counterbores from below, and the pin-A reliefs (slot 42 wide over the top 13 mm). The cheeks lift the crown there; the moment
# is F/2 x (105 - 17) from each column.
def crown_bolt_line(width):
    lay = [(width - 38 - 28, 0, 8.5), (width - 38 - 18, 8.5, 12), (width - 42 - 18, 12, 25)]
    al = [(w, a, b, w * (b - a), (a + b) / 2) for (w, a, b) in lay]
    yc_ = sum(ar * c for (_, _, _, ar, c) in al) / sum(ar for (_, _, _, ar, _) in al)
    I_ = sum(w * (b - a) ** 3 / 12 + ar * (c - yc_) ** 2 for (w, a, b, ar, c) in al)
    return I_, I_ / yc_, I_ / (25 - yc_)
for width in (80, 120):
    I_, Zb, Zt = crown_bolt_line(width)
    for F in (6400, 16000):
        M = F / 2 * (105 - 17)
        print('Crown %d wide at the cheek-bolt line, %4.1f kN: I %.0f mm4, %.0f MPa (bottom) / %.0f MPa (top)' % (width, F / 1000, I_, M / Zb, M / Zt))
print('Rev E crown: 120 wide (C45 N, Re about 305-340 MPa).')
for t in (12, 15):
    I_b, Z_b = 200 * t ** 3 / 12, 200 * t ** 2 / 6   # 200 mm effective width between the columns
    out = []
    for F in (5000, 15000, 16000):
        M = F * span / 4
        out.append('%2d kN %.0f MPa %.2f mm' % (F / 1000, M / Z_b, F * span ** 3 / (48 * E * I_b)))
    print('Base %d mm: ' % t + ';  '.join(out))

# ----------------------------------------------------------------------------------------------
# 5. Masses
# ----------------------------------------------------------------------------------------------
def poly_area_centroid(pts):
    A = cx = cy = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        c = x0 * y1 - x1 * y0
        A += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    A /= 2
    return abs(A), cx / (6 * A), cy / (6 * A)


def rr_area(w, h, r):
    return w * h - (4 - math.pi) * r * r


circ = lambda d: math.pi * d * d / 4
prof, (Az, Ay) = P.lever_profile()
A_lev, u_cg, w_cg = poly_area_centroid(prof)
A_lev_net = A_lev - circ(18) - circ(14)
m_lever = A_lev_net * 20 * STEEL
m_grip = math.pi * (16 ** 2 - 12 ** 2) * 120 * TPR

frame = {
    'base plate 15 mm': (460 * 260 + 140 * 210) * 15 * STEEL,
    'rails + keepers': 2 * 460 * 14 * 12.05 * STEEL + 2 * 460 * 20 * 4 * STEEL,
    'stop blocks, stop pin, knobs, plunger': 2 * 30 * 27 * 16 * STEEL + 0.10,
    'die table (6061)': (340 * 150 - 2 * circ(8)) * 12 * AL,
    'columns': 2 * (circ(20) * 6.5 + circ(25) * 158 + circ(20) * 25 + circ(16) * 16) * STEEL,
    'crown': (120 * 250 - 38 * 66 - 2 * circ(20)) * 25 * STEEL,
    'column nuts + washers': 2 * 0.045,
}
ram = {
    'ram': (80 * 250 - 2 * circ(32)) * 30 * STEEL,
    'ram bushings': 2 * ((circ(32) - circ(25)) * 30 + (circ(40) - circ(25)) * 3) * BRONZE,
    'clevis': (20 * 32 * 22 - circ(14) * 20) * STEEL,
    'die holder': ((circ(50) * 11 + circ(24) * 4) - circ(16) * 15) * STEEL,
    'return rods + nuts': 2 * circ(10) * 176 * STEEL + 2 * 0.025,
    'station pilot': circ(8) * 84 * STEEL,
}
drive = {
    'pivot cheeks': 2 * (50 * 50 - (4 - math.pi) * 100 / 2 - circ(18)) * 16 * STEEL,
    'handle lever': m_lever,
    'grip (TPR)': m_grip,
    'toggle links': 2 * (60 * 24 + circ(24) - 2 * circ(14)) * 7 * STEEL,
    'pins O, A, B': (circ(16) * 78 + 2 * circ(12) * 40) * STEEL,
    'spacers': 2 * (circ(24) - circ(16.2)) * 10 * BRONZE,
    'return springs': 2 * (math.pi * 28 * 18.4) * circ(3.5) * STEEL,
}
die_upper = {
    'upper die body 144 x 116 x 20 (Rev E)': ((rr_area(144, 116, 6) - circ(10)) * 20 - (circ(54) + 45 * 10) * 10) * STEEL,
    'shank + shim + pins': (circ(16) * 15 + circ(10) * 9) * STEEL + 0.02,
    'upper carrier': (rr_area(144, 116, 3) - rr_area(106.02, 81.02, 6)) * 14 * STEEL,
}
die_lower = {
    'station bases (2)': 2 * rr_area(150, 120, 3) * 10 * STEEL,
    'lower carriers (2)': 2 * ((rr_area(144, 116, 3) - rr_area(106.02, 81.02, 6)) * 15 + (rr_area(144, 116, 3) - rr_area(96, 72, 6)) * 3) * STEEL,
    'die springs, screws, pins': 0.15,
}


def kit(X, Z):
    ring = lambda ox, oz, T: (rr_area(106, 81, 6) - rr_area(ox, oz, 4.2)) * T * STEEL
    return {
        'plug': rr_area(X + 0.3, Z + 0.3, 4.15) * 14.5 * STEEL,
        'upper ring': ring(X + 0.35, Z + 0.35, 14),
        'pickup ring A': ring(X + 0.6, Z + 0.6, 15),
        'pickup pedestal': rr_area(X - 0.5, Z - 0.5, 3.75) * 21.8 * STEEL,
        'crimp ring B': ring(X + 0.45, Z + 0.45, 15),
        'crimp anvil': (rr_area(X + 0.3, Z + 0.3, 4.15) * 16 + rr_area(X - 4.5, Z - 4.5, 2.5)) * STEEL,
    }


def kit_round(Dm):
    """Rev D round size kit, kg (turned plug, pedestal and anvil; rings with a round bore)."""
    disc = lambda d: math.pi * d * d / 4
    ring_r = lambda d, T: (rr_area(106, 81, 6) - disc(d)) * T * STEEL
    return {
        'plug': disc(Dm + 0.3) * 14.5 * STEEL,
        'upper ring': ring_r(Dm + 0.35, 14),
        'pickup ring A': ring_r(Dm + 0.6, 15),
        'pickup pedestal': disc(Dm - 0.5) * 21.8 * STEEL,
        'crimp ring B': ring_r(Dm + 0.45, 15),
        'crimp anvil': (disc(Dm + 0.3) * 16 + disc(Dm - 4.5)) * STEEL,
    }


def revb_set(X, Z):
    """Rev B complete die set for one size (for comparison)."""
    fr = lambda ox, oz, T: (rr_area(126, 100, 3) - rr_area(ox, oz, 4.2)) * T * STEEL
    return (rr_area(126, 100, 6) * 10 * STEEL + fr(X + 0.35, Z + 0.35, 14) + fr(X + 0.6, Z + 0.6, 18) + fr(X + 0.45, Z + 0.45, 18)
            + 2 * rr_area(150, 120, 3) * 10 * STEEL + rr_area(X + 0.3, Z + 0.3, 4.15) * 14.5 * STEEL
            + rr_area(X - 0.5, Z - 0.5, 3.75) * 21.8 * STEEL + rr_area(X - 4.5, Z - 4.5, 2.5) * 17 * STEEL)


section('5. MASSES (estimate, kg)')
groups = [('Frame', frame), ('Ram assembly', ram), ('Drive', drive), ('Universal die, upper', die_upper), ('Universal die, lower', die_lower)]
total = 0
for name, g in groups:
    sub = sum(g.values())
    total += sub
    print('%-24s %5.1f   (%s)' % (name, sub, ', '.join('%s %.2f' % (k, v) for k, v in g.items())))
kits = {cd: kit(X, Z) for cd, X, Z in SIZES}
for cd in kits:
    print('Size kit %s %18.2f   (%s)' % (cd, sum(kits[cd].values()), ', '.join('%s %.2f' % (k, v) for k, v in kits[cd].items())))
heaviest = max(sum(k.values()) for k in kits.values())
print('Press with the heaviest kit fitted   %.1f kg' % (total + heaviest))
print('Die steel for all four sizes: Rev C %.1f kg (universal die + 4 kits)  vs  Rev B %.1f kg (4 complete sets)'
      % (sum(die_upper.values()) + sum(die_lower.values()) + sum(sum(k.values()) for k in kits.values()),
         sum(revb_set(X, Z) for cd, X, Z in SIZES)))
rkits = {cd: kit_round(Dm) for cd, Dm in ROUND}
for cd in rkits:
    print('Size kit %s %19.2f   (%s)' % (cd, sum(rkits[cd].values()), ', '.join('%s %.2f' % (k, v) for k, v in rkits[cd].items())))
print('Rev D: die steel for all eight sizes %.1f kg (universal die + 4 square/rectangular + 4 round kits)'
      % (sum(die_upper.values()) + sum(die_lower.values()) + sum(sum(k.values()) for k in kits.values()) + sum(sum(k.values()) for k in rkits.values())))
print('Lever: area %.0f mm2, mass %.2f kg, CG at u %.0f, w %.1f mm from pivot O' % (A_lev_net, m_lever, u_cg, w_cg))

# ----------------------------------------------------------------------------------------------
# 6. Return springs
# ----------------------------------------------------------------------------------------------
section('6. RETURN SPRINGS (2 per press, on the rods at X +-30)')
d_w, OD, n_act, G_mod = 3.5, 31.5, 16.4, 81500.0
D_m = OD - d_w
k_sp = G_mod * d_w ** 4 / (8 * D_m ** 3 * n_act)
C_ix = D_m / d_w
K_w = (4 * C_ix - 1) / (4 * C_ix - 4) + 0.615 / C_ix
L_inst_open = 109.5
L_solid = (n_act + 2) * d_w
FREE = float(sys.argv[1]) if len(sys.argv) > 1 else 128.0


def F_spring(phi):
    return k_sp * (FREE - (L_inst_open - travel(phi)))


tau = lambda F: 8 * F * D_m * K_w / (math.pi * d_w ** 3)
m_ram_side = sum(ram.values()) + sum(die_upper.values()) + max(k['plug'] + k['upper ring'] for k in kits.values()) + drive['toggle links'] / 2
m_lever_side = m_lever + m_grip + drive['toggle links'] / 2 + circ(12) * 40 * STEEL


def T_lever(psi):
    """torque of the lever weight about O, N.mm (positive = pulls the handle down)."""
    c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    t = m_lever * G_ACC * (u_cg * c - w_cg * s) + m_grip * G_ACC * (320 * c)
    t += (drive['toggle links'] / 2 + circ(12) * 40 * STEEL) * G_ACC * (Az * c - Ay * s)
    return t


print('Wire %.1f, OD %.1f, mean D %.1f (C %.1f), %.1f active coils, G %.0f -> rate %.2f N/mm; solid %.1f mm'
      % (d_w, OD, D_m, C_ix, n_act, G_mod, k_sp, L_solid))
print('Free length %.0f; installed %.1f open, %.1f closed' % (FREE, L_inst_open, L_inst_open - STROKE))
print('Moving mass on the ram %.1f kg; lever side %.2f kg' % (m_ram_side, m_lever_side))
print(' handle deg   springs N (2)   needed N (no friction)   margin   shear stress MPa')
for psi in (65, 45, 30, 15, 3):
    phi = psi + OFF
    need = m_ram_side * G_ACC + T_lever(psi) / dyd(phi)
    have = 2 * F_spring(phi)
    print('    %4.0f        %6.0f            %6.0f              %4.2f      %4.0f' % (psi, have, need, have / need, tau(F_spring(phi))))
print('Torque at the closed position: springs %.2f N.m, needed %.2f N.m' % (2 * F_spring(PHI_END) * dyd(PHI_END) / 1000,
                                                                         (m_ram_side * G_ACC * dyd(PHI_END) + T_lever(3)) / 1000))
print('Rev A springs (2 x 45 N): %.2f N.m' % (2 * 45 * dyd(PHI_END) / 1000))
print('Extra hand force from the springs: at the start %.0f N, at the end %.0f N'
      % (2 * F_spring(PHI_OPEN) / (ETA * MA(PHI_OPEN, L_REV_BC)), 2 * F_spring(PHI_END) / (ETA * MA(PHI_END, L_REV_BC))))

# ----------------------------------------------------------------------------------------------
# 7. Die springs (ISO 10243, rates from supplier charts)
# ----------------------------------------------------------------------------------------------
section('7. DIE SPRINGS (Rev C, universal: the same springs for every size)')
springs = [
    # name, n, rate N/mm, free L, cavity at rest, working travel, class limit for 500k strokes, class max
    ('Lower A (green, light, D10 x 32)', 4, 9.4, 32, 30, 8.0, 35.0, 40.0),
    ('Lower B (green, light, D10 x 32)', 4, 9.4, 32, 30, 8.0, 35.0, 40.0),
    ('Upper Rev D (blue, medium, D10 x 32)', 8, 14.2, 32, 26, STROKE - 26.0 - 8.0, 33.75, 37.5),
    ('Upper Rev E (red, heavy, D12.5 x 44)', UP_N, UP_K, UP_L0, UP_CAV, STROKE - 26.0 - 8.0, 25.0, 30.0),
]
for name, n, k, L0, cav, tr, lim, mx in springs:
    pre = L0 - cav
    dmax = pre + tr
    print('%-34s preload %.1f mm (%2.0f%%) -> %.1f mm (%2.0f%%): %4.0f N -> %4.0f N total; 500k-stroke limit %.2f%%, max %.1f%%'
          % (name, pre, 100 * pre / L0, dmax, 100 * dmax / L0, n * k * pre, n * k * dmax, lim, mx))
print('Upper retraction at the end of stroke 2 = working travel - lower travel = %.2f mm (5.5 available).' % (STROKE - 26 - 8))
print('Rev B used red (heavy) D10 x 32 springs at 12.5 -> 37.5%; the heavy-duty maximum is about 30%.')
print('Rev E upper springs reach 29% at the stop of stroke 2 (heavy-duty max 30%): replace them every 100,000 strokes. The extra cavity')
print('comes from 8 spring caps MP-213 on top of the die body (Rev D blue springs could not hold the ring while the tin folds).')
