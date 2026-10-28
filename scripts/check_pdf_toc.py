import fitz
doc = fitz.open(r"E:\workspace\industrial-agentic-cybernetics\monograph\Industrial-Agentic-Cybernetics.pdf")
toc = doc.get_toc(simple=False)
cnt = {}
for lvl, title, page, _ in toc:
    cnt[lvl] = cnt.get(lvl, 0) + 1
print("total entries:", len(toc), "| max level:", max(cnt), "| per level:", dict(sorted(cnt.items())))
for lvl, title, page, _ in toc[:60]:
    print(lvl, page, title[:70])
