"""Crop the two cover renders to the 111 x 200 frames on MP-000.  Usage: python3 web/tools/crop_covers.py <shots dir> cad"""
import sys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
for a, b in (('cover_assembled.png', 'img_assembled.png'), ('cover_exploded.png', 'img_exploded.png')):
    im = Image.open('%s/%s' % (src, a)).convert('RGB')
    W, H = im.size
    h = int(W / (111 / 200))
    y0 = max(0, (H - h) // 2)
    im.crop((0, y0, W, y0 + h)).save('%s/%s' % (dst, b))
