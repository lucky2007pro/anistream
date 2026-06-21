with open('d:/anime/anistream/anime/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
match = re.search(r'class UserProfile.*?def __str__', text, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("UserProfile not found")
