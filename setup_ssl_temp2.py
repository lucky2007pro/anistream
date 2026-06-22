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
    listen 443 ssl;
    server_name anistream.dev www.anistream.dev 161.97.142.166;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

    location ^~ /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /opt/anistream;
    }

    location /media/ {
        root /opt/anistream;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8080;
    }
}
'''

with open('/etc/nginx/sites-available/anistream', 'w') as f:
    f.write(config)

os.system("nginx -t && systemctl restart nginx")
"""
    cmd = f'cat << "EOF" > /opt/anistream/setup_ssl_temp2.py\n{script}\nEOF\npython3 /opt/anistream/setup_ssl_temp2.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
