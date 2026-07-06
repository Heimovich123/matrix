import asyncio
import ssl
from nio import AsyncClient

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Logging in as @antigravity...")
    client = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await client.login("antigravity_pass_123")
    
    # Делаем sync, чтобы загрузить список комнат
    print("Syncing...")
    resp = await client.sync(timeout=5000)
    
    print("\nJoined Rooms:")
    for room_id, room in client.rooms.items():
        print(f"Room ID: {room_id} | Name: {room.name} | Display Name: {room.display_name}")
        
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
