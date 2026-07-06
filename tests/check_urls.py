import urllib.request

urls = [
    "https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh",
    "https://raw.githubusercontent.com/mhsanaei/3x-ui/main/install.sh",
    "https://raw.githubusercontent.com/MHSanaei/3x-ui/master/install.sh",
    "https://raw.githubusercontent.com/MHSanaei/3x-ui/main/install.sh"
]

for url in urls:
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req) as resp:
            print(f"{url} -> {resp.status}")
    except Exception as e:
        print(f"{url} -> Error: {e}")
