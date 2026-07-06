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

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to 31.76.40.86 using password...")
    ssh.connect('31.76.40.86', username='root', password='lxERp1PBxjPm', timeout=15)
    
    # Ищем ed25519 публичный ключ в Windows
    pub_key_path = os.path.expanduser('~/.ssh/id_ed25519.pub')
    if os.path.exists(pub_key_path):
        with open(pub_key_path, 'r') as f:
            pub_key = f.read().strip()
        print(f"Adding local SSH key ({pub_key_path}) to authorized_keys on 31.76.40.86...")
        ssh.exec_command(f'mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo "{pub_key}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys')
        print("SSH key added successfully!")
    else:
        print("Error: id_ed25519.pub not found!")
        sys.exit(1)
        
except Exception as e:
    print(f"Error during SSH setup: {e}")
    sys.exit(1)
finally:
    ssh.close()
