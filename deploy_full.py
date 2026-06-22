import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    print("Connected successfully!")
    
    commands = [
        "cd /opt/anistream && git stash",
        "cd /opt/anistream && git pull --force",
        "cd /opt/anistream && rm -f db.sqlite3",
        "cd /opt/anistream && /opt/anistream/venv/bin/python manage.py migrate",
        "pkill -f 'gunicorn core.wsgi:application --bind 0.0.0.0:8080'",
        "cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 --daemon > /dev/null 2>&1 &"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out: print(f"OUT: {out}")
        if err: print(f"ERR: {err}")

    ssh.close()
    print("Deployment done!")
except Exception as e:
    print(f"Error: {e}")
