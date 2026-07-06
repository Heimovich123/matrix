with open("/etc/nginx/conf.d/matrix.conf", "r") as f:
    content = f.read()

# Проверяем, нет ли уже правила
if "location /register_amn" not in content:
    location_block = """
    location /register_amn {
        proxy_pass http://127.0.0.1:5000/register;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
"""
    # Вставляем перед последней закрывающей фигурной скобкой
    last_brace_idx = content.rfind("}")
    if last_brace_idx != -1:
        new_content = content[:last_brace_idx] + location_block + content[last_brace_idx:]
        with open("/etc/nginx/conf.d/matrix.conf", "w") as f:
            f.write(new_content)
        print("matrix.conf patched successfully.")
    else:
        print("Error: closing brace not found in config.")
else:
    print("matrix.conf already patched.")
