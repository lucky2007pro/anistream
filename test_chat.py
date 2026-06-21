import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create a test user
user, _ = User.objects.get_or_create(username='testuser')
user.set_password('testpass')
user.save()

c = Client(HTTP_HOST='127.0.0.1')
c.login(username='testuser', password='testpass')

try:
    response = c.get('/chat/')
    print(f"Chat: {response.status_code}")
except Exception as e:
    import traceback
    traceback.print_exc()

