import os
import re

filepath = r"d:\anime\anistream\anime\templates\home.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update slider-container padding and border-radius
content = re.sub(
    r'\.slider-wrapper-outer \{[^}]+\}',
    '''.slider-wrapper-outer {
        width: 100%;
        max-width: 1400px;
        margin: 20px auto;
        padding: 0 5%;
    }''',
    content
)

content = re.sub(
    r'\.slider-container \{[^}]+\}',
    '''.slider-container {
        position: relative;
        width: 100%;
        aspect-ratio: auto;
        height: 65vh;
        min-height: 480px;
        max-height: 700px;
        overflow: hidden;
        border-radius: 24px;
        margin: 0 auto;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.05), 0 20px 50px rgba(0,0,0,0.5);
    }''',
    content
)

# 2. Update blur effect
content = re.sub(
    r'filter: blur\(20px\) brightness\(0\.4\);',
    'filter: blur(8px) brightness(0.45);',
    content
)

# 3. Update poster image border-radius
content = re.sub(
    r'\.slide-poster-right img \{[^}]+\}',
    '''.slide-poster-right img {
        width: 100%;
        height: auto;
        aspect-ratio: 2 / 3;
        object-fit: cover;
        display: block;
        border-radius: 12px;
    }''',
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated locally")
