import os
import pymupdf

path = r'E:\workspace\industrial-agentic-cybernetics\monograph\Industrial-Agentic-Cybernetics.pdf'
d = pymupdf.open(path)
t = ''.join(p.get_text() for p in d)
print('pages=', d.page_count)
print('size_MB=', round(os.path.getsize(path) / 1048576, 2))
print('has_concept_doi=', 'zenodo.23636677' in t)
print('has_old_23722977=', 'zenodo.23722977' in t)
print('has_old_23637013=', 'zenodo.23637013' in t)
