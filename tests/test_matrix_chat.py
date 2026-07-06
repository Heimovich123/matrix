import asyncio
import ssl
from nio import AsyncClient, RoomMessageText

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # 1. Отправляем сообщение от @antigravity
    print("Logging in as @antigravity...")
    client_anti = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await client_anti.login("antigravity_pass_123")
    
    print("Sending test message...")
    await client_anti.room_send(
        room_id=ROOM_ID,
        message_type="m.room.message",
        content={"msgtype": "m.text", "body": "Привет, Hermes! Это Antigravity. Мы теперь в одной сети!"}
    )
    await client_anti.close()
    print("Message sent.")
    
    # 2. Читаем сообщения от имени @hermes_my
    print("\nLogging in as @hermes_my...")
    client_hermes = AsyncClient(HOMESERVER, "@hermes_my:artem-vpn-server.duckdns.org")
    await client_hermes.login("hermes_pass_123")
    
    print("Reading room messages...")
    resp = await client_hermes.room_messages(ROOM_ID, limit=5)
    await client_hermes.close()
    
    if hasattr(resp, "chunk"):
        print("\nLast messages in room:")
        for event in reversed(resp.chunk):
            if isinstance(event, RoomMessageText):
                print(f"[{event.sender}]: {event.body}")
    else:
        print(f"Failed to read messages: {resp}")

if __name__ == "__main__":
    asyncio.run(main())
