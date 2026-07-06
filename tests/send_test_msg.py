import asyncio
import ssl
from nio import AsyncClient

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print("Logging in as @antigravity...")
    client = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await client.login("antigravity_pass_123")
    
    msg = "Привет, @hermesray! Твой агент успешно вошел в зашифрованный канал ИИ-агентов. Связь установлена!"
    print(f"Sending message: {msg}")
    resp = await client.room_send(
        room_id=ROOM_ID,
        message_type="m.room.message",
        content={"msgtype": "m.text", "body": msg}
    )
    print(f"Message sent. Response: {resp}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
