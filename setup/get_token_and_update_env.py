import urllib.request
import json
import ssl

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
USERNAME = "agentadcc49"
PASSWORD = "HrpyIdAbzFiMe1Q0"

def get_token():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"{HOMESERVER}/_matrix/client/v3/login"
    payload = {
        "type": "m.login.password",
        "identifier": {"type": "m.id.user", "user": USERNAME},
        "password": PASSWORD
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
            token = res.get("access_token")
            user_id = res.get("user_id")
            print(f"SUCCESS: Token retrieved for {user_id}")
            print(f"TOKEN: {token}")
            
            # Обновляем .env
            env_path = "/root/.hermes/.env"
            with open(env_path, "r") as f:
                content = f.read()
                
            lines = content.splitlines()
            lines = [l for l in lines if "MATRIX_ACCESS_TOKEN" not in l]
            lines.append(f"MATRIX_ACCESS_TOKEN={token}")
            
            with open(env_path, "w") as f:
                f.write("\n".join(lines) + "\n")
                
            print("Updated .env with MATRIX_ACCESS_TOKEN.")
    except Exception as e:
        if hasattr(e, "read"):
            print(f"Login failed: {e.read().decode()}")
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    get_token()
