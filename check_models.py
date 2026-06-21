import re
with open('d:/anime/anistream/anime/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

print("Avatar references:", re.findall(r'.*avatar.*', text, re.IGNORECASE))
print("VIP references:", re.findall(r'.*vip.*', text, re.IGNORECASE))
