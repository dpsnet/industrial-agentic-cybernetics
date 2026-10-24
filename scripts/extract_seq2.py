# -*- coding: utf-8 -*-
import os
out_dir = r"E:\workspace\industrial-agentic-cybernetics\monograph"
srcs = [
    (r"E:\workspace\industrial-agentic-cybernetics\docs\part9-production-resilience\pattern-23-production-runtime-anomaly-sniffing.md", "p23_seq.mmd"),
    (r"E:\workspace\industrial-agentic-cybernetics\docs\part9-production-resilience\pattern-24-production-defect-crystallization-hotfix-loop.md", "p24_seq.mmd"),
]
for src, dst in srcs:
    text = open(src, encoding="utf-8").read()
    start = text.index("```mermaid") + len("```mermaid")
    end = text.index("\n```", start)
    code = text[start:end].strip() + "\n"
    open(os.path.join(out_dir, dst), "w", encoding="utf-8", newline="\n").write(code)
    n = len(code.splitlines())
    print("WROTE", dst, "chars=", len(code), "lines=", n)
    print("  first:", code.splitlines()[1][:50] if n > 1 else "")
    print("  last :", code.splitlines()[-2][:60] if n > 1 else "")
