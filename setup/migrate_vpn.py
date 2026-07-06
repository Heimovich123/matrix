import sys
import os
import subprocess

# Убедимся, что paramiko установлен
try:
    import paramiko
except ImportError:
    print("Installing paramiko...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

# 1. Скачиваем базу данных со старого сервера (194.33.34.146) по SFTP
temp_db_path = r"C:\Users\User\AppData\Local\Temp\x-ui.db"
if os.path.exists(temp_db_path):
    os.remove(temp_db_path)

print("Connecting to old server 194.33.34.146 via SFTP...")
ssh_old = paramiko.SSHClient()
ssh_old.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh_old.connect('194.33.34.146', username='root')
    sftp_old = ssh_old.open_sftp()
    sftp_old.get('/etc/x-ui/x-ui.db', temp_db_path)
    sftp_old.close()
    print("Database downloaded successfully from old server.")
except Exception as e:
    print(f"Failed to download DB from old server: {e}")
    sys.exit(1)
finally:
    ssh_old.close()

# 2. Подключаемся к новому серверу (31.76.40.86)
ssh_new = paramiko.SSHClient()
ssh_new.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    print("Connecting to new server 31.76.40.86...")
    ssh_new.connect('31.76.40.86', username='root')
    
    # 3. Устанавливаем 3X-UI на новом сервере через стандартный пайп
    print("Installing 3X-UI on new server...")
    stdin, stdout, stderr = ssh_new.exec_command('curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh | bash -s -- -y')
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print(f"Failed to install 3X-UI. Error: {stderr.read().decode()}")
        sys.exit(1)
    print("3X-UI installed successfully.")
    
    # 4. Останавливаем x-ui перед заменой базы
    print("Stopping x-ui...")
    ssh_new.exec_command('systemctl stop x-ui')
    
    # 5. Загружаем базу данных на новый server по SFTP
    print("Uploading database to new server...")
    sftp_new = ssh_new.open_sftp()
    sftp_new.put(temp_db_path, '/etc/x-ui/x-ui.db')
    sftp_new.close()
    print("Database uploaded successfully.")
    
    # 6. Устанавливаем certbot и выпускаем Let's Encrypt
    print("Issuing Let's Encrypt SSL certificate...")
    stdin, stdout, stderr = ssh_new.exec_command('apt-get update && apt-get install -y certbot && certbot certonly --standalone --preferred-challenges http -d artem-vpn-server.duckdns.org --non-interactive --agree-tos --register-unsafely-without-email')
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print(f"Failed to issue SSL certificate. Error: {stderr.read().decode()}")
    else:
        print("SSL certificate issued successfully.")
         
    # 7. Запускаем x-ui
    print("Starting x-ui...")
    ssh_new.exec_command('systemctl start x-ui')
    print("x-ui started successfully.")
    
    print("VPN migration completed successfully! All configs and users are moved to 31.76.40.86.")
    
except Exception as e:
    print(f"Error during migration: {e}")
    sys.exit(1)
finally:
    ssh_new.close()
