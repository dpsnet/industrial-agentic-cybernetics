# -*- coding: utf-8 -*-
"""验证新 PDF：页数/大小、关键文本定位、渲染关键页。"""
import pymupdf, io, os
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
print("pages:", doc.page_count, "size:", os.path.getsize(pdf))
targets = ["CI 不含", "代理探索", "幂律分支占优", "无效重试", "公理", "隐式分支嗅探", "原生 Provider 桥接", "首字时延短于"]
found = {t: [] for t in targets}
for i, pg in enumerate(doc, 1):
    t = pg.get_text("text", sort=True)
    for k in targets:
        if k in t:
            found[k].append(i)
for k, v in found.items():
    print(k, "->", v)
out = r"E:\workspace\industrial-agentic-cybernetics\monograph\_qa"
for p in sorted(set(sum(found.values(), []))):
    pg = doc[p-1]
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
    pix.save(os.path.join(out, "qanew_p%03d.png" % p))
print("rendered:", len(set(sum(found.values(), []))), "pages")
