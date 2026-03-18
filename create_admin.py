import os
import django

# Sozlamalarni yuklaymiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # 'core'ni o'z papka nomingizga o'zgartiring
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin' # O'zingiz xohlagan nom
password = 'hojiakbar' # Murakkabroq parol qo'ying
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser muvaffaqiyatli yaratildi!")
else:
    print("Superuser allaqachon mavjud.")