import asyncio
import ssl
from nio import AsyncClient

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"
TARGET_USER = "@agentadcc49:artem-vpn-server.duckdns.org"
TARGET_PASS = "HrpyIdAbzFiMe1Q0"

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # 1. Логинимся за админа @antigravity и отправляем инвайт
    print("Logging in as @antigravity to send invite...")
    admin_client = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await admin_client.login("antigravity_pass_123")
    
    print(f"Inviting {TARGET_USER} to room...")
    resp_invite = await admin_client.room_invite(ROOM_ID, TARGET_USER)
    print(f"Invite Response: {resp_invite}")
    await admin_client.close()

    # 2. Логинимся за нового агента и делаем join
    # Используем raw HTTP для обхода бага deserialization в matrix-nio
    print(f"Logging in as {TARGET_USER} to accept invite...")
    import urllib.request, json
    
    login_url = f"{HOMESERVER}/_matrix/client/v3/login"
    login_data = {
        "type": "m.login.password",
        "identifier": {"type": "m.id.user", "user": TARGET_USER.replace("@", "").split(":")[0]},
        "password": TARGET_PASS
    }
    req = urllib.request.Request(login_url, data=json.dumps(login_data).encode(), headers={"Content-Type": "application/json"}, method='POST')
    with urllib.request.urlopen(req, context=ctx) as resp:
        token = json.loads(resp.read().decode())["access_token"]
        
    print("Accepting invite via raw HTTP POST...")
    join_url = f"{HOMESERVER}/_matrix/client/v3/join/{ROOM_ID}"
    req_join = urllib.request.Request(join_url, data=b"{}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, method='POST')
    with urllib.request.urlopen(req_join, context=ctx) as resp_join:
        res = json.loads(resp_join.read().decode())
        print(f"Success! Joined room. Room ID: {res['room_id']}")

if __name__ == "__main__":
    asyncio.run(main())
