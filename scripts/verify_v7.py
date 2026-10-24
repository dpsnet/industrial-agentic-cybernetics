# -*- coding: utf-8 -*-
import pymupdf
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
full = "\n".join(p.get_text("text", sort=True) for p in doc)
print("pages=%d" % doc.page_count)
print("images=%d" % sum(len(p.get_images(full=True)) for p in doc))
for kw in ["2. 动机与工业失效场景 (Motivation", "5. 协作协议与状态跃迁 (Collaborations)", "5. 协作协议与因果约束 (Collaborations)", "成瘾性", "2605.20744"]:
    print("template/removed %-28s count=%d" % (kw[:26], full.count(kw)))
for kw in ["模式 01：穿透者伪装交付物", "模式 10：租约仲裁-锁状态", "模式 19：仓库-编译器-探针-门禁五重判据", "模式 22：网关-模型-底座原生直连"]:
    print("semantic %-30s present=%s" % (kw[:28], kw in full))
for kw in ["2603.04474","2509.25370","2608.05263","2605.02964","2605.20744","25. Roth","22. Zhu"]:
    print("ref %-12s count=%d" % (kw, full.count(kw)))
doc.close()
