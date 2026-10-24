# -*- coding: utf-8 -*-
for p in [r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md", r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md"]:
    t = open(p, encoding="utf-8").read()
    n = t.count("模式在工业场景中必然触发以下三类严重失效")
    t = t.replace("模式在工业场景中必然触发以下三类严重失效", "模式在工业场景中极易触发以下三类严重失效")
    open(p, "w", encoding="utf-8", newline="\n").write(t)
    print(p.split("\\")[-1], "changed", n)
