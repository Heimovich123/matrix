import urllib.request
import json
import ssl
import hmac
import hashlib

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
SHARED_SECRET = "amn_shared_secret_key_2026"
USERNAME = "test_auto_user_1"
PASSWORD = "test_password_123"

def register():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"{HOMESERVER}/_matrix/client/v3/register"

    # Вычисляем HMAC-SHA1 без nonce
    # Формат: username + "\x00" + password + "\x00" + admin (notadmin/admin)
    admin_status = "notadmin"
    message = f"{USERNAME}\x00{PASSWORD}\x00{admin_status}"
    
    mac = hmac.new(
        SHARED_SECRET.encode(),
        message.encode(),
        hashlib.sha1
    ).hexdigest()
    
    print(f"Computed MAC (no nonce): {mac}")

    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "mac": mac,
        "admin": False
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            res = json.loads(response.read().decode())
            print(f"Success! Registered user: {res.get('user_id')}")
    except Exception as e:
        if hasattr(e, "read"):
            print(f"Registration failed: {e.read().decode()}")
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    register()
