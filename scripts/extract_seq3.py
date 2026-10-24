# -*- coding: utf-8 -*-
import os
out_dir = r"E:\workspace\industrial-agentic-cybernetics\monograph"
srcs = [
    (r"E:\workspace\industrial-agentic-cybernetics\docs\part9-production-resilience\pattern-23-production-runtime-anomaly-sniffing.md", "p23_seq.mmd"),
    (r"E:\workspace\industrial-agentic-cybernetics\docs\part9-production-resilience\pattern-24-production-defect-crystallization-hotfix-loop.md", "p24_seq.mmd"),
]
for src, dst in srcs:
    text = open(src, encoding="utf-8").read()
    sec = text.index("### 5. 协作协议与因果约束")
    start = text.index("```mermaid", sec) + len("```mermaid")
    end = text.index("\n```", start)
    code = text[start:end].strip() + "\n"
    open(os.path.join(out_dir, dst), "w", encoding="utf-8", newline="\n").write(code)
    lines = code.splitlines()
    print("WROTE", dst, "chars=", len(code), "lines=", len(lines))
    print("  first:", lines[0][:60])
    print("  last :", lines[-2][:60])
