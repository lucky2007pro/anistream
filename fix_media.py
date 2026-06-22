import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # We want to use django's serve for media files in production without nginx
    script = """
import os
import django
from dotenv import load_dotenv

load_dotenv('/opt/anistream/.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

with open('/opt/anistream/core/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

if "from django.urls import re_path" not in content:
    content = content.replace("from django.urls import path, include", "from django.urls import path, include, re_path")
    
if "from django.views.static import serve" not in content:
    content = "from django.views.static import serve\\n" + content
    
if "re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})" not in content:
    # Add to the end of file
    new_urls = "\\n\\n# Force media serving in production without nginx\\nif not settings.DEBUG:\\n    urlpatterns += [\\n        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),\\n    ]\\n"
    content += new_urls
    
    with open('/opt/anistream/core/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("urls.py modified for media.")
else:
    print("urls.py already has media serve.")
"""
    cmd = f'cat << "EOF" > /opt/anistream/fix_media.py\n{script}\nEOF\n/opt/anistream/venv/bin/python /opt/anistream/fix_media.py && pkill -f gunicorn'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
