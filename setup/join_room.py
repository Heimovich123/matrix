import asyncio
import ssl
from nio import AsyncClient

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Logging in as @hermes_my...")
    client_hermes = AsyncClient(HOMESERVER, "@hermes_my:artem-vpn-server.duckdns.org")
    await client_hermes.login("hermes_pass_123")
    
    print(f"Joining room {ROOM_ID}...")
    resp_join = await client_hermes.join(ROOM_ID)
    print(f"Join response: {resp_join}")
    await client_hermes.close()
    
    print("Joined successfully!")

if __name__ == "__main__":
    asyncio.run(main())
