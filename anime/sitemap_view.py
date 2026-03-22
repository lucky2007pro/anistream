# anime/views.py ga qo'shish uchun
# urls.py ga ham: path('sitemap.xml', sitemap_view, name='sitemap'),

from django.http import HttpResponse
from django.utils import timezone
from .models import Anime  # o'zingizning modelingiz

def sitemap_view(request):
    base = "https://anistream.uz"
    today = timezone.now().date()

    urls = [
        f"  <url><loc>{base}/</loc><changefreq>daily</changefreq><priority>1.0</priority><lastmod>{today}</lastmod></url>",
        f"  <url><loc>{base}/catalog</loc><changefreq>daily</changefreq><priority>0.9</priority><lastmod>{today}</lastmod></url>",
        f"  <url><loc>{base}/genres</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>",
        f"  <url><loc>{base}/schedule</loc><changefreq>daily</changefreq><priority>0.8</priority></url>",
        f"  <url><loc>{base}/news</loc><changefreq>daily</changefreq><priority>0.8</priority></url>",
        f"  <url><loc>{base}/about</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>",
        f"  <url><loc>{base}/contact</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>",
        f"  <url><loc>{base}/faq</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>",
        f"  <url><loc>{base}/premium</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>",
    ]

    # Barcha anime sahifalarini qo'shish
    for anime in Anime.objects.all():
        urls.append(
            f"  <url><loc>{base}/anime/{anime.id}</loc>"
            f"<changefreq>weekly</changefreq><priority>0.9</priority></url>"
        )

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '\n'.join(urls)
    xml += '\n</urlset>'

    return HttpResponse(xml, content_type='application/xml')
