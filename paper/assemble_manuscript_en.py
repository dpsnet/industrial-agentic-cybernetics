# -*- coding: utf-8 -*-
"""Assemble paper/manuscript-en.md from English sections (single-source).

Strips per-section work-note header blocks, inserts figure refs,
prepends English title+abstract, appends unified reference list.
"""
import io, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(ROOT, "sections_en")

ORDER = [
    "01-introduction.md",
    "02-related-work.md",
    "03-model.md",
    "04-formalization.md",
    "05-experimental-setup.md",
    "06-results.md",
    "07-capacity-regulation.md",
    "08-discussion.md",
    "09-mechanism-revision.md",
    "10-scope.md",
    "11-limitations.md",
    "12-conclusion.md",
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
    text = open(os.path.join(ROOT, "abstract_en.md"), encoding="utf-8").read()
    m = re.search(r"^## Abstract\s*\n(.*)$", text, re.M | re.S)
    if m is None:
        raise RuntimeError("abstract_en section not found")
    return m.group(1).strip() + "\n"

TITLE_EN = "# Memory Poisoning in Ungated Agentic Memory Architectures: Architecture-Dependent Propagation Mechanisms, Capacity Control, and Quarantine Invariance\n"
AUTHOR_EN = "**Bin Wang**\n\nBeijing Kailuzhe Technology Co., Ltd. · Technical Lead\n\n"

def main():
    parts = []
    parts.append(TITLE_EN)
    parts.append(AUTHOR_EN)
    parts.append(load_abstract() + "\n")
    parts.append("---\n")
    parts.append("## 1. Introduction\n")
    parts.append(strip_header(open(os.path.join(SEC, "01-introduction.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 2. Background and Related Work\n")
    parts.append(strip_header(open(os.path.join(SEC, "02-related-work.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 3. Model\n")
    parts.append(strip_header(open(os.path.join(SEC, "03-model.md"), encoding="utf-8").read()) + "\n")
    parts.append("![Mechanism schematic: branching decay (selective replay) vs. linear accumulation-competition (full append)](figures/fig-mechanism.png)\n")
    parts.append("*Figure 1. Two propagation mechanisms: A) branching decay under selective replay (Galton-Watson, geometric law, extinction probability = least fixed point); B) linear accumulation-competition under full append (per-generation write $w_n\\in\\{0,1\\}$, chain mean $E[w_n]=0.917$, FIFO competition at capacity $M$, critical $M_c\\in(8,16)$ (low-transcription-state reading)).* (data: DeepSeek-V4.1-Flash-1017, chain means)\n")
    parts.append("## 4. Formalization\n")
    parts.append(strip_header(open(os.path.join(SEC, "04-formalization.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 5. Experimental Setup\n")
    parts.append(strip_header(open(os.path.join(SEC, "05-experimental-setup.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 6. Results\n")
    parts.append(strip_header(open(os.path.join(SEC, "06-results.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 7. Capacity Regulation under State Feedback\n")
    parts.append(strip_header(open(os.path.join(SEC, "07-capacity-regulation.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 8. Discussion\n")
    parts.append(strip_header(open(os.path.join(SEC, "08-discussion.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 9. Mechanism Revision Narrative\n")
    parts.append(strip_header(open(os.path.join(SEC, "09-mechanism-revision.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 10. Scope and Generalizability\n")
    parts.append(strip_header(open(os.path.join(SEC, "10-scope.md"), encoding="utf-8").read()) + "\n")
    parts.append("## 11. Limitations and Future Work\n")
    parts.append(strip_header(open(os.path.join(SEC, "11-limitations.md"), encoding="utf-8").read()) + "\n")
    parts.append("![Deployment cost-benefit of state-feedback capacity regulation](figures/fig-deployment.png)\n")
    parts.append("*Figure 3  Deployment cost-benefit of state-feedback capacity regulation: batch cost of a 12-chain controlled batch (bars, k credits) vs. poison survival and memory-utility retention (lines; high-state three-window merged readings, §11.4). Cost rises from gated (34,580) to companion 1:2 (50,540 credits) while safety and utility stay identical—the probe increment buys within-batch drift exercisability (switching dynamics, untested), not direct safety; quarantine has zero increment with zero poison survival and 0.88 utility retention, at the cost of memory-freeze availability loss. Data: DeepSeek-V4.1-Flash-1017; Flash 1 token = 0.19 credits, one chain ≈ 2,660 credits.*\n")
    parts.append("## 12. Conclusion\n")
    parts.append(strip_header(open(os.path.join(SEC, "12-conclusion.md"), encoding="utf-8").read()) + "\n")
    parts.append("## Appendix\n")
    parts.append(strip_header(open(os.path.join(ROOT, "appendix_en.md"), encoding="utf-8").read()) + "\n")
    parts.append("## References\n")
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
18. Leong, J. W., et al. (2026). *Defense Effectiveness Across Architectural Layers: A Mechanistic Evaluation of Persistent Memory Attacks on Stateful LLM Agents*. arXiv:2605.08442.
""")

    out = os.path.join(ROOT, "manuscript-en.md")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    body = "\n".join(parts)
    words = len(re.findall(r"\S+", body))
    print("manuscript-en.md written, ~%d words, %.1f KB" % (words, len(body.encode("utf-8"))/1024))

if __name__ == "__main__":
    main()
