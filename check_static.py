import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # Let's check status code of a static file and a media file
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w \"%{http_code}\" http://127.0.0.1:8080/static/css/index.css")
    print("STATIC CSS:", stdout.read().decode().strip())

    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w \"%{http_code}\" http://127.0.0.1:8080/media/images/placeholder.png")
    print("MEDIA:", stdout.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
