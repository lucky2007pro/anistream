from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from anime import views
from anime.admin_views import *
from anime.sitemaps import NewsSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'news': NewsSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('accounts/login/', views.login, name='login_legacy'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('movie/<int:id>/', views.movie_detail, name='movie_detail'),
    path('toggle-favorite/<int:movie_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_page, name='favorites_page'),
    path('history/', views.watch_history_page, name='watch_history_page'),
    path('catalog/', views.anime_catalog, name='anime_catalog'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
    path('premium/', views.premium_page, name='premium_page'),
    path('news/', views.news_feed, name='news_feed'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('news/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('reels/', views.reels_feed, name='reels'),
    path('aloqa/', views.aloqa, name='aloqa'),

    path('chat/', views.chat, name='chat'),
    path('chat/messages/', views.chat_messages_api, name='chat_messages_api'),
    path('ban_user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('make-vip/<int:user_id>/', views.make_vip, name='make_vip'),

    # Admin Panel
    path('control-panel/', admin_dashboard, name='admin_dashboard'),
    path('control-panel/users/', admin_users, name='admin_users'),
    path('control-panel/users/<int:user_id>/role/', admin_user_role, name='admin_user_role'),
    path('control-panel/movies/', admin_movies, name='admin_movies'),
    path('control-panel/movies/add/', admin_movie_form, name='admin_movie_form'),
    path('control-panel/movies/<int:pk>/edit/', admin_movie_form, name='admin_movie_form'),
    path('control-panel/movies/<int:pk>/delete/', admin_movie_delete, name='admin_movie_delete'),
    path('control-panel/genres/', admin_genres, name='admin_genres'),
    path('control-panel/genres/add/', admin_genre_form, name='admin_genre_form'),
    path('control-panel/genres/<int:pk>/edit/', admin_genre_form, name='admin_genre_form'),
    path('control-panel/genres/<int:pk>/delete/', admin_genre_delete, name='admin_genre_delete'),
    path('control-panel/episodes/', admin_episodes, name='admin_episodes'),
    path('control-panel/episodes/add/', admin_episode_form, name='admin_episode_form'),
    path('control-panel/episodes/<int:pk>/edit/', admin_episode_form, name='admin_episode_form'),
    path('control-panel/episodes/<int:pk>/delete/', admin_episode_delete, name='admin_episode_delete'),
    path('control-panel/chat/', admin_chat, name='admin_chat'),
    path('control-panel/chat/edit/<int:pk>/', admin_message_edit, name='admin_message_edit'),
    path('control-panel/chat/delete/<int:pk>/', admin_message_delete, name='admin_message_delete'),

    path('control-panel/subscriptions/', admin_subscriptions, name='admin_subscriptions'),
    path('control-panel/subscriptions/<int:pk>/<str:action>/', admin_subscription_action,
         name='admin_subscription_action'),
    path('control-panel/avatars/', admin_avatars, name='admin_avatars'),
    path('control-panel/avatars/add/', admin_avatar_form, name='admin_avatar_form'),
    path('control-panel/avatars/<int:pk>/delete/', admin_avatar_delete, name='admin_avatar_delete'),

    path('control-panel/comments/', admin_comments, name='admin_comments'),
    path('control-panel/comments/<int:pk>/edit/', admin_comment_edit, name='admin_comment_edit'),
    path('control-panel/comments/<int:pk>/delete/', admin_comment_delete, name='admin_comment_delete'),

    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),

    # Django default admin
    path('admin/', admin.site.urls),

    # STORY VIEW
    path('story/<int:story_id>/', views.story_view, name='story_view'),
    path('story/seen/<int:story_id>/', views.mark_story_seen, name='mark_story_seen'),
    path('story/<int:story_id>/next/', views.next_story_view, name='next_story'),
    path('story/<int:story_id>/prev/', views.prev_story_view, name='prev_story'),

    # REELS
    path('reels/<int:reel_id>/', views.reel_detail, name='reel_detail'),
    path('reels/<int:reel_id>/like/', views.toggle_reel_like, name='toggle_reel_like'),
    path('reels/<int:reel_id>/comment/', views.add_reel_comment, name='add_reel_comment'),
    path('reels/<int:reel_id>/comments/', views.reel_comments_api, name='reel_comments_api'),
    path('reels/<int:reel_id>/share/', views.reel_share, name='reel_share'),

    # SETTINGS
    path('settings/', views.settings_general, name='settings_general'),
    path('settings/telegram/', views.settings_telegram, name='settings_telegram'),
    path('settings/premium/', views.settings_premium, name='settings_premium'),
    path('settings/devices/', views.settings_devices, name='settings_devices'),
    path('settings/privacy/', views.settings_privacy, name='settings_privacy'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)