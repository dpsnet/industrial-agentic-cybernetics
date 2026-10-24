# -*- coding: utf-8 -*-
import re

new_refs = [
"21. Xie, et al. (2026). *From Spark to Fire: Modeling and Mitigating Error Cascades in LLM-Based Multi-Agent Collaboration*. arXiv:2603.04474.",
"22. Zhu, K., et al. (2025). *Where LLM Agents Fail and How They Can Learn From Failures*. arXiv:2509.25370.",
"23. Chen, Y., et al. (2026). *OrchestraBench: Evaluating Multi-Agent Orchestration Failure Modes, Recovery, and Decomposition Quality*. arXiv:2608.05263.",
"24. Thaman, K., et al. (2026). *Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use*. arXiv:2605.02964.",
"25. Roth, A., et al. (2026). *Hack-Verifiable Environments: Towards Evaluating Reward Hacking at Scale*. arXiv:2605.20744.",
]

files = [
    r"E:\workspace\industrial-agentic-cybernetics\docs\terminology-mapping.md",
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md",
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md",
]
body_files = [
    r"E:\workspace\industrial-agentic-cybernetics\docs\preface\02-compliance-theater.md",
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md",
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md",
]

old_tail = "，且 exploit 呈成瘾性——一次成功后几乎必然再次采用（arXiv:2605.20744）"

for path in body_files:
    t = open(path, encoding="utf-8").read()
    n = t.count(old_tail)
    t = t.replace(old_tail, "")
    open(path, "w", encoding="utf-8", newline="\n").write(t)
    print("BODY", path.split("\\")[-1], "removed", n)

for path in files:
    t = open(path, encoding="utf-8").read()
    m = re.search(r"20\. Kapoor[^\n]*\n", t)
    if not m:
        print("NO-ANCHOR", path.split("\\")[-1]); continue
    t = t[:m.end()] + "\n".join(new_refs) + "\n" + t[m.end():]
    open(path, "w", encoding="utf-8", newline="\n").write(t)
    print("REFS", path.split("\\")[-1], "ok; 25-present =", ("25. Roth" in t))
