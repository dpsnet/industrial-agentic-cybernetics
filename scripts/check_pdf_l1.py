# -*- coding: utf-8 -*-
import fitz
doc = fitz.open(r"E:\workspace\industrial-agentic-cybernetics\monograph\Industrial-Agentic-Cybernetics.pdf")
toc = doc.get_toc(simple=False)
hits = [t for t in toc if t[0] == 1]
print("level1 count:", len(hits))
for lvl, title, page, _ in hits:
    print(page, title[:52])
