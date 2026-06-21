with open('d:/anime/anistream/anime/models.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "video_url = models.URLField" in line or "video_url = models.URLField(" in line:
        skip = True
        continue
    if skip:
        if ")" in line and not "models.URLField" in line:
            if "verbose_name=" in line or "help_text=" in line or "blank=" in line or "null=" in line:
                skip = False
                continue
            else:
                skip = False
                # fall through to append if it's not part of the kwargs
                if line.strip() == ")":
                    continue
        else:
            continue
    new_lines.append(line)

with open('d:/anime/anistream/anime/models.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
