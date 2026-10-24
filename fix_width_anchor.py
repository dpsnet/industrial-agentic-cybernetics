# -*- coding: utf-8 -*-
import io
p1 = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md"
p2 = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md"

def fix(p, width):
    c = io.open(p, encoding="utf-8").read()
    nw = c.count("{width=85%}")
    c = c.replace("{width=85%}", "{width=%s}" % width)
    # 锚点：A.5 标题加自定义 identifier，使链接 #a5-参考文献-references 可解析
    if "## A.5 参考文献（References）{#a5-参考文献-references}" not in c:
        c = c.replace("## A.5 参考文献（References）",
                      "## A.5 参考文献（References）{#a5-参考文献-references}")
    io.open(p, "w", encoding="utf-8").write(c)
    return nw

print("latex md width=85% count:", fix(p1, 80))
print("merged width=85% count:", fix(p2, 80))
