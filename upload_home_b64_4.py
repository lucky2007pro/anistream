import paramiko
import base64

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

local_home = r"d:\anime\anistream\anime\templates\home.html"

try:
    with open(local_home, 'rb') as f:
        home_content_b64 = base64.b64encode(f.read()).decode('utf-8')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = f"""
import base64
content = base64.b64decode('{home_content_b64}').decode('utf-8')

try:
    with open('/opt/anistream/anime/templates/home.html', 'w') as f:
        f.write(content)
except: pass

try:
    with open('/root/anistream/my_app/templates/home.html', 'w') as f:
        f.write(content)
except: pass

import os
os.system("pkill -f gunicorn && bash -c 'cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &' && bash -c 'cd /root/anistream && nohup /root/anistream/venv/bin/gunicorn src.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 > /root/anistream/gunicorn.log 2>&1 &'")
"""
    cmd = f'cat << "EOF" > /tmp/write_home4.py\n{script}\nEOF\npython3 /tmp/write_home4.py'
    ssh.exec_command(cmd)
    
    ssh.close()
    print("Uploaded")
except Exception as e:
    print(f"Error: {e}")
