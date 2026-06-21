with open('d:/anime/anistream/anime/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
match = re.search(r'def home_page\(.*?\):.*?return render\(', content, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("home_page not found")
