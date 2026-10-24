p = r"E:\workspace\industrial-agentic-cybernetics\apply_kimi.py"
t = open(p, encoding="utf-8").read()
t = t.replace("import re\n", "import os, re\n", 1)
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("fixed")
