import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    stdin, stdout, stderr = ssh.exec_command("cp /opt/anistream/static/images/favicon.svg /opt/anistream/static/images/anistream-logo.svg")
    print("OUT:", stdout.read().decode().strip())
    print("ERR:", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
