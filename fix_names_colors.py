import os
import re

template_dir = r"d:\anime\anistream\anime\templates"

replacements = [
    # Name replacements
    ("BESTMEDIA", "AniStream"),
    ("BestMedia", "AniStream"),
    ("bestmedia", "anistream"),
    ("Bestmedia", "AniStream"),
    ("AniBest", "AniStream"),
    ("anibest", "anistream"),
    ("Anibest", "AniStream"),
    ("ANIBEST", "ANISTREAM"),
    ("bestmedia-official.uz", "anistream.uz"),

    # Color replacements - cyan to pink
    ("rgba(0, 243, 255, 0.25)", "rgba(255, 51, 102, 0.25)"),
    ("rgba(0, 243, 255, 0.12)", "rgba(255, 51, 102, 0.12)"),
    ("rgba(0, 243, 255, 0.13)", "rgba(255, 51, 102, 0.15)"),
    ("rgba(0, 243, 255, 0.28)", "rgba(255, 51, 102, 0.3)"),
    ("rgba(0, 243, 255, 0.6)", "rgba(255, 51, 102, 0.6)"),
    ("rgba(0, 243, 255, 0.15)", "rgba(255, 51, 102, 0.15)"),
    ("rgba(0, 243, 255, 0.3)", "rgba(255, 51, 102, 0.3)"),
    ("rgba(0, 243, 255, 0.08)", "rgba(255, 51, 102, 0.08)"),
    ("rgba(0, 243, 255, 0.4)", "rgba(255, 51, 102, 0.4)"),
    ("rgba(0, 243, 255, 0.7)", "rgba(255, 51, 102, 0.7)"),
    ("rgba(0, 243, 255, 0.18)", "rgba(255, 51, 102, 0.18)"),
    ("rgba(0, 243, 255, 0.35)", "rgba(255, 51, 102, 0.35)"),
    ("rgba(0, 243, 255, 0.1)", "rgba(255, 51, 102, 0.1)"),
    ("rgba(0, 243, 255, 0.2)", "rgba(255, 51, 102, 0.2)"),
    ("#00f3ff", "#ff3366"),
    ("--accent: #0af", "--accent: #ff3366"),
    ("--accent:#0af", "--accent:#ff3366"),
    ("color: #0af", "color: #ff3366"),
    ("background: #0af", "background: #ff3366"),
    ("border-color: #0af", "border-color: #ff3366"),
    ("linear-gradient(135deg, #0ea5e9, #2563eb)", "linear-gradient(135deg, #ff003c, #ff4d6d)"),
    ("rgba(14, 165, 233, 0.3)", "rgba(255, 0, 60, 0.3)"),
    ("rgba(14, 165, 233, 0.5)", "rgba(255, 0, 60, 0.5)"),

    # Accent variable definition
    ("--accent: #00f3ff", "--accent: #ff3366"),
]

count = 0
for root, dirs, files in os.walk(template_dir):
    for fname in files:
        if fname.endswith(('.html', '.css', '.js')):
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            for old, new in replacements:
                content = content.replace(old, new)

            if content != original:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1
                print(f"Updated: {fname}")

print(f"\nTotal files updated: {count}")
