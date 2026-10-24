# -*- coding: utf-8 -*-
import pymupdf
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
full = "\n".join(p.get_text("text", sort=True) for p in doc)
print("pages=%d images=%d" % (doc.page_count, sum(len(p.get_images(full=True)) for p in doc)))
for kw in ["彻底", "注意力熵增", "Attention Entropy", "灾难性失效", "灾难性设计缺陷", "成瘾性"]:
    print("%-16s count=%d" % (kw, full.count(kw)))
for kw in ["全书术语约定（导读）", "注意力稀释与特权发散公理", "Axiom of Attention Dilution", "术语锚定】：「自免疫」为工程借喻", "修辞语；所指机制为公理 IV 的经验自免疫收敛", "受控实验普遍观测到奖励欺骗", "倾向伪造测试", "极易触发以下三类严重失效", "杜绝“虚假繁荣”（所测环境与任务族内"]:
    print("%-30s present=%s" % (kw[:28], kw in full))
doc.close()
