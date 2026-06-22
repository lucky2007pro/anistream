import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = """
import os

config = '''
server {
    listen 80;
    server_name bestmedia-official.uz www.bestmedia-official.uz;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name bestmedia-official.uz www.bestmedia-official.uz;

    ssl_certificate /etc/letsencrypt/live/bestmedia-official.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bestmedia-official.uz/privkey.pem;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /root/anistream;
    }

    location /media/ {
        root /root/anistream;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }
}
'''

with open('/etc/nginx/sites-available/bestmedia', 'w') as f:
    f.write(config)

os.system("ln -sf /etc/nginx/sites-available/bestmedia /etc/nginx/sites-enabled/bestmedia")
os.system("nginx -t && systemctl restart nginx")
"""
    cmd = f'cat << "EOF" > /tmp/setup_bestmedia.py\n{script}\nEOF\npython3 /tmp/setup_bestmedia.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
