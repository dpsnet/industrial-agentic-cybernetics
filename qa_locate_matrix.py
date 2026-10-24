# -*- coding: utf-8 -*-
"""定位 §8 模式矩阵页与图页，渲染验证。"""
import pymupdf, os
doc = pymupdf.open(r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.pdf")
keys = ["宏微观渐进展开", "驱动–导航结对", "五重机械判据", "生产异常嗅探", "断点续跑", "蓝图", "标记门", "模式"]
for k in keys:
    pages = [i for i, pg in enumerate(doc, 1) if k in pg.get_text("text", sort=True)]
    print(k, "->", pages[:12])
# 找含图片的页（渲染 2 张抽查）
imgpages = []
for i, pg in enumerate(doc, 1):
    if pg.get_images(full=True) and len(imgpages) < 3:
        imgpages.append(i)
print("first image pages:", imgpages)
out = r"E:\workspace\industrial-agentic-cybernetics\monograph\_qa"
for p in imgpages + [i for i, pg in enumerate(doc, 1) if "宏微观渐进展开" in pg.get_text("text", sort=True)][:1]:
    doc[p-1].get_pixmap(matrix=pymupdf.Matrix(2,2), alpha=False).save(os.path.join(out, "qanew_p%03d.png" % p))
print("done")
