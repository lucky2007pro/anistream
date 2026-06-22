import paramiko

host = "161.97.142.166"
user = "root"
password = "hojiakbar"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    html_500 = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>500 Server Xatosi</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { margin: 0; padding: 0; background-color: #1a151d; font-family: 'Outfit', sans-serif; color: white; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .error-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px; }
        .error-code { font-size: 180px; font-weight: 900; background: linear-gradient(to right, #ff416c, #ff8f00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; line-height: 1; }
        .error-icon { font-size: 100px; margin: 10px 0 20px 0; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.5)); }
        .error-title { font-size: 40px; font-weight: 800; margin: 0 0 15px 0; }
        .error-text { color: #a0a0a0; font-size: 18px; max-width: 500px; margin: 0 0 35px 0; line-height: 1.6; }
        .btn-group { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
        .btn-primary { background: linear-gradient(to right, #ff416c, #ff4b2b); color: white; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 16px; text-decoration: none; border: none; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4); display: flex; align-items: center; gap: 8px; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6); }
        .btn-secondary { background: #2a2a35; color: white; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 16px; text-decoration: none; transition: 0.3s; border: 1px solid #3d3d4e; display: flex; align-items: center; gap: 8px; }
        .btn-secondary:hover { background: #353542; transform: translateY(-2px); }
        @media (max-width: 600px) { .error-code { font-size: 120px; } .error-icon { font-size: 70px; } .error-title { font-size: 28px; } .error-text { font-size: 15px; } .btn-group { flex-direction: column; } }
    </style>
</head>
<body>
    <div class="error-container">
        <h1 class="error-code">500</h1>
        <div class="error-icon">⚠️</div>
        <h2 class="error-title">Server Xatosi</h2>
        <p class="error-text">
            Kechirasiz, serverda texnik nosozlik yuz berdi. Bizning jamoamiz muammoni hal qilish ustida ishlayapti. Iltimos, biroz vaqt o'tgach qayta urinib ko'ring.
        </p>
        <div class="btn-group">
            <a href="javascript:location.reload();" class="btn-primary">
                <i class="fas fa-sync-alt"></i> Qayta urinish
            </a>
            <a href="/" class="btn-secondary">
                <i class="fas fa-home"></i> Bosh sahifaga qaytish
            </a>
        </div>
    </div>
</body>
</html>"""

    html_404 = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 Sahifa topilmadi</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { margin: 0; padding: 0; background-color: #1a151d; font-family: 'Outfit', sans-serif; color: white; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .error-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px; }
        .error-code { font-size: 180px; font-weight: 900; background: linear-gradient(to right, #ff416c, #ff8f00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; line-height: 1; }
        .error-icon { font-size: 100px; margin: 10px 0 20px 0; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.5)); }
        .error-title { font-size: 40px; font-weight: 800; margin: 0 0 15px 0; }
        .error-text { color: #a0a0a0; font-size: 18px; max-width: 500px; margin: 0 0 35px 0; line-height: 1.6; }
        .btn-group { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
        .btn-primary { background: linear-gradient(to right, #ff416c, #ff4b2b); color: white; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 16px; text-decoration: none; border: none; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4); display: flex; align-items: center; gap: 8px; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6); }
        .btn-secondary { background: #2a2a35; color: white; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 16px; text-decoration: none; transition: 0.3s; border: 1px solid #3d3d4e; display: flex; align-items: center; gap: 8px; }
        .btn-secondary:hover { background: #353542; transform: translateY(-2px); }
        @media (max-width: 600px) { .error-code { font-size: 120px; } .error-icon { font-size: 70px; } .error-title { font-size: 28px; } .error-text { font-size: 15px; } .btn-group { flex-direction: column; } }
    </style>
</head>
<body>
    <div class="error-container">
        <h1 class="error-code">404</h1>
        <div class="error-icon">🔍</div>
        <h2 class="error-title">Sahifa topilmadi</h2>
        <p class="error-text">
            Kechirasiz, siz qidirayotgan sahifa mavjud emas yoki o'chirilgan bo'lishi mumkin. Manzilni to'g'ri kiritganingizni tekshiring.
        </p>
        <div class="btn-group">
            <a href="/" class="btn-primary">
                <i class="fas fa-home"></i> Bosh sahifaga qaytish
            </a>
            <a href="javascript:history.back();" class="btn-secondary">
                <i class="fas fa-arrow-left"></i> Orqaga qaytish
            </a>
        </div>
    </div>
</body>
</html>"""

    html_403 = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>403 Ruxsat etilmagan</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { margin: 0; padding: 0; background-color: #1a151d; font-family: 'Outfit', sans-serif; color: white; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .error-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px; }
        .error-code { font-size: 180px; font-weight: 900; background: linear-gradient(to right, #ff416c, #ff8f00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; line-height: 1; }
        .error-icon { font-size: 100px; margin: 10px 0 20px 0; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.5)); }
        .error-title { font-size: 40px; font-weight: 800; margin: 0 0 15px 0; }
        .error-text { color: #a0a0a0; font-size: 18px; max-width: 500px; margin: 0 0 35px 0; line-height: 1.6; }
        .btn-group { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
        .btn-primary { background: linear-gradient(to right, #ff416c, #ff4b2b); color: white; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 16px; text-decoration: none; border: none; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4); display: flex; align-items: center; gap: 8px; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6); }
        .btn-secondary { background: #2a2a35; color: white; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 16px; text-decoration: none; transition: 0.3s; border: 1px solid #3d3d4e; display: flex; align-items: center; gap: 8px; }
        .btn-secondary:hover { background: #353542; transform: translateY(-2px); }
        @media (max-width: 600px) { .error-code { font-size: 120px; } .error-icon { font-size: 70px; } .error-title { font-size: 28px; } .error-text { font-size: 15px; } .btn-group { flex-direction: column; } }
    </style>
</head>
<body>
    <div class="error-container">
        <h1 class="error-code">403</h1>
        <div class="error-icon">🔒</div>
        <h2 class="error-title">Ruxsat etilmagan</h2>
        <p class="error-text">
            Kechirasiz, sizda ushbu sahifaga kirish uchun ruxsat yo'q. Agar bu xatolik deb hisoblasangiz, admin bilan bog'laning.
        </p>
        <div class="btn-group">
            <a href="/" class="btn-primary">
                <i class="fas fa-home"></i> Bosh sahifaga qaytish
            </a>
            <a href="javascript:history.back();" class="btn-secondary">
                <i class="fas fa-arrow-left"></i> Orqaga qaytish
            </a>
        </div>
    </div>
</body>
</html>"""

    script = f"""
import os
path_500 = '/opt/anistream/anime/templates/500.html'
path_404 = '/opt/anistream/anime/templates/404.html'
path_403 = '/opt/anistream/anime/templates/403.html'

with open(path_500, 'w', encoding='utf-8') as f: f.write('''{html_500}''')
with open(path_404, 'w', encoding='utf-8') as f: f.write('''{html_404}''')
with open(path_403, 'w', encoding='utf-8') as f: f.write('''{html_403}''')
print("Error templates created successfully.")
"""
    cmd = f'cat << "EOF" > /opt/anistream/create_error_templates.py\n{script}\nEOF\n/opt/anistream/venv/bin/python /opt/anistream/create_error_templates.py'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("OUT:", stdout.read().decode().strip())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
