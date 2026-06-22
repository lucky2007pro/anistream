import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    ssh.exec_command("pkill -9 -f gunicorn")
    ssh.exec_command("rm -rf /opt/anistream/core/__pycache__/")
    ssh.exec_command("cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &")
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
