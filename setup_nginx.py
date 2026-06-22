import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = """
server {
    listen 80;
    server_name anistream.dev www.anistream.dev 161.97.142.166;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    # We already have whitenoise and django serving media and static, 
    # but nginx serving it directly is much better!
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
"""
    cmd = f'cat << "EOF" > /etc/nginx/sites-available/anistream\n{script}\nEOF\nln -sf /etc/nginx/sites-available/anistream /etc/nginx/sites-enabled/anistream && nginx -t && systemctl restart nginx'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
