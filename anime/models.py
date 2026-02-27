from django.db import models


class Anime(models.Model):
    title = models.CharField(max_length=200, verbose_name="Anime nomi")
    description = models.TextField(verbose_name="Qisqacha ta'rifi")
    release_year = models.IntegerField(verbose_name="Chiqarilgan yili")
    rating = models.FloatField(default=0.0, verbose_name="Reyting")
    # Yangi qo'shilgan qator:
    image_url = models.URLField(max_length=500, default="https://via.placeholder.com/300x400",
                                verbose_name="Rasm havolasi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# anime/models.py ichiga qo'shiladi
from django.db import models


# Bu sizning oldingi Anime modelingiz (u o'zgarishsiz qoladi)
# class Anime(models.Model):
#     ...

# YANGI QO'SHILADIGAN QISM:
class Episode(models.Model):
    anime = models.ForeignKey('Anime', on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.IntegerField(verbose_name="Qism raqami (masalan: 1)")
    title = models.CharField(max_length=200, verbose_name="Qism nomi", blank=True, null=True)

    # Videoni kompyuterdan yuklash uchun
    video_file = models.FileField(upload_to='videos/', blank=True, null=True,
                                  verbose_name="Videoni kompyuterdan yuklash")

    # Yoki boshqa joydan silka (URL) orqali qo'yish uchun
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Yoki video silkasini yozing (URL)")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['episode_number']  # Qismlar har doim 1, 2, 3 tartibida chiqadi

    def __str__(self):
        return f"{self.anime.title} - {self.episode_number}-qism"
