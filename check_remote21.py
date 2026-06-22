import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    cmd = "cd /opt/anistream && export DEBUG=True && /opt/anistream/venv/bin/python manage.py runserver 0.0.0.0:8083 > /opt/anistream/dev_chat.log 2>&1 & sleep 5 && curl -s http://127.0.0.1:8083/chat/ > /dev/null && pkill -f 'manage.py runserver 0.0.0.0:8083' && cat /opt/anistream/dev_chat.log | grep -A 30 'Traceback'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    out = stdout.read().decode().strip()
    print("OUTPUT:\n", out)
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
