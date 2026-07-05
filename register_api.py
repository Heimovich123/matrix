import asyncio
import ssl
import json
from aiohttp import web
from nio import AsyncClient, RoomMessageText

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ADMIN_ROOM_ID = "!DM6xDke9VSSmuCV5kxv3M7qmITVmedAPJde12Btb25o"
NETWORK_ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"
ADMIN_USER = "@antigravity:artem-vpn-server.duckdns.org"
ADMIN_PASS = "antigravity_pass_123"

# SSL Контекст для работы по HTTPS с самоподписанными/внутренними серверами
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

async def create_matrix_user(username, password):
    """Отправляет команду создания пользователя в админ-комнату Conduit и ждет ответа."""
    client = AsyncClient(HOMESERVER, ADMIN_USER)
    try:
        await client.login(ADMIN_PASS)
    except Exception as e:
        return {"status": "error", "message": f"Admin login failed: {e}"}

    cmd = f"@conduit:artem-vpn-server.duckdns.org: create-user {username} {password}"
    print(f"[API] Sending command to admin room: {cmd}")
    
    try:
        await client.room_send(
            room_id=ADMIN_ROOM_ID,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": cmd}
        )
    except Exception as e:
        await client.close()
        return {"status": "error", "message": f"Failed to send admin command: {e}"}

    # Опрашиваем комнату в течение 6 секунд в поисках ответа бота
    success_text = f"Created user with user_id:"
    for attempt in range(12):
        await asyncio.sleep(0.5)
        try:
            resp_msg = await client.room_messages(ADMIN_ROOM_ID, limit=5)
            if hasattr(resp_msg, "chunk"):
                for event in resp_msg.chunk:
                    if (
                        isinstance(event, RoomMessageText)
                        and event.sender == "@conduit:artem-vpn-server.duckdns.org"
                        and success_text in event.body
                        and username in event.body
                    ):
                        print(f"[API] Registration confirmed by Conduit bot: {event.body}")
                        # Отправляем инвайт новому пользователю в нашу ОБЩУЮ комнату
                        target_user_id = f"@{username}:artem-vpn-server.duckdns.org"
                        print(f"[API] Inviting {target_user_id} to network room {NETWORK_ROOM_ID}...")
                        try:
                            await client.room_invite(NETWORK_ROOM_ID, target_user_id)
                            print(f"[API] Invite sent successfully.")
                        except Exception as inv_err:
                            print(f"[API] Failed to send invite: {inv_err}")
                        await client.close()
                        return {"status": "success", "user_id": target_user_id}
        except Exception as e:
            print(f"[API] Error reading messages: {e}")
            
    await client.close()
    return {"status": "error", "message": "Conduit admin bot response timeout"}

async def handle_register(request):
    """Обработчик POST-запросов на /register."""
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"status": "error", "message": "Invalid JSON"}, status=400)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return web.json_response({"status": "error", "message": "Username and password are required"}, status=400)

    # Простая валидация логина (латиница и цифры)
    if not username.isalnum():
        return web.json_response({"status": "error", "message": "Username must be alphanumeric"}, status=400)

    print(f"[API] Received registration request for user: {username}")
    res = await create_matrix_user(username, password)
    
    if res["status"] == "success":
        return web.json_response(res, status=200)
    else:
        return web.json_response(res, status=500)

async def handle_dashboard(request):
    """Отдает страницу дашборда управления."""
    import os
    try:
        paths = ["/opt/amn-api/dashboard.html", os.path.join(os.path.dirname(__file__), "dashboard.html"), "dashboard.html"]
        html = None
        for p in paths:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    html = f.read()
                break
        if html is None:
            raise FileNotFoundError("dashboard.html not found in any of the search paths")
        return web.Response(text=html, content_type="text/html")
    except Exception as e:
        return web.Response(text=f"Error loading dashboard: {e}", status=500)

async def handle_status(request):
    """Возвращает статус сети, список активных участников и историю сообщений."""
    client = AsyncClient(HOMESERVER, ADMIN_USER)
    try:
        await client.login(ADMIN_PASS)
        # Быстрая синхронизация для обновления состояния комнат
        await client.sync(timeout=3000)
        
        room = client.rooms.get(NETWORK_ROOM_ID)
        members = list(room.users.keys()) if room else []
        
        # Получаем последние 20 сообщений
        resp_msg = await client.room_messages(NETWORK_ROOM_ID, limit=20)
        messages = []
        if hasattr(resp_msg, "chunk"):
            for event in reversed(resp_msg.chunk):
                if isinstance(event, RoomMessageText):
                    messages.append({
                        "sender": event.sender,
                        "body": event.body,
                        "timestamp": event.server_timestamp
                    })
                    
        await client.close()
        return web.json_response({
            "status": "success",
            "members": members,
            "messages": messages
        })
    except Exception as e:
        try:
            await client.close()
        except Exception:
            pass
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def handle_send_test(request):
    """Отправляет тестовое сообщение в Matrix-сеть."""
    client = AsyncClient(HOMESERVER, ADMIN_USER)
    try:
        await client.login(ADMIN_PASS)
        await client.room_send(
            room_id=NETWORK_ROOM_ID,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": "Тестовое сообщение из панели управления AMN Control Center!"}
        )
        await client.close()
        return web.json_response({"status": "success"})
    except Exception as e:
        try:
            await client.close()
        except Exception:
            pass
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def init_app():
    app = web.Application()
    app.router.add_post('/register', handle_register)
    app.router.add_get('/dashboard', handle_dashboard)
    app.router.add_get('/api/status', handle_status)
    app.router.add_post('/api/send_test', handle_send_test)
    return app

if __name__ == '__main__':
    app = asyncio.run(init_app())
    print("[API] Starting Registration API server on port 5000...")
    web.run_app(app, host='0.0.0.0', port=5000)
