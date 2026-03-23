from django.contrib import admin
from .models import (
    Genre, Anime, Episode, UserProfile,
    WatchHistory, Comment, NewsPost
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    list_display = ('title', 'anime_type', 'status', 'release_year', 'rating', 'views_count', 'created_at')
    list_filter = ('anime_type', 'status', 'release_year', 'genres')
    search_fields = ('title', 'description', 'studio')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('views_count', 'created_at', 'updated_at')


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('anime', 'episode_number', 'title', 'telegram_message_id', 'created_at')
    list_filter = ('anime', 'created_at')
    search_fields = ('title', 'anime__title')
    ordering = ('anime', 'episode_number')
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Asosiy', {
            'fields': ('anime', 'episode_number', 'title')
        }),
        ('Video Manbasi', {
            'fields': ('video_file', 'video_url'),
            'description': "Agar video serverda yoki boshqa saytda bo'lsa."
        }),
        ('Telegram Integratsiya (Tavsiya etiladi)', {
            'fields': ('telegram_file_id', 'telegram_message_id', 'telegram_channel_post_url'),
            'description': "Katta videolarni (2GB gacha) stream qilish uchun <b>Telegram message_id</b> ni to'ldirish SHART!"
        }),
        ('Sana', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('anime')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_premium', 'premium_until')
    list_filter = ('is_premium',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('favorites', 'watchlist')


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'anime', 'episode', 'watch_progress', 'last_watched')
    list_filter = ('last_watched',)
    search_fields = ('user__username', 'anime__title')
    readonly_fields = ('last_watched',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'anime', 'text_short', 'created_at', 'likes_count')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'anime__title', 'text')
    readonly_fields = ('created_at', 'updated_at')

    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Izoh'


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'views', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')