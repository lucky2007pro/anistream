from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserSettings, VipUser

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_related_models(sender, instance, created, **kwargs):
    """Yangi user yaratilganda avtomatik settings va vip_data yaratish"""
    if created:
        UserSettings.objects.get_or_create(user=instance)
        VipUser.objects.get_or_create(user=instance)
