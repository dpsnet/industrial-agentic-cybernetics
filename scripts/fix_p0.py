# -*- coding: utf-8 -*-
"""P0 修复：
1) figures/*.png -> *.jpg（白底 RGB，quality=92，兼容性最广）
2) latex md 图片引用改 .jpg，占位题注"图（mermaid 渲染）"改为最近章节标题（caption 不带图号，LaTeX 自动编号）
3) 22/24 模式口径声明（latex md + merged 同步）
"""
import io, re, os
from PIL import Image

base = r"E:\workspace\industrial-agentic-cybernetics\monograph"

# 1) PNG -> JPG
figdir = os.path.join(base, "figures")
n_jpg = 0
for fn in os.listdir(figdir):
    if fn.lower().endswith(".png") and fn.lower().startswith("m"):
        im = Image.open(os.path.join(figdir, fn)).convert("RGB")
        jpg = fn[:-4] + ".jpg"
        im.save(os.path.join(figdir, jpg), "JPEG", quality=92)
        n_jpg += 1
print("converted jpg:", n_jpg)

# 2) latex md 图题 + .jpg 引用
p_md = os.path.join(base, "manuscript-latex.md")
lines = io.open(p_md, encoding="utf-8").read().split("\n")
cur_head = ""
img_re = re.compile(r"^!\[图（mermaid 渲染）\]\(figures/(m\d+)\.png\)\{width=(\d+)%?\}$")
out = []
for ln in lines:
    if ln.startswith("#"):
        # 取标题文本（去井号和 markdown 标点）
        t = re.sub(r"^#+\s*", "", ln).strip()
        t = re.sub(r"[#*`]", "", t).strip()
        if t:
            cur_head = t
    m = img_re.match(ln.strip())
    if m:
        name, w = m.group(1), m.group(2)
        out.append("![%s 示意](figures/%s.jpg){width=%s%%}" % (cur_head, name, w))
        continue
    out.append(ln)
io.open(p_md, "w", encoding="utf-8").write("\n".join(out))
print("latex md images relinked with captions")

# 3) 22/24 口径（latex md + merged）
def fix_22_24(p):
    c = io.open(p, encoding="utf-8").read()
    pairs = [
        ("本专著所阐述的 22 个设计模式均作为",
         "本专著所阐述的 22 个设计模式（模式 01–22）均作为"),
        ("回顾本书总结的 8 大模式族：",
         "回顾本书总结的 8 大模式族（覆盖模式 01–22；模式 23/24 为生产现场实证模式，计入 24 模式体系）："),
        ("这 22 个模式互为支点",
         "这 22 个模式（连同生产现场实证的模式 23/24，全书共 24 模式）互为支点"),
    ]
    n = 0
    for a, b in pairs:
        if a in c:
            c = c.replace(a, b)
            n += 1
    # 章节标题 "22 个模式构筑的系统外骨骼" 保留（属结语小标题），在其段落首句后补口径
    if "22 个模式构筑的系统外骨骼" in c and "模式 23/24" not in c.split("22 个模式构筑的系统外骨骼")[1][:200]:
        c = c.replace("回顾本书总结的 8 大模式族", "回顾本书总结的 8 大模式族（覆盖模式 01–22；模式 23/24 为生产现场实证模式，计入 24 模式体系）")
        n += 1
    io.open(p, "w", encoding="utf-8").write(c)
    return n

print("latex 22/24 fixes:", fix_22_24(p_md))
print("merged 22/24 fixes:", fix_22_24(os.path.join(base, "manuscript-merged.md")))
