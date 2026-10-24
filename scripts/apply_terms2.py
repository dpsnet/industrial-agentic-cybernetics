# -*- coding: utf-8 -*-
import os
pairs = [
('"注意力熵增"为隐喻命名：公理 II 的实际可操作量是', '"注意力稀释"为公理 II 的操作性命名：其实际可操作量是'),
("公理 II（注意力熵增）", "公理 II（注意力稀释）"),
("注意力熵增公理<br/>(Axiom of Attention Entropy)", "注意力稀释公理<br/>(Axiom of Attention Dilution)"),
]
roots = [r"E:\workspace\industrial-agentic-cybernetics\docs", r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md", r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md"]
files = []
for r in roots:
    if r.endswith(".md"): files.append(r)
    else:
        for dp, dn, fns in os.walk(r):
            for f in fns:
                if f.endswith(".md"): files.append(os.path.join(dp, f))
for f in files:
    t = open(f, encoding="utf-8").read()
    n = 0
    for old, new in pairs:
        c = t.count(old)
        if c:
            t = t.replace(old, new); n += c
    if n:
        open(f, "w", encoding="utf-8", newline="\n").write(t)
        print("OK", os.path.relpath(f, r"E:\workspace\industrial-agentic-cybernetics"), "+%d" % n)
print("done")
