import os
import re
import shutil

src_dir = 'd:/anime/anime_zakaz/my_app/templates'
dst_dir = 'd:/anime/anistream/anime/templates'

files_to_copy = ['chat.html', 'reels.html', 'reel_detail.html', 'story_view.html']

for f in files_to_copy:
    src_path = os.path.join(src_dir, f)
    dst_path = os.path.join(dst_dir, f)
    
    with open(src_path, 'r', encoding='utf-8') as src_file:
        content = src_file.read()
    
    # Replace colors
    content = content.replace('#00f3ff', '#ff3366')
    content = content.replace('0,243,255', '255,51,102')
    content = content.replace('#00d4ff', '#ff3366')
    content = content.replace('0,212,255', '255,51,102')
    content = content.replace('#00aacc', '#ff003c')
    content = content.replace('#ff2d2d', '#ff3366')
    content = content.replace('255, 45, 45', '255, 51, 102')

    # Replace font families
    content = re.sub(r'font-family:\s*[^;]+;', "font-family: 'Outfit', sans-serif;", content)

    # Insert Outfit font before </head> if not exists
    font_link = '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap" rel="stylesheet">'
    if 'Outfit' not in content:
        content = content.replace('</head>', f'    {font_link}\n</head>')
    
    # Make sure we use anistream URLs and views where necessary
    # In chat.html, the base layout is standalone but might have links to home
    
    with open(dst_path, 'w', encoding='utf-8') as dst_file:
        dst_file.write(content)
        
print("Templates copied and adapted successfully.")
