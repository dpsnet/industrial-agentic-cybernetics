# -*- coding: utf-8 -*-
from PIL import Image
import os
fig = r"E:\workspace\industrial-agentic-cybernetics\monograph\figures"
for n in [50, 51]:
    png = os.path.join(fig, "m%d.png" % n)
    jpg = os.path.join(fig, "m%d.jpg" % n)
    im = Image.open(png).convert("RGB")
    w, h = im.size
    # 白底
    bg = Image.new("RGB", (w, h), (255, 255, 255))
    bg.paste(im, (0, 0))
    bg.save(jpg, "JPEG", quality=92)
    print("m%d.png %dx%d ratio=%.2f -> m%d.jpg %d bytes" % (n, w, h, w/h, n, os.path.getsize(jpg)))
