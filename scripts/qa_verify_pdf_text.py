import os
import pymupdf

path = r'E:\workspace\industrial-agentic-cybernetics\monograph\Industrial-Agentic-Cybernetics.pdf'
d = pymupdf.open(path)
t = ''.join(p.get_text() for p in d)
size = os.path.getsize(path) / 1048576
print('pages=', d.page_count)
print('size_MB=', round(size, 2))
print('has_24_patterns=', '24 个设计模式（模式 01–24）' in t)
print('has_benshu=', '本书抛弃所有空洞的修辞' in t)
print('has_old_22=', '22 个设计模式（模式 01–22）' in t)
print('has_old_benzhu=', '本专著抛弃' in t)
