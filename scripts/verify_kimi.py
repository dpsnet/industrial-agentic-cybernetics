# -*- coding: utf-8 -*-
import os
files = [r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md", r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md", r"E:\workspace\industrial-agentic-cybernetics\docs\preface\01-paradigm-shift.md", r"E:\workspace\industrial-agentic-cybernetics\docs\preface\03-axioms-and-invariance.md", r"E:\workspace\industrial-agentic-cybernetics\docs\appendix-formal-proofs.md", r"E:\workspace\industrial-agentic-cybernetics\docs\axioms-validation-report.md"]
for f in files:
    t = open(f, encoding="utf-8").read()
    print("%-40s EVT=%d PEER=%d IND=%d 已证改=%d 全部已证残=%d" % (os.path.basename(f), t.count("四公理证据等级总览"), t.count("同行现状说明"), t.count("『工业级』口径声明"), t.count("（形式化层全部已证）"), t.count("（全部已证）")))
