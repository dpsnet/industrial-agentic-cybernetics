# -*- coding: utf-8 -*-
import pymupdf
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
rows = ["pages=%d" % doc.page_count]
full = "\n".join(p.get_text("text", sort=True) for p in doc)
for kw in ["flowchart TD", "flowchart", "sequenceDiagram", "subgraph", "mermaid", "截断示例片段"]:
    rows.append("%-16s count=%d" % (kw, full.count(kw)))
rows.append("model_full=%s" % ("DeepSeek-V4.1-Flash-1017" in full))
rows.append("model_short=%s" % ("pro/Kimi/Flash" in full))
n = sum(len(p.get_images(full=True)) for p in doc)
rows.append("images=%d" % n)
for key in ["图51", "图52", "图53", "图54"]:
    rows.append("%s=%s" % (key, key in full))
for key in ["模式 23：隔离环境审计与三维异常嗅探维度流程", "模式 24：缺陷萃取-验证-晋升-免疫闭环流程"]:
    pg = next((i for i, p in enumerate(doc, start=1) if key in p.get_text("text", sort=True)), None)
    rows.append("caption '%s' -> p%s" % (key[:16], pg))
print("\n".join(rows))
