import urllib.request
import json
import ssl

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"

def raw_join():
    # Отключаем проверку SSL
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # 1. Логинимся за @hermes_my, чтобы получить access_token
    login_url = f"{HOMESERVER}/_matrix/client/v3/login"
    login_data = {
        "type": "m.login.password",
        "identifier": {
            "type": "m.id.user",
            "user": "hermes_my"
        },
        "password": "hermes_pass_123"
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(login_url, data=json.dumps(login_data).encode(), headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            login_res = json.loads(resp.read().decode())
            token = login_res["access_token"]
            print("Logged in successfully! Token acquired.")
    except Exception as e:
        print(f"Login failed: {e}")
        return
        
    # 2. Делаем POST-запрос на вход в комнату с пустым JSON-телом {}
    join_url = f"{HOMESERVER}/_matrix/client/v3/join/{ROOM_ID}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    # Отправляем пустой JSON {}
    join_data = {}
    req_join = urllib.request.Request(join_url, data=json.dumps(join_data).encode(), headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req_join, context=ctx) as resp_join:
            res = json.loads(resp_join.read().decode())
            print(f"Successfully joined room! Response: {res}")
    except Exception as e:
        print(f"Join failed: {e}")

if __name__ == "__main__":
    raw_join()
