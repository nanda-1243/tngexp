"""Interference sweep through the whole stroke at 1 degree steps of the handle (handle up -> stop at 3 deg).
Moving parts (ram group, lever group, links) are checked against every other placed part; die parts against die parts
are skipped (the spring-loaded rings telescope by design), return springs skipped (they compress)."""
import math
import os
import sys

ROOT = '/home/user/tngexp'
sys.path[:0] = [os.path.join(ROOT, 'models'), os.path.join(ROOT, 'cad')]
os.chdir(os.path.join(ROOT, 'models'))
import build_models as B  # noqa: E402

B.build()
inst = []
for p in B.PARTS:
    for n, f in enumerate(p['places'], 1):
        inst.append(('%s_%d' % (p['id'], n), p['id'], f(p['shape']), p['color']))
groups = {p['id']: p['group'] for p in B.PARTS}
die = lambda n: groups[n.rsplit('_', 1)[0]] in ('Universal die', 'Size kit')
moving_ids = B.RAM_MOVES | B.LEVER_MOVES | {'MP-114'}


def is_moving(n, pid):
    return n in moving_ids or pid in moving_ids


results = []
angles = [B.PSI] + list(range(int(B.PSI), 2, -1))
for psi in angles:
    placed, drop = B.pose(inst, psi)
    mov = [(n, pid, s, s.BoundingBox()) for (n, pid, s) in placed if is_moving(n, pid)]
    fix = [(n, pid, s, s.BoundingBox()) for (n, pid, s) in placed]
    hits = []
    seen = set()
    for n1, p1, s1, b1 in mov:
        for n2, p2, s2, b2 in fix:
            if n1 == n2 or (n2, n1) in seen:
                continue
            seen.add((n1, n2))
            if b1.xmax < b2.xmin or b2.xmax < b1.xmin or b1.ymax < b2.ymin or b2.ymax < b1.ymin or b1.zmax < b2.zmin or b2.zmax < b1.zmin:
                continue
            if (die(n1) and die(n2)) or 'BUY-20' in (p1, p2):
                continue
            v = s1.intersect(s2).Volume()
            if v > 1.0:
                hits.append((n1, n2, v))
    results.append((psi, drop, hits))
    print('psi %5.1f  ram %5.2f  overlaps %d' % (psi, drop, len(hits)), flush=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sweep.txt'), 'w') as f:
    f.write('Interference sweep, handle %.1f deg (up) to 3 deg (stop) in 1 deg steps, moving parts against all others.\n' % B.PSI)
    for psi, drop, hits in results:
        f.write('psi %5.1f  ram down %6.2f mm  overlaps: %s\n' % (psi, drop, ', '.join('%s x %s %.1f mm3' % h for h in hits) or 'none'))
print('done', sum(len(h) for _, _, h in results), 'overlaps in total')
