with open('d:/anime/anistream/anime/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
match = re.search(r'def profile_page\(.*?(def |$)', content, re.DOTALL)
if match:
    print(match.group(0)[:800])
