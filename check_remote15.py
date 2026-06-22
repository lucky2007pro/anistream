import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    script = """
import psycopg
conn = psycopg.connect("postgresql://bestmedia_admin:hojiakbar_db_pass@127.0.0.1:5432/anistream")
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
tables = cur.fetchall()
print("TABLES:", [t[0] for t in tables])
cur.close()
conn.close()
"""
    cmd = f'cat << "EOF" > /opt/anistream/check_tables.py\n{script}\nEOF\n/opt/anistream/venv/bin/python /opt/anistream/check_tables.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUTPUT:", stdout.read().decode().strip())
    print("ERROR:", stderr.read().decode().strip())

    ssh.close()
except Exception as e:
    print(f"Error: {e}")
