# -*- coding: utf-8 -*-
import os, re
base = r"E:\workspace\industrial-agentic-cybernetics\monograph\figures"
mids = ["m4","m6","m8","m10","m12","m14","m16","m18","m20","m22","m24","m26","m29","m31","m33","m35","m37","m39","m42","m44","m46","m48","m5","m7","m9","m11","m13","m15","m17","m19","m21","m23","m25","m27","m30","m32","m34","m36","m38","m40","m43","m45","m47","m49"]
node_pat = re.compile(r"^\s*(\w+)\s*\[([^\]]{2,60})\]")
part_pat = re.compile(r"^\s*participant\s+(\S+)")
for m in mids:
    p = os.path.join(base, m + ".mmd")
    if not os.path.exists(p):
        print(m, "NO-MMD"); continue
    txt = open(p, encoding="utf-8").read()
    first = txt.strip().split("\n")[0].strip()
    nodes = []
    parts = []
    for ln in txt.split("\n"):
        nm = node_pat.match(ln)
        if nm and nm.group(2) not in nodes:
            nodes.append(nm.group(2))
        pm = part_pat.match(ln)
        if pm:
            parts.append(pm.group(1))
    print("%s [%s] parts=%s nodes=%s" % (m, first[:20], parts[:4], nodes[:4]))
