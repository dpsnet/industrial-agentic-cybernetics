# -*- coding: utf-8 -*-
"""在 pandoc 生成的 tex 中找出所有数学环境（\(...\)、$$...$$）内含 CJK 的位置。"""
import io, re
p = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-check.tex"
c = io.open(p, encoding="utf-8").read()
lines = c.split("\n")

def has_cjk(s):
    return any('\u4e00' <= ch <= '\u9fff' for ch in s)

# 逐行 + 跨行处理 \(...\)
pat = re.compile(r"\\\((.+?)\\\)", re.S)
buf = "\n".join(lines)
hits = []
for m in pat.finditer(buf):
    seg = m.group(1)
    if has_cjk(seg):
        # 定位行号
        ln = buf[:m.start()].count("\n") + 1
        hits.append((ln, seg[:200]))
print("math envs containing CJK:", len(hits))
for ln, seg in hits[:30]:
    print("L%d: %s" % (ln, seg))
# $$ 块
for m in re.finditer(r"\$\$(.+?)\$\$", buf, re.S):
    seg = m.group(1)
    if has_cjk(seg):
        ln = buf[:m.start()].count("\n") + 1
        print("DISP L%d: %s" % (ln, seg[:200]))
