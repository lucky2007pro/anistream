import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
"""
    cmd = f'cat << "EOF" > /opt/anistream/drop_db2.py\n{script}\nEOF\n/opt/anistream/venv/bin/python /opt/anistream/drop_db2.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("DROP OUT:", stdout.read().decode().strip())
    print("DROP ERR:", stderr.read().decode().strip())

    # Run migrate again
    cmd_migrate = "cd /opt/anistream && /opt/anistream/venv/bin/python manage.py migrate"
    stdin, stdout, stderr = ssh.exec_command(cmd_migrate)
    print("MIGRATE OUT:", stdout.read().decode().strip())
    print("MIGRATE ERR:", stderr.read().decode().strip())
    
    # Restart gunicorn
    ssh.exec_command("pkill -f 'gunicorn core.wsgi:application'")
    ssh.exec_command("cd /opt/anistream && nohup /opt/anistream/venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8080 > /opt/anistream/gunicorn.log 2>&1 &")
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
