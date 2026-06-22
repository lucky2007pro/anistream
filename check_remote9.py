import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    cmd_migrate = "cd /opt/anistream && /opt/anistream/venv/bin/python manage.py showmigrations"
    stdin, stdout, stderr = ssh.exec_command(cmd_migrate)
    print("SHOWMIGRATIONS:", stdout.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
