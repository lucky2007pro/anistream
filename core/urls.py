"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from anime import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Asosiy sahifalar
    path('', views.home_page, name='home'),
    path('catalog/', views.catalog_page, name='catalog'),
    path('search/', views.search_page, name='search'),

    # Anime
    path('anime/<int:anime_id>/', views.anime_detail, name='detail'),

    # Janrlar
    path('genres/', views.genres_page, name='genres'),
    path('genre/<slug:slug>/', views.genre_detail, name='genre_detail'),

    # Jadval
    path('schedule/', views.schedule_page, name='schedule'),

    # Auth
    path('auth/', views.auth_view, name='auth_page'),
    path('logout/', views.logout_view, name='logout'),

    # User
    path('profile/', views.profile_page, name='profile'),
    path('favorites/', views.favorites_page, name='favorites'),
    path('watchlist/', views.watchlist_page, name='watchlist'),
    path('history/', views.history_page, name='history'),
    path('settings/', views.settings_page, name='settings'),

    # Actions
    path('anime/<int:anime_id>/favorite/', views.add_to_favorites, name='add_favorite'),

    # Yangiliklar
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),

    # Info pages
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('faq/', views.faq_page, name='faq'),
    path('premium/', views.premium_page, name='premium'),
]

# Custom error handlers
handler404 = 'anime.views.custom_404'
handler500 = 'anime.views.custom_500'

# Media fayllar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)