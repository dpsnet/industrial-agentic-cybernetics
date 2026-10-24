# -*- coding: utf-8 -*-
"""mermaid -> SVG 渲染（修正入口 src/cli.js），失败重试一次。"""
import io, os, re, subprocess

BASE = r"E:\workspace\industrial-agentic-cybernetics"
MONO = os.path.join(BASE, "monograph")
FIG = os.path.join(MONO, "figures")
SRC = os.path.join(MONO, "manuscript-merged.md")
CFG = os.path.join(MONO, "puppeteer.json")
NODE = r"C:\Users\dps_n\AppData\Local\DoubaoWork\User Data\sandbox_runtime\bases\772984f6fd3a8ae0ae7d2422cd7c2bfa\node\node.EXE"
CLI = os.path.join(BASE, ".tools", "node_modules", "@mermaid-js", "mermaid-cli", "src", "cli.js")

c = io.open(SRC, encoding="utf-8").read()
blocks = re.findall(r"```mermaid\s*\n(.*?)\n```", c, re.S)
print("blocks:", len(blocks))

def render(idx, src, retry=True):
    mmd = os.path.join(FIG, "m%d.mmd" % idx)
    svg = os.path.join(FIG, "m%d.svg" % idx)
    io.open(mmd, "w", encoding="utf-8", newline="\n").write(src.strip() + "\n")
    r = subprocess.run([NODE, CLI, "-i", mmd, "-o", svg, "-p", CFG, "-b", "white", "-s", "2"],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0 and retry:
        return render(idx, src, retry=False)
    return r.returncode, (r.stderr[-200:] if r.returncode else "")

fail = []
for i, m in enumerate(re.finditer(r"```mermaid\s*\n(.*?)\n```", c, re.S)):
    rc, err = render(i, m.group(1))
    svg = os.path.join(FIG, "m%d.svg" % i)
    if rc == 0 and os.path.exists(svg) and os.path.getsize(svg) > 100:
        continue
    fail.append((i, rc, err[:150]))
    print("FAIL", i, rc, err[:120])
print("done, failed:", len(fail), fail[:3])
ok = len(blocks) - len(fail)
print("ok:", ok)
