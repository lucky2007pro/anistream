import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = """
# Generate self-signed cert
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/C=US/ST=State/L=City/O=Company/CN=anistream.dev"

# Update Nginx config
cat << "EOF" > /etc/nginx/sites-available/anistream
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
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://127.0.0.1:8080;
    }
}
EOF

nginx -t && systemctl restart nginx
"""
    cmd = f'cat << "EOF" > /opt/anistream/setup_ssl_temp.sh\n{script}\nEOF\nbash /opt/anistream/setup_ssl_temp.sh'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
