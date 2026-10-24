# -*- coding: utf-8 -*-
import re
path = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md"
text = open(path, encoding="utf-8").read()

# 匹配缩进 mermaid 块：```mermaid 后紧跟 flowchart TD，到闭合 ```
pat = re.compile(r"```mermaid\nflowchart TD\n.*?\n```", re.S)
ms = list(pat.finditer(text))
print("blocks found:", len(ms))
assert len(ms) == 2, "expect exactly 2 blocks"

repls = [
    (ms[0], "m52.jpg", "模式 23：隔离环境审计与三维异常嗅探维度流程", "45%"),
    (ms[1], "m53.jpg", "模式 24：缺陷萃取-验证-晋升-免疫闭环流程", "50%"),
]
# 逆序替换
for m, fig, title, w in reversed(repls):
    new = "![%s 示意](figures/%s){width=%s}\n" % (title, fig, w)
    text = text[:m.start()] + new + text[m.end():]
open(path, "w", encoding="utf-8", newline="\n").write(text)
print("after: flowchart TD count =", text.count("flowchart TD"))
print("after: subgraph count =", text.count("subgraph"))
print("after: mermaid block count =", text.count("```mermaid"))
