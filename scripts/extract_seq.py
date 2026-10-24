# -*- coding: utf-8 -*-
import re, os
out_dir = r"E:\workspace\industrial-agentic-cybernetics\monograph"
fig = os.path.join(out_dir, "figures")
os.makedirs(fig, exist_ok=True)
srcs = [
    (r"E:\workspace\industrial-agentic-cybernetics\docs\part9-production-resilience\pattern-23-production-runtime-anomaly-sniffing.md", "p23_seq.mmd"),
    (r"E:\workspace\industrial-agentic-cybernetics\docs\part9-production-resilience\pattern-24-production-defect-crystallization-hotfix-loop.md", "p24_seq.mmd"),
]
for src, dst in srcs:
    text = open(src, encoding="utf-8").read()
    m = re.search(r"```mermaid\n(.*?)\n```", text, re.S)
    if not m:
        print("NO MATCH", src); continue
    open(os.path.join(out_dir, dst), "w", encoding="utf-8", newline="\n").write(m.group(1).strip() + "\n")
    print("WROTE", dst, len(m.group(1)))
print("figures m50/m51 exist:", os.path.exists(os.path.join(fig, "m50.png")), os.path.exists(os.path.join(fig, "m51.png")))
