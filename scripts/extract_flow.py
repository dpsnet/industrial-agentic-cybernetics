# -*- coding: utf-8 -*-
import os
out_dir = r"E:\workspace\industrial-agentic-cybernetics\monograph"
srcs = [
    (r"E:\workspace\industrial-agentic-cybernetics\docs\part9-production-resilience\pattern-23-production-runtime-anomaly-sniffing.md", "p23_flow.mmd"),
    (r"E:\workspace\industrial-agentic-cybernetics\docs\part9-production-resilience\pattern-24-production-defect-crystallization-hotfix-loop.md", "p24_flow.mmd"),
]
for src, dst in srcs:
    text = open(src, encoding="utf-8").read()
    pos = text.index("flowchart TD")
    start = text.rindex("```mermaid", 0, pos) + len("```mermaid")
    end = text.index("```", start)
    code = text[start:end].strip() + "\n"
    open(os.path.join(out_dir, dst), "w", encoding="utf-8", newline="\n").write(code)
    lines = code.splitlines()
    print("WROTE", dst, "lines=", len(lines), "| first:", lines[0][:30], "| last:", lines[-2][:30] if len(lines) > 1 else "")
