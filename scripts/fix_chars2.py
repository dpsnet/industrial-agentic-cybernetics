# -*- coding: utf-8 -*-
"""二轮净化：① Unicode 数学字母（U+1D400-1D7FF 及希腊系列）→ LaTeX 命令
② 图片引用加宽度属性 ③ 生成 header.tex（数学字体 CJK range 兜底）。"""
import io, os, re

BASE = r"E:\workspace\industrial-agentic-cybernetics\monograph"
SRC = os.path.join(BASE, "manuscript-latex.md")
HDR = os.path.join(BASE, "latex-header.tex")

# --- 希腊序列映射 ---
CAPS = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota",
        "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma", "Tau",
        "Upsilon", "Phi", "Chi", "Psi", "Omega"]
SMALL = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota",
         "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau",
         "upsilon", "phi", "chi", "psi", "omega"]

def tex_of_greek(cap_cmd, small_cmd, is_cap):
    """LaTeX 命令（unicode-math 命名与 LaTeX 一致，除 epsilon/phi 用 variants）。"""
    if is_cap:
        return r"\mathrm{%s}" % cap_cmd  # 大写：用 \mathrm 拉丁/命令形式
    return r"\%s" % small_cmd

# 小写 LaTeX 名（epsilon->varepsilon, phi->varphi? 保留 phi 以保语义）
LATEX_SMALL = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
               "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
               "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]
LATEX_CAPS = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
              "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
              "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"]

def greek_cmd(idx, is_cap):
    n = LATEX_CAPS[idx] if is_cap else LATEX_SMALL[idx]
    return r"\%s" % n

def build_math_greek_map():
    m = {}
    # 各样式起点（大写下标0=Α，小写下标0=α），序列均为 24
    styles = [
        (0x1D6A8, 0x1D6C2, "bold"),
        (0x1D6E2, 0x1D6FC, "italic"),
        (0x1D71C, 0x1D736, "bolditalic"),
    ]
    for cap0, sm0, name in styles:
        for i in range(24):
            m[chr(cap0 + i)] = greek_cmd(i, True)
            m[chr(sm0 + i)] = greek_cmd(i, False)
    # unicode-math 的 variant 字形：1D6C0 ε? 补齐 ς/Ϝ 等不映射（保守跳过）
    return m

GREEK = build_math_greek_map()
# 拉丁数学字母（斜体/粗体 A-Z a-z）→ 对应拉丁字符（文本模式中直接取普通字母，数学用 \mathit）
LATIN_MATH = {}
for c0, c1 in [(0x1D400, 0x1D419), (0x1D434, 0x1D44D), (0x1D468, 0x1D481),
               (0x1D49C, 0x1D4B5), (0x1D4D0, 0x1D4E9), (0x1D504, 0x1D51D),
               (0x1D538, 0x1D551)]:  # 常见 Latin math italic/bold 区（部分含伪字符，跳过无效）
    for cp in range(c0, c1 + 1):
        ch = chr(cp)
        if 0x1D400 <= cp <= 0x1D419:  # bold cap
            LATIN_MATH[ch] = chr(0x41 + (cp - 0x1D400))
        elif 0x1D434 <= cp <= 0x1D44D:  # italic cap
            LATIN_MATH[ch] = chr(0x41 + (cp - 0x1D434))
        elif 0x1D468 <= cp <= 0x1D481:  # bold small
            LATIN_MATH[ch] = chr(0x61 + (cp - 0x1D468))
        elif 0x1D4D0 <= cp <= 0x1D4E9:  # bold italic small
            LATIN_MATH[ch] = chr(0x61 + (cp - 0x1D4D0))

TEXT_MAP = [(a, "$%s$" % b) for a, b in GREEK.items()] + [(a, "$%s$" % b) for a, b in LATIN_MATH.items()]
CODE_MAP = [(a, b.strip("\\")) for a, b in GREEK.items()] + list(LATIN_MATH.items())

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
    parts, buf, in_math, i = [], [], False, 0
    while i < len(ln):
        ch = ln[i]
        if ch == "$":
            if i + 1 < len(ln) and ln[i + 1] == "$":
                buf.append("$$"); i += 2; in_math = not in_math; continue
            buf.append("$"); i += 1; in_math = not in_math; continue
        if in_math:
            buf.append(ch); i += 1; continue
        hit = None
        for a, b in TEXT_MAP:
            if ln.startswith(a, i):
                hit = (a, b); break
        if hit:
            buf.append(hit[1]); i += len(hit[0])
        else:
            buf.append(ch); i += 1
    out.append("".join(buf))
text = "\n".join(out)

# 图片宽度：![alt](figures/mN.png) -> {width=85%}
text = re.sub(r"(!\[图（mermaid 渲染）\]\(figures/m\d+\.png\))(\s*\n)", lambda m: m.group(1) + "{width=85%}" + m.group(2), text)
io.open(SRC, "w", encoding="utf-8", newline="\n").write(text)
print("latex-md updated bytes:", os.path.getsize(SRC))

# header.tex：数学模式下中文/全角字符 fallback 到 SimSun
hdr = r"""% 数学模式 CJK 兜底（latinmodern-math 无 CJK 字形）
\setmathfont{SimSun}[range={"4E00-"9FFF,"3000-"303F,"FF00-"FFEF,"2010-"2015},BoldFont=SimHei]
% 超宽浮动限制
\usepackage{graphicx}
\PassOptionsToPackage{hyphens}{url}
"""
io.open(HDR, "w", encoding="utf-8", newline="\n").write(hdr)
print("header written:", os.path.getsize(HDR))
