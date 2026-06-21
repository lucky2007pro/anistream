import re

with open("d:/anime/anime_zakaz/my_app/templates/home.html", "r", encoding="utf-8") as f:
    zakaz_home = f.read()

with open("d:/anime/anistream/anime/templates/index.html", "r", encoding="utf-8") as f:
    ani_index = f.read()

# 1. Extract CSS from zakaz_home
css_match = re.search(r'<style>(.*?)</style>', zakaz_home, re.DOTALL)
zakaz_css = css_match.group(1) if css_match else ""

# Replace blue colors with pink colors in zakaz CSS
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.25)", "rgba(255, 51, 102, 0.25)")
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.12)", "rgba(255, 51, 102, 0.12)")
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.13)", "rgba(255, 51, 102, 0.15)")
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.28)", "rgba(255, 51, 102, 0.3)")
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.6)", "rgba(255, 51, 102, 0.6)")
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.15)", "rgba(255, 51, 102, 0.15)")
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.3)", "rgba(255, 51, 102, 0.3)")

# Contact buttons colors
zakaz_css = zakaz_css.replace("linear-gradient(135deg, #0ea5e9, #2563eb)", "linear-gradient(135deg, #ff003c, #ff4d6d)")
zakaz_css = zakaz_css.replace("rgba(14, 165, 233, 0.3)", "rgba(255, 0, 60, 0.3)")
zakaz_css = zakaz_css.replace("rgba(14, 165, 233, 0.5)", "rgba(255, 0, 60, 0.5)")

# Chat buttons colors
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.08)", "rgba(255, 51, 102, 0.08)")
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.4)", "rgba(255, 51, 102, 0.4)")
zakaz_css = zakaz_css.replace("rgba(0, 243, 255, 0.7)", "rgba(255, 51, 102, 0.7)")

# Replace default poster variable if needed
zakaz_css = zakaz_css.replace("var(--accent)", "#ff3366")

# 2. Extract HTML content from zakaz_home
content_match = re.search(r'{% block content %}(.*?){% endblock %}', zakaz_home, re.DOTALL)
zakaz_html = content_match.group(1) if content_match else ""

# Remove Action buttons section
zakaz_html = re.sub(r'<!-- ALOQA VA CHAT TUGMALAR -->.*?</div>\s*</div>', '', zakaz_html, flags=re.DOTALL)

# Fix URL for detail page (in anime_zakaz it was movie_detail, here it is detail)
zakaz_html = zakaz_html.replace("'movie_detail'", "'detail'")
zakaz_html = zakaz_html.replace("anime.minimum_tier", "anime.is_premium")
zakaz_html = zakaz_html.replace("== 'premium'", "")

# 3. Modify anistream index.html
# Find where the old slider starts. We keep navbar and profile menu, and everything up to `</nav>`
navbar_end = ani_index.find("</nav>") + 6

# Also anistream has profile sidebar, hamburger etc. The navbar HTML contains them? Wait, let's just keep everything before `<div class="slider-container">`
slider_start = ani_index.find('<div class="slider-container">')

# But we also need to append the JS at the end.
# Wait, anistream index.html has a lot of content after slider (stories, animes loop etc).
# I'll just keep the Head, Navbar, Mobile Nav, Sidebar, and inject the new CSS and Content.

# Let's cleanly rebuild the file:
# Keep <head> up to </head>
head_end = ani_index.find("</head>")
head = ani_index[:head_end]

# In head, we already have a <style> block. Let's append zakaz_css to it.
head = head.replace("</style>", f"\n{zakaz_css}\n</style>")

# Find <body>
body_start = ani_index.find("<body>") + 6

# Find navbar and sidebar HTML in anistream
# Let's keep from <body> to `<div class="slider-container">`
top_html = ani_index[body_start:slider_start]

# What about the profile sidebar and scripts? In anistream, they are at the bottom of the page.
# Let's find `<div class="profile-overlay"`
profile_start = ani_index.find('<div class="profile-overlay"')
scripts_start = ani_index.find('<script>', profile_start)
bottom_html = ani_index[profile_start:]

# Put it together:
final_html = head + "</head>\n<body>\n" + top_html + zakaz_html + "\n" + bottom_html

with open("d:/anime/anistream/anime/templates/index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("Merge completed!")
