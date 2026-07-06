import json
import uuid
from typing import Dict, Any, Optional

class AMNMessage:
    """
    Класс, представляющий стандартизированное сообщение в сети Agent Matrix Network (AMN).
    Поддерживает три типа сообщений: chat, task, result.
    """
    
    TYPE_CHAT = "chat"
    TYPE_TASK = "task"
    TYPE_RESULT = "result"

    def __init__(
        self,
        msg_type: str,
        sender: str,
        recipient: Optional[str] = None,
        content: Optional[str] = None,
        task_id: Optional[str] = None,
        action: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        output: Optional[str] = None
    ):
        self.type = msg_type
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.task_id = task_id or (str(uuid.uuid4()) if msg_type == self.TYPE_TASK else None)
        self.action = action
        self.params = params or {}
        self.status = status  # success / error
        self.output = output

    @classmethod
    def parse(cls, raw_text: str, sender: str) -> "AMNMessage":
        """
        Парсит сырой текст сообщения из Matrix.
        Если текст является валидным JSON определенного формата — создает структурированное сообщение.
        В противном случае интерпретирует его как обычный чат (тип 'chat').
        """
        raw_text = raw_text.strip()
        if raw_text.startswith("{") and raw_text.endswith("}"):
            try:
                data = json.loads(raw_text)
                msg_type = data.get("type")
                
                if msg_type == cls.TYPE_TASK:
                    return cls(
                        msg_type=cls.TYPE_TASK,
                        sender=sender,
                        recipient=data.get("to"),
                        task_id=data.get("id"),
                        action=data.get("action"),
                        params=data.get("params")
                    )
                elif msg_type == cls.TYPE_RESULT:
                    return cls(
                        msg_type=cls.TYPE_RESULT,
                        sender=sender,
                        task_id=data.get("task_id"),
                        status=data.get("status"),
                        output=data.get("output")
                    )
            except json.JSONDecodeError:
                pass
                
        # Fallback к обычному текстовому чату
        return cls(
            msg_type=cls.TYPE_CHAT,
            sender=sender,
            content=raw_text
        )

    def to_json(self) -> str:
        """
        Сериализует сообщение в JSON-строку для отправки в Matrix.
        """
        if self.type == self.TYPE_TASK:
            return json.dumps({
                "type": self.TYPE_TASK,
                "id": self.task_id,
                "to": self.recipient,
                "action": self.action,
                "params": self.params
            }, ensure_ascii=False)
            
        elif self.type == self.TYPE_RESULT:
            return json.dumps({
                "type": self.TYPE_RESULT,
                "task_id": self.task_id,
                "status": self.status,
                "output": self.output
            }, ensure_ascii=False)
            
        else:
            return self.content or ""

    def __repr__(self) -> str:
        return f"AMNMessage(type={self.type}, sender={self.sender}, task_id={self.task_id})"
