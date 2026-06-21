import os
import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

c = Client()
try:
    response = c.get('/')
    print(f"Index: {response.status_code}")
except Exception as e:
    print(f"Index error: {e}")

try:
    response = c.get('/chat/')
    print(f"Chat: {response.status_code}")
except Exception as e:
    print(f"Chat error: {e}")

try:
    response = c.get('/reels/')
    print(f"Reels: {response.status_code}")
except Exception as e:
    print(f"Reels error: {e}")

