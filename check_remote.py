import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # Run the server temporarily with gunicorn in foreground and make a curl request to see the error output
    cmd = "cd /opt/anistream && /opt/anistream/venv/bin/python manage.py check"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("CHECK OUT:", stdout.read().decode().strip())
    print("CHECK ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
