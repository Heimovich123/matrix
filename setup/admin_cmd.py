import asyncio
import ssl
from nio import AsyncClient, RoomMessageText

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!DM6xDke9VSSmuCV5kxv3M7qmITVmedAPJde12Btb25o"

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Logging in as @antigravity...")
    client = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await client.login("antigravity_pass_123")
    
    # Отправляем команду list-users
    cmd = "@conduit:artem-vpn-server.duckdns.org: list-users"
    print(f"Sending command: {cmd}")
    await client.room_send(
        room_id=ROOM_ID,
        message_type="m.room.message",
        content={"msgtype": "m.text", "body": cmd}
    )
    
    # Ждем 3 секунды
    print("Waiting for bot response...")
    await asyncio.sleep(3)
    
    # Читаем последние сообщения
    resp_msg = await client.room_messages(ROOM_ID, limit=10)
    await client.close()
    
    if hasattr(resp_msg, "chunk"):
        print("\n=== BOT RESPONSE ===")
        for event in reversed(resp_msg.chunk):
            if isinstance(event, RoomMessageText):
                print(f"[{event.sender}]: {event.body}")
        print("====================")

if __name__ == "__main__":
    asyncio.run(main())
