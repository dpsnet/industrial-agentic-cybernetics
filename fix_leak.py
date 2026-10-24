# -*- coding: utf-8 -*-
"""修复 md 中行内数学 $...$ 关闭 $ 后紧跟字母/数字导致的 pandoc 数学边界泄漏：
在关闭 $ 后补一个空格。只处理 $ 内为 LaTeX 命令/短式的情形（长度<=24 且以 \ 开头，或匹配常见符号命令）。
"""
import io, re

def fix(p):
    c = io.open(p, encoding="utf-8").read()
    # 逐行处理，跳过代码块
    lines = c.split("\n")
    out = []
    in_code = False
    n = [0]
    for ln in lines:
        s = ln.strip()
        if s.startswith("```"):
            in_code = not in_code
            out.append(ln)
            continue
        if in_code:
            out.append(ln)
            continue
        def repl(m):
            seg = m.group(1)
            # 仅处理看起来像符号命令的短数学段（防止误伤长公式）
            if len(seg) <= 24 and (seg.startswith("\\") or re.match(r"^[\\]?[A-Za-z]+$", seg)):
                n[0] += 1
                return "$%s$ " % seg
            return m.group(0)
        ln2 = re.sub(r"\$([^$\n]+?)\$(?=[A-Za-z0-9])", repl, ln)
        out.append(ln2)
    io.open(p, "w", encoding="utf-8").write("\n".join(out))
    return n

a = fix(r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md")
print("latex md fixed:", a)
b = fix(r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md")
print("merged fixed:", b)
