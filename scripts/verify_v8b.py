# -*- coding: utf-8 -*-
import pymupdf
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
full = "\n".join(p.get_text("text", sort=True) for p in doc)
for kw in ["自免疫」为工程借喻", "修辞语", "所指机制为公理 IV", "极易触发", "经验繁殖阈值"]:
    print("%-24s count=%d" % (kw, full.count(kw)))
# 公理 IV 锚定上下文
i = full.find("自免疫」为工程借喻")
if i >= 0:
    print("ctx:", full[i-50:i+60].replace("\n", " "))
else:
    i = full.find("工程借喻")
    print("ctx2:", full[max(0,i-60):i+60].replace("\n", " ") if i>=0 else "not found")
doc.close()
