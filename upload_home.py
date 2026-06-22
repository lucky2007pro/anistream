import paramiko
import os

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

local_home = r"d:\anime\anistream\anime\templates\home.html"

try:
    with open(local_home, 'r', encoding='utf-8') as f:
        home_content = f.read()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    sftp = ssh.open_sftp()
    
    with sftp.file('/opt/anistream/anime/templates/home.html', 'w') as f:
        f.write(home_content.encode('utf-8'))
        
    with sftp.file('/root/anistream/anime/templates/home.html', 'w') as f:
        f.write(home_content.encode('utf-8'))
        
    sftp.close()
    print("Successfully uploaded to remote servers.")
    
    ssh.exec_command("pkill -f gunicorn && bash -c 'cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &' && bash -c 'cd /root/anistream && nohup /root/anistream/venv/bin/gunicorn src.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 > /root/anistream/gunicorn.log 2>&1 &'")
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
