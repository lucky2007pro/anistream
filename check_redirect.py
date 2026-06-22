import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    stdin, stdout, stderr = ssh.exec_command("curl -I http://127.0.0.1/.well-known/acme-challenge/test -H 'Host: anistream.dev'")
    print("OUT:", stdout.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
