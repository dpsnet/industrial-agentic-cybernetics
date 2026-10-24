# -*- coding: utf-8 -*-
import re, os
base = r"E:\workspace\industrial-agentic-cybernetics"
md_path = base + r"\monograph\manuscript-latex.md"
lines = open(md_path, encoding="utf-8").read().split("\n")
cap_pat = re.compile(r"^!\[(.*?)\]\(figures/(m\d+)\.jpg\)")
head_pat = re.compile(r"^# 模式 (\d+)：")
title = "前篇"
out = []
for i, l in enumerate(lines, 1):
    m = head_pat.match(l.strip())
    if m:
        title = l.strip()
    c = cap_pat.match(l.strip())
    if c and c.group(2) in ("m4","m5","m6","m7","m8","m9","m10","m11","m12","m13","m14","m15","m16","m17","m18","m19","m20","m21","m22","m23","m24","m25","m26","m27","m30","m32","m34","m36","m38","m40","m43","m45","m47","m49"):
        out.append((i, c.group(2), title))
for i, m, t in out:
    mmd = base + r"\monograph\figures\%s.mmd" % m
    head = ""
    if os.path.exists(mmd):
        txt = open(mmd, encoding="utf-8").read()
        parts = [x.strip() for x in txt.split("\n") if x.strip()]
        head = parts[0][:60] if parts else "(empty)"
    print("L%-5d %-4s | %s | mmd: %s" % (i, m, t, head))
