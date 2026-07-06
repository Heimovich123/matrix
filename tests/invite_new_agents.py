import asyncio
import ssl
from nio import AsyncClient

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"
AGENTS = [
    "@agentfbacc5:artem-vpn-server.duckdns.org",
    "@agent64d54d:artem-vpn-server.duckdns.org"
]

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print("Logging in as @antigravity...")
    admin_client = AsyncClient(HOMESERVER, "@antigravity:artem-vpn-server.duckdns.org")
    await admin_client.login("antigravity_pass_123")
    
    for agent in AGENTS:
        print(f"Inviting {agent} to room...")
        resp_invite = await admin_client.room_invite(ROOM_ID, agent)
        print(f"Invite Response for {agent}: {resp_invite}")
        
    await admin_client.close()

if __name__ == "__main__":
    asyncio.run(main())
