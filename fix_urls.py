with open("d:/anime/anistream/anime/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace anime_catalog with catalog
html = html.replace("'anime_catalog'", "'catalog'")

# Replace movie_detail with detail (I did this already, but maybe there's more)
html = html.replace("'movie_detail'", "'detail'")

with open("d:/anime/anistream/anime/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
