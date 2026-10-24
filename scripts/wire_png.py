# -*- coding: utf-8 -*-
"""mermaid -> PNG 渲染（跳过已存在的），全部完成后替换 PDF 版 md 的图引用为 .png。"""
import io, os, re, subprocess

BASE = r"E:\workspace\industrial-agentic-cybernetics"
MONO = os.path.join(BASE, "monograph")
FIG = os.path.join(MONO, "figures")
PDFMD = os.path.join(MONO, "manuscript-pdf.md")
NODE = r"C:\Users\dps_n\AppData\Local\DoubaoWork\User Data\sandbox_runtime\bases\772984f6fd3a8ae0ae7d2422cd7c2bfa\node\node.EXE"
CLI = os.path.join(BASE, ".tools", "node_modules", "@mermaid-js", "mermaid-cli", "src", "cli.js")
CFG = os.path.join(MONO, "puppeteer.json")

ok, fail = 0, []
for i in range(52):
    mmd = os.path.join(FIG, "m%d.mmd" % i)
    png = os.path.join(FIG, "m%d.png" % i)
    if not os.path.exists(mmd):
        continue
    if os.path.exists(png) and os.path.getsize(png) > 2000:
        ok += 1
        continue
    r = subprocess.run([NODE, CLI, "-i", mmd, "-o", png, "-p", CFG, "-b", "white", "-s", "2"],
                       capture_output=True, text=True, timeout=120)
    if r.returncode == 0 and os.path.exists(png) and os.path.getsize(png) > 2000:
        ok += 1
    else:
        fail.append((i, r.returncode, r.stderr[-120:]))
        print("FAIL", i, r.returncode, r.stderr[-120:])
print("png ok:", ok, "fail:", fail[:3])

# 替换 PDF 版 md：figures/mN.svg -> figures/mN.png（仅对存在 PNG 的）
c = io.open(PDFMD, encoding="utf-8").read()
for i in range(52):
    if os.path.exists(os.path.join(FIG, "m%d.png" % i)):
        c = c.replace("(figures/m%d.svg)" % i, "(figures/m%d.png)" % i)
io.open(PDFMD, "w", encoding="utf-8", newline="\n").write(c)
print("pdf-md svg->png replaced; bytes:", os.path.getsize(PDFMD))
