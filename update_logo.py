import re

filepath = r"d:\anime\anistream\anime\templates\base.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace text
content = content.replace('<span class="nav-brand-text">ANI <span>BEST</span></span>', '<span class="nav-brand-text">Ani<span>Stream</span></span>')

# Replace font size
content = re.sub(r'(\.nav-brand-text\s*\{[^}]*font-size:\s*)1\.16rem', r'\g<1>1.5rem', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated base.html locally")
