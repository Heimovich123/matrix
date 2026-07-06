import asyncio
import ssl
import os
from nio import AsyncClient, RoomMessageText

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"
ADMIN_USER = "@antigravity:artem-vpn-server.duckdns.org"
ADMIN_PASS = "antigravity_pass_123"

async def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    client = AsyncClient(HOMESERVER, ADMIN_USER)
    try:
        await client.login(ADMIN_PASS)
    except Exception as e:
        print(f"Error: Login failed: {e}")
        return

    # Загружаем ID последнего обработанного события
    last_event_path = "last_event.txt"
    last_event_id = ""
    if os.path.exists(last_event_path):
        try:
            with open(last_event_path, "r") as f:
                last_event_id = f.read().strip()
        except Exception:
            pass

    # Получаем последние сообщения
    resp_msg = await client.room_messages(ROOM_ID, limit=10)
    await client.close()

    if not hasattr(resp_msg, "chunk"):
        print("Error: No messages found.")
        return

    # Ищем самую свежую необработанную команду
    for event in resp_msg.chunk:
        if isinstance(event, RoomMessageText):
            # Проверяем, что сообщение адресовано нам, содержит [CMD] и отправлено не нами
            if (
                "@antigravity" in event.body 
                and "[CMD]" in event.body 
                and event.sender != ADMIN_USER
                and event.event_id != last_event_id
            ):
                print(f"Found new task from {event.sender}: {event.body}")
                
                # Записываем задачу в файл
                with open("task.txt", "w", encoding="utf-8") as f:
                    f.write(event.body)
                    
                # Сохраняем event_id как обработанный
                with open(last_event_path, "w") as f:
                    f.write(event.event_id)
                    
                print("Task saved to task.txt successfully.")
                return

    print("No new tasks found in Matrix.")

if __name__ == "__main__":
    asyncio.run(main())
