with open("/etc/conduit/conduit.toml", "r") as f:
    content = f.read()

lines = content.splitlines()
lines = [l for l in lines if "registration_shared_secret" not in l]
lines.append('registration_shared_secret = "amn_shared_secret_key_2026"')

with open("/etc/conduit/conduit.toml", "w") as f:
    f.write("\n".join(lines) + "\n")
print("conduit.toml fixed successfully.")
