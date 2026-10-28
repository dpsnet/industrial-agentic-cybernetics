# -*- coding: utf-8 -*-
import glob, io, re, os

CN = {n: '四五六七八九十'[n-4] if 4 <= n <= 10 else
          ('十' + '一二三四五六七八九'[n-11]) if 11 <= n <= 19 else
          ('二十' + '一二三四五六七八九'[n-21]) if 21 <= n <= 28 else ''
      for n in range(4, 29)}
CN[20] = '二十'

def fix_file(path):
    with io.open(path, 'r', encoding='utf-8-sig') as f:
        lines = f.read().split('\n')
    changed = False
    for i, line in enumerate(lines):
        m = re.match(r'^(#+)\s*模式\s*(\d{2})\s*：', line)
        if m and int(m.group(2)) >= 1:
            n = int(m.group(2)) + 3
            new = '%s 第%s章 模式 %s：' % (m.group(1), CN[n], m.group(2))
            lines[i] = new + line.split('：', 1)[1]
            changed = True
            print(path.split('\\')[-1], '->', lines[i][:60])
            continue
        m2 = re.match(r'^(#+)\s*结语\s*：', line)
        if m2:
            lines[i] = '%s 第二十八章 结语：' % m2.group(1) + line.split('：', 1)[1]
            changed = True
            print(path.split('\\')[-1], '->', lines[i][:60])
    if changed:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

roots = [
    r'E:\workspace\industrial-agentic-cybernetics\docs\part*\pattern-*.md',
    r'E:\workspace\industrial-agentic-cybernetics\docs\epilogue\*.md',
    r'E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md',
]
for pat in roots:
    for p in glob.glob(pat):
        fix_file(p)
print('DONE')
