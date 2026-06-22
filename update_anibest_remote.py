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
import re

def update_dir(template_dir):
    # 1. Replace ANI BEST and Ani Best
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = re.sub(r'ANI BEST', 'AniStream', content)
                new_content = re.sub(r'Ani Best', 'AniStream', new_content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated: {filepath}")

    # 2. Modify home.html slider CSS
    home_html = os.path.join(template_dir, 'home.html')
    if os.path.exists(home_html):
        with open(home_html, 'r', encoding='utf-8') as f:
            home_content = f.read()

        home_content = re.sub(
            r'\\.slider-container\\s*\\{[^}]*\\}',
            '''\.slider-container {
        position: relative;
        width: 100%;
        aspect-ratio: 21 / 9;
        min-height: 480px;
        max-height: 85vh;
        overflow: hidden;
        border-radius: 20px;
        margin: 0 auto;
        box-shadow: 0 0 0 2px rgba(255, 51, 102, 0.3), 0 0 60px rgba(255, 51, 102, 0.2);
    }''',
            home_content
        )

        home_content = re.sub(
            r'\\.slide-title\\s*\\{[^}]*\\}',
            '''\.slide-title {
        font-size: 4.2rem;
        font-weight: 900;
        line-height: 1.05;
        margin-bottom: 15px;
        text-shadow: 0 10px 30px rgba(0,0,0,0.8);
        letter-spacing: -0.02em;
    }''',
            home_content
        )

        home_content = re.sub(
            r'\\.btn-main\\s*\\{[^}]*\\}',
            '''\.btn-main {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 16px 36px;
        border-radius: 16px;
        background: linear-gradient(135deg, #ff003c, #ff4d6d);
        color: #fff;
        font-size: 18px;
        font-weight: 700;
        text-decoration: none;
        box-shadow: 0 10px 30px rgba(255, 0, 60, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        -webkit-tap-highlight-color: transparent;
    }''',
            home_content
        )

        with open(home_html, 'w', encoding='utf-8') as f:
            f.write(home_content)
        print(f"Updated CSS in {home_html}")

update_dir('/opt/anistream/anime/templates')
update_dir('/root/anistream/anime/templates')

# Restart Gunicorn processes
os.system("systemctl restart anistream || true")
os.system("pkill -f gunicorn && bash -c 'cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &' && bash -c 'cd /root/anistream && nohup /root/anistream/venv/bin/gunicorn src.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 > /root/anistream/gunicorn.log 2>&1 &'")
"""
    cmd = f'cat << "EOF" > /tmp/update_anibest.py\n{script}\nEOF\npython3 /tmp/update_anibest.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:\n", stdout.read().decode().strip())
    print("ERR:\n", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
