from django.apps import AppConfig


class AnimeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'anime'
    verbose_name = 'Anime Streaming'

    def ready(self):
        import anime.signals  # Signal'larni import qilish
