# -*- coding: utf-8 -*-
"""提取 p164 文本层，判定数学是否字面输出还是正常渲染。"""
import pymupdf
doc = pymupdf.open(r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf")
t = doc[163].get_text("text", sort=True)
print("=== p164 raw text (dollar segments) ===")
import re
for m in re.finditer(r"\$\S{0,20}", t):
    s = m.group(0)
    print(repr(s))
print("=== contains literal '$' count:", t.count("$"))
print("=== contains U+03B3 gamma:", "\u03b3" in t, "| U+03B2 beta:", "\u03b2" in t, "| U+03BB lambda:", "\u03bb" in t)
print("=== around 'Spearman' ===")
i = t.find("Spearman")
print(repr(t[max(0,i-60):i+120]))
