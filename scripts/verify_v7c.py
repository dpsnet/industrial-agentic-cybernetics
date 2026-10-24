# -*- coding: utf-8 -*-
import pymupdf
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
full = "\n".join(p.get_text("text", sort=True) for p in doc)
for kw in ["智能体-沙箱-隐藏", "隔离测评", "模式 18"]:
    print("%-14s count=%d" % (kw, full.count(kw)))
idx = full.find("智能体-沙箱-隐藏")
if idx >= 0:
    print("ctx:", full[idx-30:idx+30].replace("\n", " "))
else:
    # 找 模式 18 图注附近
    for p in doc:
        t = p.get_text("text", sort=True)
        if "模式 18" in t and "示意" in t:
            i = t.find("模式 18")
            print("page ctx:", t[i:i+80].replace("\n", " "))
            break
doc.close()
