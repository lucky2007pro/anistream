import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    commands = [
        "pkill -f 'gunicorn core.wsgi:application'",
        "cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &",
        "sleep 3",
        "curl -s http://127.0.0.1:8080 > /dev/null",
        "cat /opt/anistream/gunicorn.log"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if cmd.startswith("cat"):
            print("LOGS:\n", out)
            if err: print("ERR:\n", err)

    ssh.close()
except Exception as e:
    print(f"Error: {e}")
