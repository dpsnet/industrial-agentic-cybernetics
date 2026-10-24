# -*- coding: utf-8 -*-
import pymupdf
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
full = "\n".join(p.get_text("text", sort=True) for p in doc)
print("pages=%d images=%d" % (doc.page_count, sum(len(p.get_images(full=True)) for p in doc)))
for kw in ["四公理证据等级总览", "证据强度排序为 IV > II > III", "同行现状说明", "『工业级』口径声明", "形式化层全部已证", "（全部已证）", "B.2 公理 I：接地不可替代性"]:
    print("%-28s count=%d" % (kw, full.count(kw)))
# 证据表内容抽查
for kw in ["认识论类型", "带边界声明的经验律", "分布式系统经典结论的应用迁移", "最强支柱", "无直接生产闭环"]:
    print("%-28s present=%s" % (kw, kw in full))
doc.close()
