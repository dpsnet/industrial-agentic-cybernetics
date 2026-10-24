# -*- coding: utf-8 -*-
import pymupdf
pdf = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf"
doc = pymupdf.open(pdf)
full = "\n".join(p.get_text("text", sort=True) for p in doc)
for kw in ["穿透者伪装交付物", "一票否决判据链", "脚手架冻结", "最小特权投影", "断点续跑与因果快照", "导航-驱动结对", "隐式分支", "幂等日志-物理时钟", "租约仲裁-锁状态", "写拦截-影子工作区", "协议桥接-锁协商", "单源萃取", "草稿-知识库-晋升门禁", "污点追踪", "手风琴多分辨率", "中断-安全点", "隐藏 Oracle 隔离测评", "五重判据", "A/B 双沙箱", "剪枝-缓存-LLM", "原生直连"]:
    print("%-24s count=%d" % (kw, full.count(kw)))
doc.close()
