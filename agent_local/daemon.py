import asyncio
import ssl
import sys
import os
import codecs
from nio import AsyncClient, RoomMessageText, SyncResponse

# Добавляем корневую папку в пути поиска модулей для импорта core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.protocol import AMNMessage

# Принудительно устанавливаем UTF-8 для консоли в Windows
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

HOMESERVER = "https://artem-vpn-server.duckdns.org:8448"
ROOM_ID = "!ztbXcKlttep3u-R9C11c1pTeCmID6T5M2jF9Vov5yrg"
ADMIN_USER = "@antigravity:artem-vpn-server.duckdns.org"
ADMIN_PASS = "antigravity_pass_123"

class AMNLocalDaemon:
    def __init__(self):
        self.client = None
        self.last_event_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "last_event.txt"
        )
        self.task_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "task.txt"
        )
        self.last_event_id = self.load_last_event()

    def load_last_event(self) -> str:
        if os.path.exists(self.last_event_path):
            try:
                with open(self.last_event_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception as e:
                print(f"[DAEMON] Не удалось прочитать last_event.txt: {e}")
        return ""

    def save_last_event(self, event_id: str):
        self.last_event_id = event_id
        try:
            with open(self.last_event_path, "w", encoding="utf-8") as f:
                f.write(event_id)
        except Exception as e:
            print(f"[DAEMON] Не удалось записать last_event.txt: {e}")

    async def send_matrix_message(self, body: str):
        """Отправка сообщения в комнату"""
        if self.client:
            try:
                await self.client.room_send(
                    room_id=ROOM_ID,
                    message_type="m.room.message",
                    content={"msgtype": "m.text", "body": body}
                )
            except Exception as e:
                print(f"[DAEMON] Ошибка отправки сообщения: {e}")

    async def on_message(self, room, event):
        """Callback-обработчик входящих сообщений"""
        if not isinstance(event, RoomMessageText):
            return

        # Игнорируем собственные сообщения
        if event.sender == ADMIN_USER:
            return

        # Игнорируем уже обработанные события
        if event.event_id == self.last_event_id:
            return

        # Парсим входящее сообщение по протоколу AMN
        msg = AMNMessage.parse(event.body, event.sender)

        # Обработка задач (тип 'task' или обычный текст с упоминанием @antigravity)
        is_targeted = False
        if msg.type == AMNMessage.TYPE_TASK and (msg.recipient == ADMIN_USER or msg.recipient == "@antigravity"):
            is_targeted = True
        elif msg.type == AMNMessage.TYPE_CHAT and "@antigravity" in msg.content:
            is_targeted = True

        if is_targeted:
            print(f"\n[DAEMON] Найдена новая задача от {event.sender} (ID: {event.event_id})")
            
            # Сохраняем event_id как обработанный
            self.save_last_event(event.event_id)

            # Отправляем подтверждение о начале работы
            reply_body = f"🚀 [AMN] Antigravity на домашнем ПК принял задачу в работу! ID: {event.event_id[:8]}"
            await self.send_matrix_message(reply_body)

            # Записываем задачу в файл task.txt для локального ИИ-агента
            task_content = msg.content if msg.type == AMNMessage.TYPE_CHAT else f"[CMD] {msg.action}: {msg.params}"
            try:
                with open(self.task_path, "w", encoding="utf-8") as f:
                    f.write(f"SENDER: {event.sender}\nEVENT_ID: {event.event_id}\nCONTENT: {task_content}")
                print(f"[DAEMON] Задача успешно записана в {self.task_path}")
            except Exception as e:
                print(f"[DAEMON] Ошибка записи файла задачи: {e}")

    async def start(self):
        print("[DAEMON] Запуск фонового демона AMN...")
        
        # Настройка SSL Bypass для локального тестирования
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        self.client = AsyncClient(HOMESERVER, ADMIN_USER, ssl=ctx)
        self.client.add_event_callback(self.on_message, RoomMessageText)

        try:
            print(f"[DAEMON] Авторизация на сервере {HOMESERVER}...")
            await self.client.login(ADMIN_PASS)
            print("[DAEMON] Успешная авторизация. Запуск прослушивания комнаты...")
            
            # Начинаем бесконечную синхронизацию событий (long-polling)
            await self.client.sync_forever(timeout=30000)
        except asyncio.CancelledError:
            print("[DAEMON] Демон остановлен.")
        except Exception as e:
            print(f"[DAEMON] Критическая ошибка в работе демона: {e}")
        finally:
            if self.client:
                await self.client.close()

if __name__ == "__main__":
    daemon = AMNLocalDaemon()
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        print("\n[DAEMON] Завершение работы по сигналу Ctrl+C.")
