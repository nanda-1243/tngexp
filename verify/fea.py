"""Linear-elastic CalculiX runs on single parts meshed with gmsh (C3D10 tets). Units mm, N, MPa."""
import math
import os
import subprocess

import gmsh
import numpy as np

FACE = {(0, 1, 2): 1, (0, 3, 1): 2, (1, 3, 2): 3, (2, 3, 0): 4}     # C3D10 corner-node faces (0-based) -> S1..S4


def mesh(step, size, refine=(), order=2, quiet=True):
    """refine: list of (x, y, z, radius, size). Returns nodes {tag: xyz}, tets [(tag, [10 nodes])], surfaces {surf_tag: info}."""
    gmsh.initialize()
    gmsh.option.setNumber('General.Terminal', 0 if quiet else 1)
    gmsh.model.add('p')
    gmsh.model.occ.importShapes(step)
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber('Mesh.MeshSizeMax', size)
    gmsh.option.setNumber('Mesh.MeshSizeMin', size / 8)
    if refine:
        fields = []
        for k, (x, y, z, r, s) in enumerate(refine):
            f = gmsh.model.mesh.field.add('Ball')
            gmsh.model.mesh.field.setNumber(f, 'XCenter', x)
            gmsh.model.mesh.field.setNumber(f, 'YCenter', y)
            gmsh.model.mesh.field.setNumber(f, 'ZCenter', z)
            gmsh.model.mesh.field.setNumber(f, 'Radius', r)
            gmsh.model.mesh.field.setNumber(f, 'VIn', s)
            gmsh.model.mesh.field.setNumber(f, 'VOut', size)
            fields.append(f)
        mn = gmsh.model.mesh.field.add('Min')
        gmsh.model.mesh.field.setNumbers(mn, 'FieldsList', fields)
        gmsh.model.mesh.field.setAsBackgroundMesh(mn)
        gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary', 0)
    gmsh.option.setNumber('Mesh.SecondOrderLinear', 1)
    gmsh.model.mesh.generate(3)
    gmsh.model.mesh.setOrder(order)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    nodes = {int(t): xyz[3 * i:3 * i + 3] for i, t in enumerate(tags)}
    et, etags, enodes = gmsh.model.mesh.getElements(3)
    tets = []
    for k, t in enumerate(et):
        npe = gmsh.model.mesh.getElementProperties(t)[3]
        for i, e in enumerate(etags[k]):
            tets.append((int(e), [int(n) for n in enodes[k][npe * i:npe * (i + 1)]]))
    surfs = {}
    for dim, s in gmsh.model.getEntities(2):
        com = gmsh.model.occ.getCenterOfMass(2, s)
        bb = gmsh.model.getBoundingBox(2, s)
        typ = gmsh.model.getType(2, s)
        pc = gmsh.model.getParametrizationBounds(2, s)
        uv = [(pc[0][0] + pc[1][0]) / 2, (pc[0][1] + pc[1][1]) / 2]
        nrm = gmsh.model.getNormal(s, uv)
        area = gmsh.model.occ.getMass(2, s)
        st, stag, snodes = gmsh.model.mesh.getElements(2, s)
        tris = []
        for k, t in enumerate(st):
            npe = gmsh.model.mesh.getElementProperties(t)[3]
            for i in range(len(stag[k])):
                tris.append([int(n) for n in snodes[k][npe * i:npe * (i + 1)]])
        snode_tags = set(int(n) for tri in tris for n in tri)
        surfs[s] = dict(com=np.array(com), bb=bb, type=typ, normal=np.array(nrm), area=area, tris=tris, nodes=snode_tags)
    gmsh.finalize()
    return nodes, tets, surfs


def faces_of(tets, tris):
    """element-face list (elem, 'S#') for surface triangles."""
    idx = {}
    for e, c in tets:
        corners = c[:4]
        for (a, b, d), fid in FACE.items():
            idx[frozenset((corners[a], corners[b], corners[d]))] = (e, fid)
    out = []
    for tri in tris:
        key = frozenset(tri[:3])
        if key in idx:
            out.append(idx[key])
    return out


def write_inp(path, nodes, tets, E, nu, bcs, dloads, cloads=(), nsets=None):
    """bcs: [(node list, dof_from, dof_to, value)], dloads: [(faces [(e, fid)], pressure)], cloads: [(node, dof, F)]."""
    L = ['*NODE, NSET=NALL']
    for t, p in nodes.items():
        L.append('%d, %.6f, %.6f, %.6f' % (t, p[0], p[1], p[2]))
    L.append('*ELEMENT, TYPE=C3D10, ELSET=EALL')
    for e, c in tets:
        # gmsh 10-node tet order -> CalculiX: gmsh edges (0-1,1-2,2-0,0-3,2-3,1-3) vs ccx (1-2,2-3,3-1,1-4,2-4,3-4)
        cc = c[:4] + [c[4], c[5], c[6], c[7], c[9], c[8]]
        L.append('%d, %s' % (e, ', '.join(map(str, cc))))
    for k, (ns, d0, d1, v) in enumerate(bcs):
        L.append('*NSET, NSET=B%d' % k)
        ns = sorted(ns)
        for i in range(0, len(ns), 12):
            L.append(', '.join(map(str, ns[i:i + 12])))
    L += ['*MATERIAL, NAME=STEEL', '*ELASTIC', '%g, %g' % (E, nu), '*SOLID SECTION, ELSET=EALL, MATERIAL=STEEL',
          '*STEP', '*STATIC, SOLVER=ITERATIVE CHOLESKY', '*BOUNDARY']
    for k, (ns, d0, d1, v) in enumerate(bcs):
        L.append('B%d, %d, %d, %g' % (k, d0, d1, v))
    if dloads:
        L.append('*DLOAD')
        for faces, p in dloads:
            for e, f in faces:
                L.append('%d, P%d, %g' % (e, f, p))
    if cloads:
        L.append('*CLOAD')
        for n, d, F in cloads:
            L.append('%d, %d, %g' % (n, d, F))
    L += ['*NODE FILE', 'U', '*EL FILE', 'S', '*NODE PRINT, NSET=NALL, TOTALS=ONLY', 'RF', '*END STEP']
    open(path, 'w').write('\n'.join(L) + '\n')


def run(job, cwd):
    env = dict(os.environ, OMP_NUM_THREADS='2', CCX_NPROC_EQUATION_SOLVER='2')
    with open(os.path.join(cwd, job + '.log'), 'w') as f:
        return subprocess.run(['ccx', '-i', job], cwd=cwd, stdout=f, stderr=subprocess.STDOUT, env=env).returncode


def read_results(frd):
    """last DISP and STRESS blocks: {node: (ux,uy,uz)}, {node: (sxx,syy,szz,sxy,syz,szx)}."""
    blocks = {}
    with open(frd, errors='replace') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith(' -4  DISP') or l.startswith(' -4  STRESS'):
            name = l[5:13].strip()
            cur = {}
            i += 1
            while lines[i].startswith(' -5'):
                i += 1
            while not lines[i].startswith(' -3'):
                s = lines[i]
                n = int(s[3:13])
                vals = [float(s[13 + 12 * k:25 + 12 * k]) for k in range((len(s.rstrip()) - 13) // 12)]
                cur[n] = vals
                i += 1
            blocks[name] = cur
        i += 1
    return blocks.get('DISP', {}), blocks.get('STRESS', {})


def mises(s):
    sxx, syy, szz, sxy, syz, szx = s[:6]
    return math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) + 3 * (sxy ** 2 + syz ** 2 + szx ** 2))
