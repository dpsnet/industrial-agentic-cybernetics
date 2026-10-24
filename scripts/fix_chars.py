# -*- coding: utf-8 -*-
"""PDF 版 md 字符净化：区分 代码块 / 数学模式 / 正文，把缺字形 Unicode 符号替换为 LaTeX 安全形式。
不改 docs 源；只改中间产物 manuscript-pdf.md -> manuscript-latex.md。"""
import io, re

SRC = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-pdf.md"
DST = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md"

TEXT_MAP = [
    ("\u27f9", r"$\Rightarrow$"),   # ⟹
    ("\u27fa", r"$\Leftrightarrow$"),  # ⟺
    ("\u2248", r"$\approx$"),        # ≈
    ("\u2264", r"$\le$"),            # ≤
    ("\u2265", r"$\ge$"),            # ≥
    ("\u2260", r"$\neq$"),           # ≠
    ("\u2208", r"$\in$"),            # ∈
    ("\u2227", r"$\wedge$"),         # ∧
    ("\u2194", r"$\leftrightarrow$"),# ↔
    ("\u03c3", r"$\sigma$"),         # σ
    ("\u03c1", r"$\rho$"),           # ρ
    ("\u03b1", r"$\alpha$"),         # α
    ("\u03b2", r"$\beta$"),          # β
    ("\u03b3", r"$\gamma$"),         # γ
    ("\u03bb", r"$\lambda$"),        # λ
    ("\u2074", r"$^{4}$"),           # ⁴
    ("\u2080", r"$_{0}$"),           # ₀
    ("\u2460", "(1)"),               # ①
    ("\u2461", "(2)"),               # ②
    ("\u2705", "\u3010\u901a\u8fc7\u3011"),   # ✅ -> 【通过】
    ("\u274c", "\u3010\u5931\u8d25\u3011"),   # ❌ -> 【失败】
    ("\u26a0", "\u3010\u8b66\u544a\u3011"),   # ⚠ -> 【警告】
    ("\ufe0f", ""),                  # emoji 变体选择符残留
    ("\U0001f7e1", "\u3010\u5f85\u5b9a\u3011"),  # 🟡 -> 【待定】
]
CODE_MAP = [
    ("\u27f9", "=>"), ("\u27fa", "<=>"), ("\u2248", "~="), ("\u2264", "<="),
    ("\u2265", ">="), ("\u2260", "!="), ("\u2208", "in "), ("\u2227", "and "),
    ("\u2194", "<->"), ("\u03c3", "sigma"), ("\u03c1", "rho"), ("\u03b1", "alpha"),
    ("\u03b2", "beta"), ("\u03b3", "gamma"), ("\u03bb", "lambda"), ("\u2074", "^4"),
    ("\u2080", "_0"), ("\u2460", "(1)"), ("\u2461", "(2)"),
    ("\u2705", "[PASS]"), ("\u274c", "[FAIL]"), ("\u26a0", "[WARN]"),
    ("\ufe0f", ""), ("\U0001f7e1", "[PEND]"),
]

def sub_map(s, mapping):
    for a, b in mapping:
        s = s.replace(a, b)
    return s

lines = io.open(SRC, encoding="utf-8").read().split("\n")
out = []
in_code = False
for ln in lines:
    if ln.startswith("```"):
        in_code = not in_code
        out.append(ln)
        continue
    if in_code:
        out.append(sub_map(ln, CODE_MAP))
        continue
    # 数学模式保护：按 $ 奇偶切换，跳过 $...$ 内部
    parts, buf, in_math, i = [], [], False, 0
    while i < len(ln):
        ch = ln[i]
        if ch == "$":
            if i + 1 < len(ln) and ln[i + 1] == "$":
                buf.append("$$"); i += 2; in_math = not in_math; continue
            buf.append("$"); i += 1; in_math = not in_math; continue
        if in_math:
            buf.append(ch); i += 1; continue
        # 正文：贪婪匹配映射（单字符）
        for a, b in TEXT_MAP:
            if ln.startswith(a, i):
                buf.append(b); i += len(a); break
        else:
            buf.append(ch); i += 1
    out.append("".join(buf))
io.open(DST, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("latex-md bytes:", __import__("os").path.getsize(DST))
