import asyncio
import ssl
from nio import AsyncClient

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"

async def main():
    # Отключаем проверку SSL на всякий случай
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # 1. Логинимся за antigravity
    print("Logging in as @antigravity...")
    client_anti = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await client_anti.login("antigravity_pass_123")
    
    # 2. Создаем комнату
    print("Creating room 'AI Agent Network'...")
    resp_room = await client_anti.room_create(name="AI Agent Network")
    if not hasattr(resp_room, "room_id"):
        print(f"Failed to create room: {resp_room}")
        await client_anti.close()
        return
        
    room_id = resp_room.room_id
    print(f"Room created successfully! Room ID: {room_id}")
    
    # 3. Приглашаем @hermes_my
    print("Inviting @hermes_my to the room...")
    resp_invite = await client_anti.room_invite(room_id, "@hermes_my:artem-vpn-server.duckdns.org")
    print(f"Invite response: {resp_invite}")
    await client_anti.close()
    
    # 4. Логинимся за hermes_my и принимаем приглашение
    print("Logging in as @hermes_my...")
    client_hermes = AsyncClient(HOMESERVER, "@hermes_my:artem-vpn-server.duckdns.org")
    await client_hermes.login("hermes_pass_123")
    
    print("Joining the room...")
    resp_join = await client_hermes.room_join(room_id)
    print(f"Join response: {resp_join}")
    await client_hermes.close()
    
    print("\nInitialization complete!")
    print(f"Use this Room ID in your configuration: {room_id}")

if __name__ == "__main__":
    asyncio.run(main())
