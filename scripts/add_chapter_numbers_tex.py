# -*- coding: utf-8 -*-
import io, re

CN = {n: '四五六七八九十'[n-4] if 4 <= n <= 10 else
          ('十' + '一二三四五六七八九'[n-11]) if 11 <= n <= 19 else
          ('二十' + '一二三四五六七八九'[n-21]) if 21 <= n <= 28 else ''
      for n in range(4, 29)}
CN[20] = '二十'

path = r'E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.tex'
with io.open(path, 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')
changed = 0
for i, line in enumerate(lines):
    m = re.match(r'^\\section\{模式\s*(\d{2})\s*：', line)
    if m:
        n = int(m.group(1)) + 3
        lines[i] = re.sub(r'^\\section\{模式\s*(\d{2})\s*：',
                          r'\\section{第%s章 模式 \1：' % CN[n], line, count=1)
        changed += 1
        continue
    m2 = re.match(r'^\\section\{结语\s*：', line)
    if m2:
        lines[i] = re.sub(r'^\\section\{结语\s*：', r'\\section{第二十八章 结语：', line, count=1)
        changed += 1
with io.open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('changed sections:', changed)
