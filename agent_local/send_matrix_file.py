import asyncio
import ssl
import os
import sys
import mimetypes
from nio import AsyncClient

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"
ADMIN_USER = "@antigravity:artem-vpn-server.duckdns.org"
ADMIN_PASS = "antigravity_pass_123"

def find_latest_text_file():
    desktops = [
        r"C:\Users\User\Desktop",
        r"C:\Users\User\OneDrive\Рабочий стол"
    ]
    latest_file = None
    latest_time = 0

    for d in desktops:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            if f.endswith((".txt", ".md")):
                filepath = os.path.join(d, f)
                if os.path.isfile(filepath):
                    mtime = os.path.getmtime(filepath)
                    if mtime > latest_time:
                        latest_time = mtime
                        latest_file = filepath
    return latest_file

async def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"ERROR: File not found: {filepath}")
            return
    else:
        filepath = find_latest_text_file()
        if not filepath:
            print("ERROR: No text or markdown files found on Desktop.")
            return

    filename = os.path.basename(filepath)
    print(f"Using file: {filename} at {filepath}")

    # Читаем файл
    try:
        with open(filepath, "rb") as f:
            file_data = f.read()
    except Exception as e:
        print(f"ERROR: Cannot read file: {e}")
        return

    # Подключение к Matrix
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    client = AsyncClient(HOMESERVER, ADMIN_USER, ssl=ctx)
    try:
        await client.login(ADMIN_PASS)
        print("Logged in successfully to Matrix.")

        # Загрузка файла на медиа-сервер Matrix
        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or "text/plain"
        
        import io
        data_stream = io.BytesIO(file_data)
        
        print(f"Uploading file {filename} ({len(file_data)} bytes) to Matrix media repository...")
        upload_resp_tuple = await client.upload(
            data_stream,
            content_type=mime_type,
            filename=filename
        )
        
        upload_resp = upload_resp_tuple[0] if isinstance(upload_resp_tuple, tuple) else upload_resp_tuple
        
        if not hasattr(upload_resp, "content_uri"):
            print(f"ERROR: Upload response invalid: {upload_resp_tuple}")
            await client.close()
            return

        print(f"File uploaded. MXC URI: {upload_resp.content_uri}")

        # Отправка m.file сообщения
        content = {
            "body": filename,
            "info": {
                "size": len(file_data),
                "mimetype": mime_type
            },
            "msgtype": "m.file",
            "url": upload_resp.content_uri
        }
        
        print("Sending file event to room...")
        await client.room_send(
            room_id=ROOM_ID,
            message_type="m.room.message",
            content=content
        )

        # Отправка текстового отчета
        report_msg = f"[AMN] [RESULT] Успешно отправлен файл '{filename}'.\nАбсолютный путь: {filepath}"
        await client.room_send(
            room_id=ROOM_ID,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": report_msg}
        )

        await client.close()
        print("Task completed successfully!")
    except Exception as e:
        print(f"ERROR: Matrix interaction failed: {e}")
        try:
            await client.close()
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
