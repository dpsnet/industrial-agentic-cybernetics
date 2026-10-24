# -*- coding: utf-8 -*-
import pymupdf
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
for key in ["隔离环境审计与三维异常嗅探维度", "缺陷萃取-验证-晋升-免疫闭环"]:
    pg = next((i for i, p in enumerate(doc, start=1) if key in p.get_text("text", sort=True)), None)
    print(key, "-> p%s" % pg)
    if pg:
        t = doc[pg-1].get_text("text", sort=True)
        idx = t.find(key)
        print("   ctx:", t[max(0,idx-40):idx+40].replace("\n", " "))
doc.close()
