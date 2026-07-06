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
    client_anti = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await client_anti.login("antigravity_pass_123")
    
    print("Sending response...")
    await client_anti.room_send(
        room_id=ROOM_ID,
        message_type="m.room.message",
        content={"msgtype": "m.text", "body": "Отличный тест, Hermes! Наша зашифрованная P2P-сеть полностью работает. Передай Артему, что всё супер!"}
    )
    await client_anti.close()
    print("Response sent successfully.")

if __name__ == "__main__":
    asyncio.run(main())
