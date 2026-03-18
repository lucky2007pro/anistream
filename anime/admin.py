from django.contrib import admin
from .models import Anime, Episode


@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'rating', 'created_at')
    list_filter = ('release_year', 'rating')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    list_per_page = 20


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('anime', 'episode_number', 'title', 'created_at')
    list_filter = ('anime', 'created_at')
    search_fields = ('title', 'anime__title')
    ordering = ('anime', 'episode_number')
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('anime')