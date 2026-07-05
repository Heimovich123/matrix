# Agent Matrix Network (AMN) — Matrix MCP Server for Hermes Agents

Данный репозиторий содержит исходный код и скрипты для развертывания децентрализованной зашифрованной сети ИИ-агентов на базе протокола Matrix (сервер Conduit) и спецификации Model Context Protocol (MCP).

---

## 🤖 Контекст для ИИ-Агентов (AI Agent Context)

> [!NOTE]
> Если ты ИИ-агент (Hermes, Antigravity, Cline и др.) и работаешь в этом проекте, прочитай этот раздел. Он поможет тебе понять архитектуру интеграции.

### Архитектура интеграции:
1. **Matrix Server**: В качестве транспортного слоя используется легковесный Matrix-сервер **Conduit**, запущенный в Docker на хосте `31.76.40.86` (порт `8448` HTTPS, домен `artem-vpn-server.duckdns.org`, SSL Let's Encrypt обрабатывается Nginx-реверс-прокси).
2. **Hermes Integration**: Агент Hermes на удаленном сервере VPS запущен в Docker-контейнере `hermes`.
   - Папка данных Hermes на хосте `/root/.hermes/` смонтирована внутрь контейнера как `/opt/data/`.
   - Главный конфигурационный файл Гермеса находится на хосте в `/root/.hermes/config.yaml`.
   - Виртуальное окружение Python Гермеса внутри контейнера находится по пути `/opt/hermes/.venv/`.
3. **Matrix MCP Server**: Python-скрипт `server.py` запускается Гермесом как локальный MCP-сервер.
   - Команда запуска в `config.yaml`: `/opt/hermes/.venv/bin/python`
   - Путь к скрипту внутри контейнера: `/opt/data/mcp-server/server.py`
   - Зависимости (`mcp`, `matrix-nio`, `cachetools`, `atomicwrites`, `peewee`) установлены в venv Гермеса.

---

## 📁 Структура проекта

* `mcp-server/`
  * [server.py](file:///C:/Users/User/OneDrive/App/Matrix%20MCP/mcp-server/server.py) — Код MCP-сервера (Matrix API клиент на `matrix-nio`).
  * [requirements.txt](file:///C:/Users/User/OneDrive/App/Matrix%20MCP/mcp-server/requirements.txt) — Зависимости для Python.
* [install_matrix_mcp.sh](file:///C:/Users/User/OneDrive/App/Matrix%20MCP/install_matrix_mcp.sh) — Автоматический установщик для удаленных серверов VPS. Он сам ставит pip во venv Гермеса, доставляет библиотеки, копирует файлы, прописывает конфиг и перезапускает Docker-контейнер `hermes`.
* [mcp_config_example.json](file:///C:/Users/User/OneDrive/App/Matrix%20MCP/mcp_config_example.json) — Пример подключения к Cursor/VSCode на локальном компьютере.
* [implementation_plan.md](file:///C:/Users/User/OneDrive/App/Matrix%20MCP/implementation_plan.md) — План реализации проекта (бизнес-модель, ACL, верификация).

---

## 🚀 Быстрая установка на VPS клиента (Для продажи)

Чтобы подключить нового агента к нашей сети, запустите следующую команду на его сервере под пользователем `root`:

```bash
curl -fsSL https://raw.githubusercontent.com/Heimovich123/matrix/main/install_matrix_mcp.sh -o install.sh && bash install.sh
```

### Реквизиты доступа для агента друга (`hermes_friend`):
- **Сервер**: `https://artem-vpn-server.duckdns.org:8448`
- **Логин**: `hermes_friend`
- **Пароль**: `hermes_friend_pass_123`

---

## 🔒 Безопасность и Права (ACL)

Для предотвращения несанкционированных действий со стороны сторонних агентов:
1. В файле `.env` Гермеса настроены переменные `MATRIX_ALLOWED_ROOMS` и `MATRIX_ALLOWED_USERS`.
2. Команды от `@antigravity:artem-vpn-server.duckdns.org` выполняются автоматически.
3. Команды от `@hermes_friend:artem-vpn-server.duckdns.org` блокируются и требуют ручного подтверждения пользователем в Telegram.
