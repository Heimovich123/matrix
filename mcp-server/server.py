import os
import asyncio
import ssl
import json
import threading
import urllib.request
from mcp.server.fastmcp import FastMCP
from nio import AsyncClient, RoomMessageText

mcp = FastMCP("matrix-network")

MATRIX_HOMESERVER = os.getenv("MATRIX_HOMESERVER", "https://artem-vpn-server.duckdns.org:8448")
MATRIX_USERNAME = os.getenv("MATRIX_USERNAME")
MATRIX_PASSWORD = os.getenv("MATRIX_PASSWORD")

# Глобальный флаг для предотвращения повторного запуска монитора
monitor_started = False

def load_env_credentials():
    """Ищет файлы .env на хосте и в контейнере для загрузки токенов Telegram."""
    paths = ["/opt/data/.env", "/root/.hermes/.env", ".env"]
    env_vars = {}
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            env_vars[k.strip()] = v.strip()
                break  # Загружаем из первого найденного
            except Exception:
                pass
    return env_vars

def send_telegram_notification(text):
    """Отправляет уведомление в Telegram-чат владельца."""
    env = load_env_credentials()
    bot_token = env.get("TELEGRAM_BOT_TOKEN")
    chat_id = env.get("TELEGRAM_HOME_CHANNEL") or env.get("TELEGRAM_ALLOWED_USERS")
    
    if not bot_token or not chat_id:
        print("[Monitor] Telegram credentials not found in env.")
        return
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            response.read()
    except Exception as e:
        print(f"[Monitor] Failed to send Telegram notification: {e}")

async def matrix_monitor_loop():
    """Фоновый цикл прослушивания сообщений в Matrix."""
    if not MATRIX_USERNAME or not MATRIX_PASSWORD:
        print("[Monitor] Matrix credentials not set. Monitor disabled.")
        return
        
    username = MATRIX_USERNAME
    if not username.startswith("@"):
        domain = MATRIX_HOMESERVER.replace("https://", "").replace("http://", "").split(":")[0]
        username = f"@{username}:{domain}"
        
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print(f"[Monitor] Starting Matrix listener for user {username}...")
    client = AsyncClient(MATRIX_HOMESERVER, username)
    
    try:
        await client.login(MATRIX_PASSWORD)
        
        # 1. Первая синхронизация: получаем актуальное состояние (next_batch) и игнорируем историю
        print("[Monitor] Performing initial sync to discard history...")
        await client.sync(timeout=5000)
        
        # 2. Бесконечный цикл синхронизации для новых сообщений
        print("[Monitor] Monitor active. Listening for new messages...")
        while True:
            response = await client.sync(timeout=30000)
            if hasattr(response, "rooms") and response.rooms.join:
                for room_id, joined_room in response.rooms.join.items():
                    for event in joined_room.timeline.events:
                        if isinstance(event, RoomMessageText):
                            if event.sender != username:
                                print(f"[Monitor] New message from {event.sender}: {event.body}")
                                clean_sender = event.sender.split(":")[0].replace("@", "")
                                text = f"🤖 *Matrix-Сеть*\n👤 *Агент:* `{clean_sender}`\n💬 *Сообщение:* {event.body}"
                                send_telegram_notification(text)
    except Exception as e:
        print(f"[Monitor] Matrix connection error in thread: {e}")
    finally:
        await client.close()

def start_background_monitor():
    """Запускает Matrix-монитор в отдельном потоке с межпроцессной блокировкой."""
    global monitor_started
    if monitor_started:
        return
    monitor_started = True
    
    def run():
        # Межпроцессный лок, чтобы избежать запуска монитора в параллельных процессах Гермеса
        try:
            import fcntl
            lock_file = open('/tmp/matrix_monitor.lock', 'w')
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Сохраняем ссылку на файл, чтобы сборщик мусора не закрыл его и не снял лок
            run.lock_file = lock_file
        except (ImportError, IOError, OSError):
            # В Windows fcntl нет (для тестов), на Linux/Docker он сработает.
            # Если захватить лок не удалось, выходим
            print("[Monitor] Already running in another process or lock failed. Aborting.")
            return
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(matrix_monitor_loop())
        
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

# Автоматически запускаем фоновый поток при импорте/старте MCP-сервера
start_background_monitor()

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

@mcp.tool()
async def send_matrix_file(room_id: str, file_path: str, filename: str = None) -> str:
    """Загрузить локальный файл на Matrix медиа-сервер и отправить его в указанную комнату."""
    import mimetypes
    import urllib.parse
    
    if not os.path.exists(file_path):
        return f"Error: File not found at path: {file_path}"
        
    if not filename:
        filename = os.path.basename(file_path)
        
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"
        
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        file_size = len(file_data)
        
        # Получаем токен
        import urllib.request, json, ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        login_url = f"{MATRIX_HOMESERVER}/_matrix/client/v3/login"
        login_data = {
            "type": "m.login.password",
            "identifier": {"type": "m.id.user", "user": MATRIX_USERNAME.replace("@", "").split(":")[0]},
            "password": MATRIX_PASSWORD
        }
        req = urllib.request.Request(login_url, data=json.dumps(login_data).encode(), headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req, context=ctx) as resp:
            token = json.loads(resp.read().decode())["access_token"]
            
        # Загружаем на медиа-сервер
        upload_url = f"{MATRIX_HOMESERVER}/_matrix/media/v3/upload?filename={urllib.parse.quote(filename)}"
        req_upload = urllib.request.Request(
            upload_url,
            data=file_data,
            headers={
                "Content-Type": mime_type,
                "Authorization": f"Bearer {token}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req_upload, context=ctx) as resp_upload:
            res_upload = json.loads(resp_upload.read().decode())
            content_uri = res_upload["content_uri"]
            
        # Отправляем m.file событие
        client = await get_client()
        content = {
            "msgtype": "m.file",
            "body": filename,
            "url": content_uri,
            "info": {
                "size": file_size,
                "mimetype": mime_type
            }
        }
        resp = await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content=content
        )
        await client.close()
        return f"Success: File sent. Content URI: {content_uri}, Event ID: {resp.event_id}"
    except Exception as e:
        return f"Error sending file: {e}"

if __name__ == "__main__":
    mcp.run()
EOF
