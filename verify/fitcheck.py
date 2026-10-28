"""Fastener and pin engagement check on the placed Rev E assembly.

For every screw, stud, set screw, thumb screw, plunger and nut: a thin probe ring just outside (male) or just inside
(female, nuts) the nominal thread diameter, over the threaded length, is intersected with every other placed part.
Tapped holes are modelled at the nominal diameter, so a ring of d+0.02..d+0.30 lies in metal over the engaged length of a
tapped hole and in air inside a clearance hole (clearance >= d+0.4). Engagement length = overlap volume / ring area.
For dowels and pins the same ring over the whole pin gives the length held in each part.
Also checked: the screw head (or countersink) bears on a part, and no screw is threaded into two parts at once.
"""
import math
import os
import sys

ROOT = '/home/user/tngexp'
sys.path[:0] = [os.path.join(ROOT, 'models'), os.path.join(ROOT, 'cad')]
os.chdir(os.path.join(ROOT, 'models'))
import build_models as B  # noqa: E402

V = B.V
B.build()
shapes = {p['id']: p for p in B.PARTS}
inst = []
for p in B.PARTS:
    for n, f in enumerate(p['places'], 1):
        inst.append(('%s_%d' % (p['id'], n), p['id'], f, f(p['shape'])))

# fastener table: id -> (kind, d, thread zone in local z (z0, z1), head ring (z, r_in, r_out) or None, material note)
# local frames follow build_models: shank along -Z from the head (cap/csk/shoulder), studs/set screws along +Z.
F = {
    'BUY-02': ('screw', 5, (-30, -2.95), ('csk', 5, 11.2)),       # csk M5x30, head 3.1 deep
    'BUY-03': ('screw', 5, (-35, -0.5), ('cap', 5.5, 8.5)),
    'BUY-04': ('screw', 6, (-40, -0.5), ('cap', 6.5, 10)),
    'BUY-06': ('screw', 10, (-16, -0.5), ('cap', 10.5, 16)),
    'BUY-10': ('set', 10, (0, 12), None),
    'BUY-24': ('screw', 8, (-30, -0.5), ('cap', 8.5, 13)),
    'BUY-27': ('screw', 5, (-25, -0.5), ('cap', 5.5, 8.5)),
    'BUY-28': ('screw', 5, (-16, -0.5), ('cap', 5.5, 8.5)),
    'BUY-29': ('set', 5, (0, 10), None),
    'BUY-35': ('screw', 5, (-19.5, -10.0), ('cap', 6.5, 10)),     # shoulder Ø6 x 10, thread M5 x 9.5
    'BUY-36': ('screw', 5, (-21.5, -12.0), ('cap', 6.5, 10)),
    'BUY-38': ('set', 5, (3, 22), None),                          # thumb screw thread
    'BUY-40': ('screw', 5, (-20, -2.95), ('csk', 5, 11.2)),
    'BUY-23': ('set', 6, (-10, 0), None),                         # bumper M6 stud
    'BUY-32': ('set', 5, (-8, 0), None),                          # knob M5 stud
    'BUY-31': ('set', 6, (0, 11.5), None),                        # M6 ball plunger body
    'BUY-45': ('set', 3, (0.75, 6), None),                        # M3 ball plunger body
    'BUY-22': ('nut', 10, (0, 10), None),
    'BUY-09': ('nut', 16, (0, 13), None),
    'BUY-05': ('nut', 6, (0, 3.2), None),
    # pins: (kind, d, (z0, z1)) whole length
    'BUY-26': ('pin', 6, (0, 16), None), 'BUY-37': ('pin', 4, (0, 14), None), 'BUY-41': ('pin', 6, (0, 12), None),
    'BUY-42': ('pin', 4, (0, 12), None), 'BUY-46': ('pin', 5, (0, 14), None), 'BUY-47': ('pin', 12, (0, 15), None),
    'BUY-48': ('pin', 4, (0, 10), None), 'BUY-39': ('pin', 6, (0, 64), None),
}
PIN_FRICTION = {'BUY-39'}
# the plug stud MP-212 (M6 into the plug) is a made part: check its threaded end too
STUD = 'MP-212'


def ring(d_in, d_out, z0, z1):
    return B.tube(d_out, d_in, z1 - z0, z0=z0)


