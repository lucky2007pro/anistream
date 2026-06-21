with open("d:/anime/anistream/anime/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace default_movie_poster variable with a placeholder url
html = html.replace("{{ default_movie_poster }}", "https://via.placeholder.com/300x450?text=No+Image")

with open("d:/anime/anistream/anime/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
