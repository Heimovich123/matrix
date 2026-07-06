import urllib.request
import json
import ssl

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"
USERNAME = "agentadcc49"
PASSWORD = "HrpyIdAbzFiMe1Q0"

def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"Logging in as {USERNAME} to get token...")
    login_url = f"{HOMESERVER}/_matrix/client/v3/login"
    login_data = {
        "type": "m.login.password",
        "identifier": {"type": "m.id.user", "user": USERNAME},
        "password": PASSWORD
    }
    
    req = urllib.request.Request(
        login_url, 
        data=json.dumps(login_data).encode(), 
        headers={"Content-Type": "application/json"}, 
        method='POST'
    )
    
    with urllib.request.urlopen(req, context=ctx) as resp:
        token = json.loads(resp.read().decode())["access_token"]
        
    print("Token obtained. Joining room via raw HTTP POST...")
    join_url = f"{HOMESERVER}/_matrix/client/v3/join/{ROOM_ID}"
    req_join = urllib.request.Request(
        join_url, 
        data=b"{}", 
        headers={
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {token}"
        }, 
        method='POST'
    )
    
    with urllib.request.urlopen(req_join, context=ctx) as resp_join:
        res = json.loads(resp_join.read().decode())
        print(f"Success! Joined room. Response Room ID: {res['room_id']}")

if __name__ == "__main__":
    main()
