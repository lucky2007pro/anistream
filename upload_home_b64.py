import paramiko
import base64

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

local_home = r"d:\anime\anistream\anime\templates\home.html"

try:
    with open(local_home, 'rb') as f:
        home_content_b64 = base64.b64encode(f.read()).decode('utf-8')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = f"""
import base64
content = base64.b64decode('{home_content_b64}').decode('utf-8')
try:
    with open('/opt/anistream/anime/templates/home.html', 'w') as f:
        f.write(content)
    print("Wrote to opt")
except Exception as e:
    print("opt:", e)

try:
    with open('/root/anistream/anime/templates/home.html', 'w') as f:
        f.write(content)
    print("Wrote to root")
except Exception as e:
    print("root:", e)
"""
    cmd = f'cat << "EOF" > /tmp/write_home.py\n{script}\nEOF\npython3 /tmp/write_home.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:\n", stdout.read().decode().strip())
    print("ERR:\n", stderr.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
