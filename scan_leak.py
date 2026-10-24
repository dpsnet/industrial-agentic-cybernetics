# -*- coding: utf-8 -*-
"""找 md 中所有行内数学 $...$ 关闭 $ 后紧跟字母/数字（pandoc 数学边界泄漏）的位置。"""
import io, re
p = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md"
lines = io.open(p, encoding="utf-8").read().split("\n")
in_code = False
hits = []
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    if s.startswith("```"):
        in_code = not in_code
        continue
    if in_code:
        continue
    # 逐字符找 $ 配对（粗略：按奇数位），检查关 $ 后字符
    # 用正则找所有 $...$（非贪婪，行内）
    for m in re.finditer(r"\$([^$\n]+?)\$", ln):
        seg = m.group(1)
        after = ln[m.end():m.end()+1] if m.end() < len(ln) else ""
        if after and re.match(r"[A-Za-z0-9]", after):
            hits.append((i, "$" + seg + "$", "after='%s'" % after, ln[:150]))
print("leak candidates:", len(hits))
for i, m, a, ln in hits:
    print("L%d: %s | %s" % (i, m, a))
    print("    %s" % ln)
