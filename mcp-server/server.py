import os
import asyncio
import sys
from mcp.server.fastmcp import FastMCP
from nio import AsyncClient, RoomMessageText

# Создаем экземпляр FastMCP
mcp = FastMCP("matrix-network")

# Получаем настройки из переменных окружения
MATRIX_HOMESERVER = os.getenv("MATRIX_HOMESERVER", "https://artem-vpn-server.duckdns.org:8448")
MATRIX_USERNAME = os.getenv("MATRIX_USERNAME") # Например, antigravity
MATRIX_PASSWORD = os.getenv("MATRIX_PASSWORD") # Например, antigravity_pass_123

async def get_client():
    """Инициализация и логин клиента Matrix."""
    if not MATRIX_USERNAME or not MATRIX_PASSWORD:
        raise ValueError("MATRIX_USERNAME and MATRIX_PASSWORD environment variables must be set")
    
    # Корректируем имя пользователя до полного Matrix ID, если нужно
    username = MATRIX_USERNAME
    if not username.startswith("@"):
        # Извлекаем домен из homeserver
        domain = MATRIX_HOMESERVER.replace("https://", "").replace("http://", "").split(":")[0]
        username = f"@{username}:{domain}"
        
    client = AsyncClient(MATRIX_HOMESERVER, username)
    await client.login(MATRIX_PASSWORD)
    return client

@mcp.tool()
async def send_matrix_message(room_id: str, message: str) -> str:
    """
    Отправить текстовое сообщение в указанную комнату Matrix.
    """
    try:
        client = await get_client()
        resp = await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )
        await client.close()
        if hasattr(resp, "event_id"):
            return f"Success: Message sent. Event ID: {resp.event_id}"
        else:
            return f"Error: {resp}"
    except Exception as e:
        return f"Exception: {e}"

@mcp.tool()
async def read_matrix_messages(room_id: str, limit: int = 10) -> str:
    """
    Прочитать последние сообщения из указанной комнаты Matrix.
    Возвращает список сообщений в формате 'Автор: Текст'.
    """
    try:
        client = await get_client()
        # Запрашиваем сообщения из комнаты
        resp = await client.room_messages(room_id, limit=limit)
        await client.close()
        
        if hasattr(resp, "chunk"):
            messages = []
            # Сообщения возвращаются от новых к старым, развернем их
            for event in reversed(resp.chunk):
                if isinstance(event, RoomMessageText):
                    messages.append(f"{event.sender}: {event.body}")
            
            if not messages:
                return "No text messages found in this room."
            return "\n".join(messages)
        else:
            return f"Error: Could not retrieve messages. {resp}"
    except Exception as e:
        return f"Exception: {e}"

@mcp.tool()
async def create_matrix_room(room_name: str) -> str:
    """
    Создать новую комнату в Matrix и вернуть её Room ID.
    """
    try:
        client = await get_client()
        resp = await client.room_create(name=room_name)
        await client.close()
        if hasattr(resp, "room_id"):
            return f"Success: Room '{room_name}' created. Room ID: {resp.room_id}"
        else:
            return f"Error: {resp}"
    except Exception as e:
        return f"Exception: {e}"

@mcp.tool()
async def invite_to_matrix_room(room_id: str, user_id: str) -> str:
    """
    Пригласить другого пользователя (или агента) в комнату Matrix по его User ID (например, @hermes_my:domain.org).
    """
    try:
        client = await get_client()
        resp = await client.room_invite(room_id, user_id)
        await client.close()
        # nio возвращает пустой объект при успехе или ошибку
        return f"Success: Invited {user_id} to room {room_id}."
    except Exception as e:
        return f"Exception: {e}"

@mcp.tool()
async def join_matrix_room(room_id: str) -> str:
    """
    Войти в комнату Matrix по её Room ID (после получения приглашения).
    """
    try:
        client = await get_client()
        resp = await client.room_join(room_id)
        await client.close()
        return f"Success: Joined room {room_id}."
    except Exception as e:
        return f"Exception: {e}"

if __name__ == "__main__":
    # Запускаем сервер MCP по стандартному протоколу ввода-вывода (stdio)
    mcp.run()
