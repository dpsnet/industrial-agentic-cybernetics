# -*- coding: utf-8 -*-
"""按宽高比分级调整 LaTeX md 中图片宽度：竖长图(高/宽>=1.3) 70%，横图 80%——消除 Float too large。"""
import io, re, os
from PIL import Image

base = r"E:\workspace\industrial-agentic-cybernetics\monograph"
p_md = os.path.join(base, "manuscript-latex.md")
lines = io.open(p_md, encoding="utf-8").read().split("\n")
img_re = re.compile(r"^(!\[[^\]]*\]\(figures/(m\d+)\.jpg\)\{width=)(\d+)%\}$")
n = 0
for i, ln in enumerate(lines):
    m = img_re.match(ln.strip())
    if m:
        name = m.group(2)
        ip = os.path.join(base, "figures", name + ".jpg")
        try:
            w, h = Image.open(ip).size
        except Exception as e:
            print("ERR", name, e)
            continue
        ratio = h / w if w else 0
        neww = 60 if ratio >= 1.85 else (70 if ratio >= 1.3 else 80)
        if int(m.group(3)) != neww:
            lines[i] = m.group(1) + str(neww) + "%}"
            n += 1
            print("m%s ratio=%.2f -> %d%%" % (name, ratio, neww))
io.open(p_md, "w", encoding="utf-8").write("\n".join(lines))
print("adjusted:", n)
