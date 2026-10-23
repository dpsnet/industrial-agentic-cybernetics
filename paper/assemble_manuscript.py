# -*- coding: utf-8 -*-
"""Assemble paper/manuscript.md from sections (single-source).

Strips per-section work-note header blocks, inserts figure refs,
prepends title+abstract, appends unified reference list.
"""
import io, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(ROOT, "sections")

ORDER = [
    "01-introduction.md",
    "02-related-work.md",
    "03-model.md",
    "04-formalization.md",
    "05-experimental-setup.md",
    "06-results.md",
    "07-discussion.md",
    "08-mechanism-revision.md",
    "09-scope.md",
    "10-limitations.md",
    "11-conclusion.md",
]

def strip_header(text):
    """Remove leading title/status note block (lines starting with '# ', '>', '---', blank)."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s == "" or s.startswith(">") or s == "---" or s.startswith("# "):
            i += 1
            continue
        break
    body = "\n".join(lines[i:])
    return body.strip() + "\n"

def load_abstract():
    text = open(os.path.join(ROOT, "abstract.md"), encoding="utf-8").read()
    m = re.search(r"^## 摘要（定稿）\s*\n(.*)$", text, re.M | re.S)
    if m is None:
        raise RuntimeError("abstract section not found")
    return m.group(1).strip() + "\n"

TITLE_ZH = "# 无门控智能体记忆架构中的记忆投毒：架构依赖的传播机制、容量控制与隔离不变性\n"

def main():
    parts = []
    parts.append(TITLE_ZH)
    parts.append(load_abstract() + "\n")
    parts.append("---\n")
    parts.append("## 1 引言\n")
    parts.append(strip_header(open(os.path.join(SEC, "01-introduction.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 2 背景与相关工作\n")
    parts.append(strip_header(open(os.path.join(SEC, "02-related-work.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 3 模型\n")
    parts.append(strip_header(open(os.path.join(SEC, "03-model.md"), encoding="utf-8").read()) + "\n")
    parts.append("![机制示意：分支衰减（选择性转写）与线性累积-容量竞争（全量追加）](figures/fig-mechanism.png)\n")
    parts.append("*图 1  两种传播机制：A）选择性转写下的分支衰减（Galton-Watson 分支过程、几何律，灭绝概率=最小不动点）；B）全量追加下的线性累积-容量竞争（每代写入 $w_n\\in\\{0,1\\}$、链均 $E[w_n]=0.917$，容量 $M$ 处 FIFO 竞争，临界 $M_c\\in(8,16)$）。*（数据：DeepSeek-V4.1-Flash-1017，链均）\n")
    parts.append("## 4 形式化\n")
    parts.append(strip_header(open(os.path.join(SEC, "04-formalization.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 5 实验设置\n")
    parts.append(strip_header(open(os.path.join(SEC, "05-experimental-setup.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 6 结果\n")
    parts.append(strip_header(open(os.path.join(SEC, "06-results.md"), encoding="utf-8").read()) + "\n")
    parts.append("![按架构与容量划分的各代毒株谱系轨迹](figures/fig-trajectories.png)\n")
    parts.append("*图 2  全量追加各条件在容量 $M\\in\\{8,16,32\\}$ 下与选择性对照（$M=16$）的各代毒株谱系条目数。临界带 $8<M_c\\leq16$ 区分灭绝与持续。数据：DeepSeek-V4.1-Flash-1017，链均。*\n")
    parts.append("## 7 讨论\n")
    parts.append(strip_header(open(os.path.join(SEC, "07-discussion.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 8 机制修正叙事\n")
    parts.append(strip_header(open(os.path.join(SEC, "08-mechanism-revision.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 9 适用域与可推广性\n")
    parts.append(strip_header(open(os.path.join(SEC, "09-scope.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 10 局限与未来工作\n")
    parts.append(strip_header(open(os.path.join(SEC, "10-limitations.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 11 结论\n")
    parts.append(strip_header(open(os.path.join(SEC, "11-conclusion.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 附录\n")
    parts.append(strip_header(open(os.path.join(ROOT, "appendix.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 参考文献\n")
    parts.append("""1. Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). *Concrete Problems in AI Safety*. arXiv:1606.06565.
2. Anthropic Alignment Team (2025). *Natural emergent misalignment from reward hacking in production RL*. arXiv:2511.18397.
3. Brooks, F. P. (1987). *No Silver Bullet: Essence and Accidents of Software Engineering*. IEEE Computer, 20(4), 10–19. DOI: 10.1109/MC.1987.1663532.
4. Chroma Research (2024). *Context Rot: How Increasing Input Tokens Impacts LLM Performance*. Technical Report.
5. Conway, M. E. (1968). *How do committees invent?* Datamation, 14(4), 28–31.
6. Gilbert, S., & Lynch, N. (2002). *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services*. ACM SIGACT News, 33(2), 51–59. DOI: 10.1145/564585.564601.
7. Harris, T. E. (1963). *The Theory of Branching Processes*. Springer.
8. Hsieh, C.-P., et al. (2024). *RULER: What's the Real Context Size of Your Long-Context Language Models?* arXiv:2404.06654.
9. Krakovna, V., et al. (2020). *Specification Gaming: The Flip Side of AI Ingenuity*. DeepMind Blog.
10. Lehman, M. M. (1980). *Programs, Life Cycles, and Laws of Software Evolution*. Proceedings of the IEEE, 68(9), 1060–1076. DOI: 10.1109/PROC.1980.11805.
11. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. TACL, 12.
12. MemoryGraft (2025). *Persistent Compromise of LLM Agents via Poisoned Experience Retrieval*. arXiv:2512.16962.
13. Moura, L., & Ullrich, S. (2021). *The Lean 4 Theorem Prover and Programming Language*. CADE-28, LNCS 12699, 625–635. DOI: 10.1007/978-3-030-79876-5_40.
14. OEP (2026). *Poisoning Self-Evolving LLM Agents via Locally Correct but Non-Transferable Experiences*. arXiv:2605.18930.
15. Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). *AI models collapse when trained on recursively generated data*. Nature, 631, 755–759. DOI: 10.1038/s41586-024-07566-y.
16. Turing, A. M. (1936). *On Computable Numbers, with an Application to the Entscheidungsproblem*. Proceedings of the LMS, 42, 230–265.
17. Zhan, Q., et al. (2024). *AgentPoison: Red-Teaming LLM Agents via Memory Engineering or Malicious Tool Manipulation*. NeurIPS 2024. arXiv:2407.12784.
18. (2026). *Defense Effectiveness Across Architectural Layers*. arXiv:2605.08442.
""")

    out = os.path.join(ROOT, "manuscript.md")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    # report word count of body (approx)
    body = "\n".join(parts)
    words = len(re.findall(r"\S+", body))
    print("manuscript.md written, ~%d words, %.1f KB" % (words, len(body.encode("utf-8"))/1024))

if __name__ == "__main__":
    main()
