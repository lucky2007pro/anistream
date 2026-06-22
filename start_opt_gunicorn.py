import paramiko
import time

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    ssh.exec_command("bash -c 'cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &'")
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w \"%{http_code}\" http://127.0.0.1:8080/")
    print("OPT STATUS:", stdout.read().decode().strip())

    ssh.close()
except Exception as e:
    print(f"Error: {e}")
