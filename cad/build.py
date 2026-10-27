import sys, os, base64, zipfile, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parts as P
import parts2 as Q
from draft import DXF

OUT = sys.argv[1]
IMG1 = sys.argv[2] if len(sys.argv) > 2 else ''
IMG2 = sys.argv[3] if len(sys.argv) > 3 else ''
os.makedirs(os.path.join(OUT, 'svg'), exist_ok=True)

Q.mp001()
for fn in (P.mp101, P.mp102, P.mp103, P.mp104, P.mp105, P.mp106, P.mp107, P.mp108, P.mp109, P.mp110, P.mp111,
           P.mp112, P.mp113, P.mp114, P.mp116, P.mp117, P.mp118, P.mp119, P.mp120, P.mp121,
           Q.mp201, Q.mp202, Q.mp203, Q.mp204, Q.mp205, Q.mp206, Q.mp207, Q.mp208, Q.mp209, Q.mp210, Q.mp211, Q.mp212, Q.mp223, Q.mp224, Q.mp226, Q.mp227, Q.mp228, Q.mp229):
    fn()
listing = [[s.no, s.title, s.qty, str(i + 2)] for i, s in enumerate(P.SHEETS)]
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode() if p and os.path.exists(p) else None
Q.mp000(listing, b64(IMG1), b64(IMG2))
N = len(P.SHEETS)
pages = []
for i, sh in enumerate(P.SHEETS, 1):
    sh.index, sh.total = i, N
    svg = sh.svg()
    fn = os.path.join(OUT, 'svg', '%02d_%s.svg' % (i, sh.no))
    open(fn, 'w').write(svg)
    pages.append(svg)
html = ('<!doctype html><html><head><meta charset="utf-8"><style>@page{size:420mm 297mm;margin:0}'
        'html,body{margin:0;padding:0}.pg{width:420mm;height:297mm;page-break-after:always;overflow:hidden}'
        '.pg:last-child{page-break-after:auto}</style></head><body>' + ''.join('<div class="pg">%s</div>' % p for p in pages) + '</body></html>')
open(os.path.join(OUT, 'set.html'), 'w').write(html)
zp = os.path.join(OUT, 'MagPress-M4_DXF_RevE.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    readme = ('MagPress M4 Rev E - DXF profiles (R12, mm, 1:1).\n'
              'Layers: OUTLINE (cut), HOLES (through holes, true size), TAP_DRILL (tap drill size - tap after cutting),\n'
              'COUNTERBORE (c\'bore diameter - machine to depth per drawing), POCKET (blind pocket outline), SPOT.\n'
              'Plan views: X right, front of the press at the bottom (crown/ram: front to the right).\n'
              'Die-set files carry the size code: 5050, 6363, 5380, 6590, and D44, D50, D56, D58 for the round kits (rings only; round plugs, pedestals and anvils are turned). The PDF drawings govern.\n')
    z.writestr('README.txt', readme)
    for name, dx in sorted(P.DXFS.items()):
        z.writestr(name, dx.dumps())
print(json.dumps({'sheets': N, 'dxf': len(P.DXFS)}))
