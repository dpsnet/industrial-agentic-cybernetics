# -*- coding: utf-8 -*-
from PIL import Image
import os
fig = r"E:\workspace\industrial-agentic-cybernetics\monograph\figures"
for n in [52, 53]:
    png = os.path.join(fig, "m%d.png" % n)
    jpg = os.path.join(fig, "m%d.jpg" % n)
    im = Image.open(png).convert("RGB")
    w, h = im.size
    bg = Image.new("RGB", (w, h), (255, 255, 255))
    bg.paste(im, (0, 0))
    bg.save(jpg, "JPEG", quality=92)
    print("m%d %dx%d ratio=%.2f jpg=%d" % (n, w, h, w/h, os.path.getsize(jpg)))
