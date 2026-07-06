import pathlib
p = pathlib.Path('/opt/hermes/hermes_cli/web_server.py')
c = p.read_text()
target = '    allow_origin_regex=r"^https?://(localhost|127\\.0\\.0\\.1)(:\\d+)?$",'
replacement = '    allow_origin_regex=r"^https?://.*$",'
if target in c:
    c = c.replace(target, replacement)
    p.write_text(c)
    print("PATCH_OK")
else:
    print("TARGET_NOT_FOUND")
