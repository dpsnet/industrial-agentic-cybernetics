# -*- coding: utf-8 -*-
"""Remove ALL brackets from headings: chapter-level work notes and section-level qualifiers.
Bracket content is folded into the title, deleted, or already stated in body text."""
import io, glob, re

# 1) chapter-level work notes (zh): （论文全文扩写）
for f in glob.glob(r"E:\workspace\industrial-agentic-cybernetics\paper\sections\*.md"):
    s = io.open(f, encoding="utf-8").read()
    new = re.sub(r"^# (.*)（论文全文扩写）$", r"# \1", s, flags=re.M)
    if new != s:
        io.open(f, "w", encoding="utf-8", newline="\n").write(new)
        print("ZH chapter:", f.split("\\")[-1])

# 2) chapter-level work notes (en): (English, for manuscript-en.md) / (Full Paper Expansion)
for f in glob.glob(r"E:\workspace\industrial-agentic-cybernetics\paper\sections_en\*.md"):
    s = io.open(f, encoding="utf-8").read()
    new = re.sub(r"^# (.*) \(English, for manuscript-en\.md\)$", r"# \1", s, flags=re.M)
    new = re.sub(r"^# (.*) \(Full Paper Expansion\)$", r"# \1", new, flags=re.M)
    if new != s:
        io.open(f, "w", encoding="utf-8", newline="\n").write(new)
        print("EN chapter:", f.split("\\")[-1])

# 3) section-level headings (zh)
S = r"E:\workspace\industrial-agentic-cybernetics\paper\sections"
E = r"E:\workspace\industrial-agentic-cybernetics\paper\sections_en"
jobs = [
    (S + r"\07-capacity-regulation.md", "## 7.1 控制律（bang-bang）", "## 7.1 bang-bang 控制律"),
    (S + r"\07-capacity-regulation.md", "## 7.2 稳定性条件（反馈带宽）", "## 7.2 反馈带宽下的稳定性条件"),
    (S + r"\07-capacity-regulation.md", "## 7.3 三方案权衡面（推导与基线锚定）", "## 7.3 三方案权衡面"),
    (S + r"\07-capacity-regulation.md", "## 7.4 实验方案与预期效果（预先注册）", "## 7.4 预先注册的实验方案与预期效果"),
    (S + r"\08-discussion.md", "## 8.1 防御依赖隔离而非标记（核心工程结论）", "## 8.1 防御依赖隔离而非标记"),
    (S + r"\08-discussion.md", "## 8.2 架构决定机制（理论结论）", "## 8.2 架构决定机制"),
    (S + r"\10-scope.md", "## 10.1 适用边界（四重）", "## 10.1 适用边界"),
    (E + r"\07-capacity-regulation.md", "## 7.1 Control law (bang-bang)", "## 7.1 Bang-bang Control Law"),
    (E + r"\07-capacity-regulation.md", "## 7.2 Stability condition (feedback bandwidth)", "## 7.2 Stability Condition under Feedback Bandwidth"),
    (E + r"\07-capacity-regulation.md", "## 7.3 Three-scheme trade-off (derivation and baseline anchoring)", "## 7.3 Three-Scheme Trade-off"),
    (E + r"\07-capacity-regulation.md", "## 7.4 Experimental protocol and expected effects (pre-registered)", "## 7.4 Pre-registered Experimental Protocol and Expected Effects"),
    (E + r"\08-discussion.md", "## 8.1 Defense Depends on Quarantine, Not Marking (Core Engineering Conclusion)", "## 8.1 Defense Depends on Quarantine, Not Marking"),
    (E + r"\08-discussion.md", "## 8.2 Architecture Determines Mechanism (Theoretical Conclusion)", "## 8.2 Architecture Determines Mechanism"),
    (E + r"\10-scope.md", "## 10.1 Applicability Boundaries (Four)", "## 10.1 Applicability Boundaries"),
]
ok = fail = 0
for path, old, new in jobs:
    s = io.open(path, encoding="utf-8").read()
    n = s.count(old)
    if n != 1:
        print("WARN %s got %d: %s" % (path.split("\\")[-1], n, old[:60]))
        fail += 1
        continue
    io.open(path, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    ok += 1
print("section headings applied %d, failed %d" % (ok, fail))
