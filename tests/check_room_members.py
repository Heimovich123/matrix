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
    
    # Синхронизируемся, чтобы получить актуальные данные о комнатах
    print("Syncing with homeserver...")
    await client.sync(timeout=5000)
    
    print(f"\nChecking members of room: {ROOM_ID}")
    room = client.rooms.get(ROOM_ID)
    if not room:
        print("Error: Room not found in client state.")
        await client.close()
        return
        
    print(f"Room Name: {room.name}")
    print("\nMembers:")
    for user_id in room.users.keys():
        print(f" - {user_id}")
        
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
