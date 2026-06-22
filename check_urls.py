import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    stdin, stdout, stderr = ssh.exec_command("cat /opt/anistream/core/urls.py")
    print("URLS:", stdout.read().decode().strip()[-500:])
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
