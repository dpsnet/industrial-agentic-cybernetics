# -*- coding: utf-8 -*-
import re
merged = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md"
latex  = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md"

# 1) merged 图注现状
t = open(merged, encoding="utf-8").read()
pat = re.compile(r"!\[([^\]]*)\]\(figures/(m\d+)\.jpg\)\{width=([^}]+)\}")
caps = pat.findall(t)
print("merged captions:", len(caps))
from collections import Counter
c = Counter(x[0][:20] for x in caps)
for k, v in c.most_common(8):
    print("  ", v, k)

# 2) merged 是否有同模板标题
print("merged template '动机与工业失效场景':", t.count("动机与工业失效场景"))
print("merged template '协作协议与因果约束':", t.count("协作协议与因果约束"))
print("merged template '协作协议与状态跃迁':", t.count("协作协议与状态跃迁"))
# 3) latex 校验
tl = open(latex, encoding="utf-8").read()
for kw in ["2. 动机与工业失效场景 (Motivation", "5. 协作协议与状态跃迁 (Collaborations)", "5. 协作协议与因果约束 (Collaborations)"]:
    print("latex template", kw[:20], "count=", tl.count(kw))