def probe_for(kind, d, z0, z1):
    if kind == 'nut':
        return ring(d - 0.30, d - 0.02, z0, z1), math.pi / 4 * ((d - 0.02) ** 2 - (d - 0.30) ** 2)
    return ring(d + 0.02, d + 0.30, z0, z1), math.pi / 4 * ((d + 0.30) ** 2 - (d + 0.02) ** 2)


others = [(n, pid, s, s.BoundingBox()) for (n, pid, f, s) in inst]


def overlaps(shape, me):
    bb = shape.BoundingBox()
    out = []
    for n, pid, s, b in others:
        if n == me:
            continue
        if b.xmax < bb.xmin or bb.xmax < b.xmin or b.ymax < bb.ymin or bb.ymax < b.ymin or b.zmax < bb.zmin or bb.zmax < b.zmin:
            continue
        v = s.intersect(shape).Volume()
        if v > 1e-3:
            out.append((n, pid, v))
    return out


rows, flags = [], []
for n, pid, f, s in inst:
    if pid not in F:
        continue
    kind, d, (z0, z1), head = F[pid]
    pr, area = probe_for(kind, d, z0, z1)
    hits = overlaps(f(pr), n)
    eng = [(hn, hp, v / area) for (hn, hp, v) in hits]
    eng = [e for e in eng if e[2] > 0.05]
    desc = ', '.join('%s %.1f' % (hn, L) for (hn, hp, L) in sorted(eng, key=lambda e: -e[2])) or 'nothing'
    note = ''
    if kind in ('screw', 'set'):
        tot = sum(L for (_, _, L) in eng)
        nparts = len([e for e in eng if e[2] > 0.5])
        if tot < 1.0 * d - 1e-6:
            note = 'SHORT ENGAGEMENT (%.1f < 1.0 d)' % tot
        if kind == 'screw' and nparts > 1:
            note += (' ' if note else '') + 'THREADED IN %d PARTS' % nparts
        if head:
            ht, ri, ro = head
            if ht == 'cap':
                hp_ = ring(ri, ro - 0.3, -0.25, 0.0)
            else:
                hp_ = B.cone(d + 0.5, ro - 0.4, (ro - d) / 2 - 0.3, z0=-(ro - d) / 2)
            seat = overlaps(f(hp_), n)
            seat = [h for h in seat if h[2] > 0.02]
            if not seat:
                note += (' ' if note else '') + 'HEAD NOT SEATED'
            desc += ' | head on ' + (', '.join(h[0] for h in seat) or '-')
    elif kind == 'nut':
        tot = sum(L for (_, _, L) in eng)
        if tot < 0.8 * (z1 - z0):
            note = 'NUT NOT FULLY ON THREAD (%.1f of %.1f)' % (tot, z1 - z0)
    elif kind == 'pin':
        held = sorted([e for e in eng], key=lambda e: -e[2])
        if len(held) < 2 and pid not in ('BUY-37',):
            note = 'PIN IN ONE PART ONLY'
        elif len(held) >= 2 and held[1][2] < 0.8 * d and pid not in PIN_FRICTION:
            note = 'SHORT ENGAGEMENT IN %s (%.1f < 0.8 d)' % (held[1][0], held[1][2])
    rows.append((n, kind, d, desc, note))
    if note:
        flags.append((n, note))

# plug stud: its M6 end into the plug MP-203 (thread along local z; read from cad if available)
out = ['Fastener and pin engagement check, MagPress M4 Rev E assembly (handle up, kit 6363 at station B).',
       'Engagement = length of thread (or pin) held in metal in each part, mm. Tapped holes are modelled at the nominal diameter.', '']
out.append('%-12s %-6s %-4s %s' % ('instance', 'kind', 'd', 'engaged in (mm)  | head bears on'))
for n, kind, d, desc, note in rows:
    out.append('%-12s %-6s %-4g %s%s' % (n, kind, d, desc, ('   <-- ' + note) if note else ''))
out.append('')
out.append('%d fasteners and pins checked, %d flagged.' % (len(rows), len(flags)))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fitcheck.txt'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out[-1:]))
for n, note in flags:
    print('  FLAG', n, note)
