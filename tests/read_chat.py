import asyncio
import ssl
import sys
from nio import AsyncClient, RoomMessageText

sys.stdout.reconfigure(encoding='utf-8')

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Logging in as @antigravity...")
    client_anti = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await client_anti.login("antigravity_pass_123")
    
    print("Reading room messages...")
    resp = await client_anti.room_messages(ROOM_ID, limit=10)
    await client_anti.close()
    
    if hasattr(resp, "chunk"):
        print("\n=== MATRIX CHAT HISTORY ===")
        for event in reversed(resp.chunk):
            if isinstance(event, RoomMessageText):
                # Печатаем в UTF-8
                print(f"[{event.sender}]: {event.body}")
        print("===========================")
    else:
        print(f"Failed to read messages: {resp}")

if __name__ == "__main__":
    asyncio.run(main())
