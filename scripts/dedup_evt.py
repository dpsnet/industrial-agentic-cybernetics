# -*- coding: utf-8 -*-
import os
marker = "#### 3.2.1 四公理证据等级总览"
ax = "#### 公理 I：物理非信任公理（Axiom of Physical Non-Trustworthiness）"
for f in [r"E:\workspace\industrial-agentic-cybernetics\docs\preface\03-axioms-and-invariance.md", r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md", r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md"]:
    t = open(f, encoding="utf-8").read()
    if t.count(marker) > 1:
        i1 = t.find(marker); i2 = t.find(marker, i1+1); ia = t.find(ax)
        assert i2 > i1 and ia > i2, (os.path.basename(f), i1, i2, ia)
        t = t[:i2] + t[ia:]
        open(f, "w", encoding="utf-8", newline="\n").write(t)
        print("FIXED", os.path.basename(f), "marker now", t.count(marker))
    else:
        print("clean", os.path.basename(f), t.count(marker))
