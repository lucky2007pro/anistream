import paramiko
import time

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    print("Connected successfully!")
    
    commands = [
        "cd /opt/anistream && git pull",
        "cd /opt/anistream && source venv/bin/activate && python3 manage.py migrate",
        "pkill -f 'gunicorn core.wsgi:application --bind 0.0.0.0:8080'",
        "cd /opt/anistream && source venv/bin/activate && gunicorn core.wsgi:application --bind 0.0.0.0:8080 --daemon"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out: print(f"OUT: {out}")
        if err: print(f"ERR: {err}")
        time.sleep(2)

    ssh.close()
    print("Deployment done!")
except Exception as e:
    print(f"Error: {e}")
