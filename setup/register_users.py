import urllib.request
import json
import ssl

def register_user(username, password):
    url = "https://artem-vpn-server.duckdns.org:8448/_matrix/client/v3/register"
    data = {
        "auth": {
            "type": "m.login.dummy"
        },
        "username": username,
        "password": password,
        "inhibit_device_key_generation": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Отключаем проверку SSL (на всякий случай, хотя у нас Let's Encrypt)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            print(f"User {username} registered successfully! User ID: {res_data.get('user_id')}")
            return True, res_data
    except Exception as e:
        print(f"Failed to register {username}: {e}")
        return False, str(e)

# Регистрируем наших трех агентов
register_user("antigravity", "antigravity_pass_123")
register_user("hermes_my", "hermes_pass_123")
register_user("hermes_friend", "hermes_friend_pass_123")
