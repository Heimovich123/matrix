#!/bin/bash
set -e

echo "=== AMN Agent Auto-Installer ==="

# 1. Создаем папку для MCP-сервера в директории данных Hermes
echo "Creating mcp-server directory..."
mkdir -p /root/.hermes/mcp-server

# 2. Записываем server.py на хост
echo "Writing server.py..."
cat << 'EOF' > /root/.hermes/mcp-server/server.py
import os
import asyncio
from mcp.server.fastmcp import FastMCP
from nio import AsyncClient, RoomMessageText

mcp = FastMCP("matrix-network")

MATRIX_HOMESERVER = os.getenv("MATRIX_HOMESERVER", "https://artem-vpn-server.duckdns.org:8448")
MATRIX_USERNAME = os.getenv("MATRIX_USERNAME")
MATRIX_PASSWORD = os.getenv("MATRIX_PASSWORD")

async def get_client():
    if not MATRIX_USERNAME or not MATRIX_PASSWORD:
        raise ValueError("MATRIX_USERNAME and MATRIX_PASSWORD env vars must be set")
    username = MATRIX_USERNAME
    if not username.startswith("@"):
        domain = MATRIX_HOMESERVER.replace("https://", "").replace("http://", "").split(":")[0]
        username = f"@{username}:{domain}"
    client = AsyncClient(MATRIX_HOMESERVER, username)
    await client.login(MATRIX_PASSWORD)
    return client

@mcp.tool()
async def send_matrix_message(room_id: str, message: str) -> str:
    """Отправить текстовое сообщение в комнату Matrix."""
    try:
        client = await get_client()
        resp = await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )
        await client.close()
        return f"Success: Message sent. Event ID: {resp.event_id}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
async def read_matrix_messages(room_id: str, limit: int = 10) -> str:
    """Прочитать последние сообщения из указанной комнаты Matrix."""
    try:
        client = await get_client()
        resp = await client.room_messages(room_id, limit=limit)
        await client.close()
        if hasattr(resp, "chunk"):
            messages = []
            for event in reversed(resp.chunk):
                if isinstance(event, RoomMessageText):
                    messages.append(f"{event.sender}: {event.body}")
            return "\n".join(messages) if messages else "No messages."
        return f"Error: {resp}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
async def join_matrix_room(room_id: str) -> str:
    """Войти в комнату Matrix по её Room ID."""
    try:
        import urllib.request, json, ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Получаем токен
        login_url = f"{MATRIX_HOMESERVER}/_matrix/client/v3/login"
        login_data = {
            "type": "m.login.password",
            "identifier": {"type": "m.id.user", "user": MATRIX_USERNAME.replace("@", "").split(":")[0]},
            "password": MATRIX_PASSWORD
        }
        req = urllib.request.Request(login_url, data=json.dumps(login_data).encode(), headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req, context=ctx) as resp:
            token = json.loads(resp.read().decode())["access_token"]
            
        # Делаем join с пустым {}
        join_url = f"{MATRIX_HOMESERVER}/_matrix/client/v3/join/{room_id}"
        req_join = urllib.request.Request(join_url, data=b"{}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, method='POST')
        with urllib.request.urlopen(req_join, context=ctx) as resp_join:
            res = json.loads(resp_join.read().decode())
            return f"Success: Joined room. Room ID: {res['room_id']}"
    except Exception as e:
        return f"Error during join: {e}"

if __name__ == "__main__":
    mcp.run()
EOF

# 3. Устанавливаем pip во venv Гермеса (если его нет) и зависимости
if ! docker exec hermes /opt/hermes/.venv/bin/python -m pip --version &>/dev/null; then
    echo "pip not found in Hermes venv. Installing via get-pip.py..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | docker exec -i hermes /opt/hermes/.venv/bin/python
fi

echo "Installing python dependencies inside Hermes venv..."
docker exec hermes /opt/hermes/.venv/bin/pip install mcp matrix-nio cryptography cachetools atomicwrites peewee

# 4. Модифицируем config.yaml с помощью встроенного Python
echo "Updating config.yaml with MCP server configurations..."
python3 - << 'EOF'
import yaml

config_path = '/root/.hermes/config.yaml'

with open(config_path, 'r') as f:
    config = yaml.safe_load(f) or {}

if 'mcp_servers' not in config:
    config['mcp_servers'] = {}

config['mcp_servers']['matrix-network'] = {
    'command': '/opt/hermes/.venv/bin/python',
    'args': ['/opt/data/mcp-server/server.py'],
    'env': {
        'MATRIX_HOMESERVER': 'https://artem-vpn-server.duckdns.org:8448',
        'MATRIX_USERNAME': 'hermes_my',
        'MATRIX_PASSWORD': 'hermes_pass_123'
    }
}

with open(config_path, 'w') as f:
    yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)

print("config.yaml updated successfully.")
EOF

# 5. Перезапускаем контейнер Hermes для применения настроек
echo "Restarting Hermes container..."
docker restart hermes

echo "=== AMN installation completed successfully! ==="
