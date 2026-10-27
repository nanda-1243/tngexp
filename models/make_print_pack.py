"""Zip the individual part files for 3D printing: STL at full size and at half scale, and OBJ at full size.

python3 models/make_print_pack.py        # reads models/stl, models/obj and models/parts.csv; writes the zips to release/RevD/

Each file sits in a folder for its group, with the number to print at the end of its name (…_x4.stl).
"""
import csv
import io
import os
import struct
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REL = os.path.join(HERE, '..', 'release', 'RevD')
TAG = 'MagPress-M4_RevD'
SIZES = {'5050': '50 × 50', '6363': '63.5 × 63.5', '5380': '53 × 80', '6590': '65 × 90',
         'D44': 'Ø44', 'D50': 'Ø50', 'D56': 'Ø56', 'D58': 'Ø58'}
FOLDERS = {'Frame': '01_frame', 'Die table': '02_die-table', 'Press drive': '03_press-drive', 'Universal die': '04_universal-die'}


def folder_and_qty(r):
    pid, qty = r['id'], int(r['qty_in_assembly'])
    code = pid.rsplit('-', 1)[-1]
    if r['group'] == 'Size kit' and code in SIZES:
        return '%02d_kit-%s' % (6 + list(SIZES).index(code), code), 1
    if r['group'] == 'Size kit':
        return '05_kit-hardware_per-kit', qty
    return FOLDERS[r['group']], max(qty, 1)


def stl_scaled(data, k):
    """binary STL with every vertex multiplied by k."""
    n = struct.unpack_from('<I', data, 80)[0]
    out = bytearray(data[:84])
    for i in range(n):
        o = 84 + 50 * i
        nx, ny, nz, *v, attr = struct.unpack_from('<12fH', data, o)
        out += struct.pack('<12fH', nx, ny, nz, *[c * k for c in v], attr)
    return bytes(out)


def stl_size(data):
    n = struct.unpack_from('<I', data, 80)[0]
    lo, hi = [1e9] * 3, [-1e9] * 3
    for i in range(n):
        v = struct.unpack_from('<9f', data, 84 + 50 * i + 12)
        for j in range(9):
            lo[j % 3] = min(lo[j % 3], v[j]); hi[j % 3] = max(hi[j % 3], v[j])
    return [hi[i] - lo[i] for i in range(3)]


def readme(scale, rows, fmt):
    pieces = sum(q for (_, _, q, _) in rows)
    big = [(name, dims) for (name, _, _, dims) in rows if max(dims[0], dims[1]) > 220 or dims[2] > 250]
    lines = ['MagPress M4 Rev D - every part as its own %s file, %s.' % (fmt, scale),
             '',
             'Folders: 01 frame, 02 die table, 03 press drive (ram, crown, lever, links, pins), 04 universal die,',
             '05 hardware that comes with every size kit, 06-09 the square and rectangular kits (5050 = 50 x 50,',
             '6363 = 63.5 x 63.5, 5380 = 53 x 80, 6590 = 65 x 90), 10-13 the round kits (D44 = diameter 44 ... D58 = diameter 58).',
             'Round kits use the inner plug holes (D2, K2) in the upper die body and need no 4 mm pins (BUY-48).',
             'Pick the kits you want; one kit is enough to see how everything fits.',
             '',
             'The number at the end of each file name is how many to print for one press (folder 05: per kit).',
             'Files: %d. Pieces for one press with all eight kits: %d.' % (len(rows), pieces + 7 * sum(q for (n, f, q, _) in rows if f.startswith('05'))),
             '',
             'MP-xxx files are machined parts (drawing numbers). BUY-xx files are bought hardware (screws, pins, springs,',
             'bushings): print them for looks, or use real ones at full size and skip them.',
             '',
             'Units mm. Parts lie flat or stand on one end, ready to slice. Holes and pins are at their true size, so',
             'printed pins will not go into printed holes: use the slicer\'s hole compensation (+0.15 to +0.3 mm) or print',
             'pins and screws at 97-98 %. Springs are shown at their installed length.',
             '']
    if big:
        lines.append('Parts that need more than a 220 x 220 mm bed or 250 mm height at this scale (as laid out in the file, X x Y x height):')
        lines += ['  %s  %.0f x %.0f x %.0f mm' % (n, *d) for (n, d) in big]
    else:
        lines.append('Every part fits a 220 x 220 mm bed and 250 mm height at this scale, as laid out in its file.')
    lines += ['', 'Made by models/make_print_pack.py from models/stl and models/obj. 3D views of how the parts fit:',
              'models/assembly/ and the assembly manual (release/RevD/MagPress-M4_Assembly-Manual_RevD.pdf).', '']
    return '\n'.join(lines)


def pack(name, fmt, scale_k, scale_txt):
    rows, files = [], []
    with open(os.path.join(HERE, 'parts.csv')) as f:
        for r in csv.DictReader(f):
            folder, qty = folder_and_qty(r)
            src = os.path.join(HERE, fmt.lower(), r['file_base'] + '.' + fmt.lower())
            with open(src, 'rb') as g:
                data = g.read()
            if fmt == 'STL':
                if scale_k != 1:
                    data = stl_scaled(data, scale_k)
                dims = stl_size(data)
            else:
                dims = [0, 0, 0]
            arc = '%s/%s_x%d.%s' % (folder, r['file_base'], qty, fmt.lower())
            files.append((arc, data))
            rows.append((r['file_base'], folder, qty, dims))
    path = os.path.join(REL, name)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('README.txt', readme(scale_txt, rows, fmt))
        for arc, data in sorted(files):
            z.writestr(arc, data)
    print('%s: %d files, %.1f MB' % (name, len(files), os.path.getsize(path) / 1e6))


if __name__ == '__main__':
    os.makedirs(REL, exist_ok=True)
    pack('%s_print-STL_half-scale.zip' % TAG, 'STL', 0.5, 'half scale (50 %), fits a 256 mm bed')
    pack('%s_print-STL_full-size.zip' % TAG, 'STL', 1.0, 'full size (1:1)')
    pack('%s_print-OBJ_full-size.zip' % TAG, 'OBJ', 1.0, 'full size (1:1)')
