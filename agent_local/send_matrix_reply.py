import asyncio
import ssl
import sys
from nio import AsyncClient

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"
ADMIN_USER = "@antigravity:artem-vpn-server.duckdns.org"
ADMIN_PASS = "antigravity_pass_123"

async def main():
    if len(sys.argv) < 2:
        print("Usage: python send_matrix_reply.py <message>")
        return
        
    msg = sys.argv[1]
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    client = AsyncClient(HOMESERVER, ADMIN_USER)
    try:
        await client.login(ADMIN_PASS)
        print(f"Sending reply: {msg}")
        await client.room_send(
            room_id=ROOM_ID,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": msg}
        )
        await client.close()
        print("Reply sent successfully.")
    except Exception as e:
        print(f"Error: {e}")
        try:
            await client.close()
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
