from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, VipUser, Category, Movie, MovieEpisode,
    SiteSettings, AppSettings, MP3, ChatMessage, ProfileAvatar,
    SubscriptionReceipt, FavoriteAnime, WatchHistory,
    MovieComment, ActiveSession, AnimeNews, NewsLike,
    Story, StoryView, Reel, ReelLike, ReelComment, ReelShare,
    UserSettings, AnimeSchedule
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_admin_user', 'is_banned')
    list_filter = ('is_staff', 'is_admin_user', 'is_banned', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha', {'fields': ('phone', 'is_banned', 'is_admin_user', 'avatar')}),
    )


@admin.register(VipUser)
class VipUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'is_vip', 'vip_expire')
    list_filter = ('tier', 'is_vip')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'minimum_tier', 'views_count', 'is_home_featured', 'created_at')
    list_filter = ('minimum_tier', 'is_home_featured', 'category')
    search_fields = ('title', 'description')


@admin.register(MovieEpisode)
class MovieEpisodeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'episode_number', 'title', 'created_at')
    list_filter = ('movie',)
    search_fields = ('title', 'movie__title')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'updated_at')


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'default_theme', 'allow_stickers', 'updated_at')


@admin.register(MP3)
class MP3Admin(admin.ModelAdmin):
    list_display = ('title', 'created_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_banned', 'is_admin')
    list_filter = ('created_at', 'is_banned', 'is_admin')
    search_fields = ('user__username', 'message')


@admin.register(ProfileAvatar)
class ProfileAvatarAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')


@admin.register(SubscriptionReceipt)
class SubscriptionReceiptAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_approved', 'is_rejected', 'created_at')
    list_filter = ('is_approved', 'is_rejected')


@admin.register(FavoriteAnime)
class FavoriteAnimeAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'created_at')


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'last_watched')


@admin.register(MovieComment)
class MovieCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'text', 'created_at')
    list_filter = ('created_at',)


@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'ip_address', 'created_at')


@admin.register(AnimeNews)
class AnimeNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'description')


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'expires_at', 'created_at')
    list_filter = ('is_active',)


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'views_count', 'created_at')
    list_filter = ('created_at',)


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'tabbar_on')
    list_filter = ('theme', 'tabbar_on')


@admin.register(AnimeSchedule)
class AnimeScheduleAdmin(admin.ModelAdmin):
    list_display = ('anime', 'day_of_week', 'air_time', 'episode_number')
    list_filter = ('day_of_week',)
    search_fields = ('anime__title',)
