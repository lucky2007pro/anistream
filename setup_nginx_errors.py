import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    html = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xatolik - AniStream</title>
    <style>
        body { background-color: #0a0a0f; color: #fff; font-family: 'Inter', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; flex-direction: column; }
        h1 { font-size: 4rem; color: #ff3366; margin-bottom: 10px; }
        p { font-size: 1.2rem; color: #8a7a7d; margin-bottom: 30px; }
        a { text-decoration: none; padding: 15px 30px; background: #ff3366; color: white; border-radius: 30px; font-weight: 800; transition: 0.3s; }
        a:hover { background: #e02255; }
    </style>
</head>
<body>
    <h1>XATOLIK YUZ BERDI</h1>
    <p>Kechirasiz, tizimda qandaydir xatolik yuz berdi yoki sahifa topilmadi.<br>Sayt tez orada o'z holiga qaytadi.</p>
    <a href="/">Bosh sahifaga qaytish</a>
</body>
</html>"""

    script = f"""
import os

html_content = '''{html}'''

with open('/var/www/html/error.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

anistream_config = '''
server {{
    listen 80;
    server_name anistream.dev www.anistream.dev 161.97.142.166;
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl;
    server_name anistream.dev www.anistream.dev;

    client_max_body_size 2000M;

    ssl_certificate /etc/letsencrypt/live/anistream.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/anistream.dev/privkey.pem;

    error_page 413 404 500 502 503 504 /error.html;
    location = /error.html {{
        root /var/www/html;
        internal;
    }}

    location = /favicon.ico {{ access_log off; log_not_found off; }}
    
    location /static/ {{
        root /opt/anistream;
    }}

    location /media/ {{
        root /opt/anistream;
    }}

    location / {{
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8080;
    }}
}}
'''

with open('/etc/nginx/sites-available/anistream', 'w') as f:
    f.write(anistream_config)

bestmedia_config = '''
server {{
    listen 80;
    server_name bestmedia-official.uz www.bestmedia-official.uz;
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl;
    server_name bestmedia-official.uz www.bestmedia-official.uz;

    client_max_body_size 2000M;

    ssl_certificate /etc/letsencrypt/live/bestmedia-official.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bestmedia-official.uz/privkey.pem;

    error_page 413 404 500 502 503 504 /error.html;
    location = /error.html {{
        root /var/www/html;
        internal;
    }}

    location = /favicon.ico {{ access_log off; log_not_found off; }}
    
    location /static/ {{
        root /root/anistream;
    }}

    location /media/ {{
        root /root/anistream;
    }}

    location / {{
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }}
}}
'''

with open('/etc/nginx/sites-available/bestmedia', 'w') as f:
    f.write(bestmedia_config)

os.system("nginx -t && systemctl restart nginx")
"""
    cmd = f'cat << "EOF" > /tmp/setup_nginx_errors.py\n{script}\nEOF\npython3 /tmp/setup_nginx_errors.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
