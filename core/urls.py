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
    # Custom content admin dashboard (faqat staff uchun)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Custom content admin (URL nomlari Django admin'dan oldin turishi kerak)
    path('admin/genres/', views.admin_genre_list, name='admin_genre_list'),
    path('admin/genres/create/', views.admin_genre_create, name='admin_genre_create'),
    path('admin/genres/<int:pk>/edit/', views.admin_genre_edit, name='admin_genre_edit'),
    path('admin/genres/<int:pk>/delete/', views.admin_genre_delete, name='admin_genre_delete'),

    path('admin/animes/', views.admin_anime_list, name='admin_anime_list'),
    path('admin/animes/create/', views.admin_anime_create, name='admin_anime_create'),
    path('admin/animes/<int:pk>/edit/', views.admin_anime_edit, name='admin_anime_edit'),
    path('admin/animes/<int:pk>/delete/', views.admin_anime_delete, name='admin_anime_delete'),

    path('admin/episodes/', views.admin_episode_list, name='admin_episode_list'),
    path('admin/episodes/create/', views.admin_episode_create, name='admin_episode_create'),
    path('admin/episodes/<int:pk>/edit/', views.admin_episode_edit, name='admin_episode_edit'),
    path('admin/episodes/<int:pk>/delete/', views.admin_episode_delete, name='admin_episode_delete'),

    path('admin/news/', views.admin_news_list, name='admin_news_admin_list'),
    path('admin/news/create/', views.admin_news_create, name='admin_news_create'),
    path('admin/news/<int:pk>/edit/', views.admin_news_edit, name='admin_news_edit'),
    path('admin/news/<int:pk>/delete/', views.admin_news_delete, name='admin_news_delete'),

    path('admin/shorts/', views.admin_short_list, name='admin_short_list'),
    path('admin/shorts/create/', views.admin_short_create, name='admin_short_create'),
    path('admin/shorts/<int:pk>/edit/', views.admin_short_edit, name='admin_short_edit'),
    path('admin/shorts/<int:pk>/delete/', views.admin_short_delete, name='admin_short_delete'),

    # Django default admin (umumiy /admin/ prefiksidan keyin)
    path('admin/', admin.site.urls),

    # Asosiy sahifalar
    path('', views.home_page, name='home'),
    path('catalog/', views.catalog_page, name='catalog'),
    path('search/', views.search_page, name='search'),

    # Anime
    path('anime/<int:anime_id>/', views.anime_detail, name='detail'),
    path('shorts/', views.shorts_page, name='shorts_page'),
    path('shorts/<int:short_id>/stream/', views.short_stream, name='short_stream'),

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
    path('anime/<int:anime_id>/comment/', views.add_comment, name='add_comment'),

    # Yangiliklar
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),

    # Info pages
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('faq/', views.faq_page, name='faq'),
    path('premium/', views.premium_page, name='premium'),
    path('fandub-projects/', views.fandub_projects_page, name='fandub_projects'),
    path('live-streams/', views.live_streams_page, name='live_streams'),
    path('billing/', views.billing_page, name='billing'),
    path('password-help/', views.password_reset_help_page, name='password_help'),
]

# Custom error handlers
handler404 = 'anime.views.custom_404'
handler500 = 'anime.views.custom_500'

# Media fayllar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)