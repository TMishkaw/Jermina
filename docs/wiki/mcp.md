# Model Context Protocol (MCP) у Jemini & Antigravity

> **Model Context Protocol (MCP)** — це відкритий стандарт, який дозволяє AI-агентам та середовищам розробки безпечно підключатися до локальних інструментів, баз даних, файлових парсерів та зовнішніх API.

---

## 1. Що дає MCP для екосистеми Jemini

MCP виступає універсальним містком між агентами Jemini та інфраструктурою:
- **Пряма інспекція PostgreSQL**: замість ручного передавання схем агенти через MCP перевіряють актуальну структуру таблиць (`api_keys`, `agent_memories`, `live_stream_events`).
- **Автономний GitHub workflow**: автоматичне відкриття Issue під час знаходження помилок тестувальниками або детекції feature gaps, а також створення Pull Request'ів агентами саморозвитку.
- **Дотримання безпеки**: виконання інструментів контролюється політикою доступу та перевіряється перед виконанням.

---

## 2. Структура конфігурації MCP

В Antigravity налаштування розділені на два рівні:
1. **Глобальний конфіг**: `~/.gemini/config/mcp_config.json`
2. **Воркспейс-конфіг**: `.agents/mcp_config.json` (у корені проєкту)

### Приклад конфігурації `.agents/mcp_config.json`:

```json
{
  "mcpServers": {
    "postgres-jemini": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://postgres:postgres@localhost:5432/jemini"
      ]
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN"
      }
    }
  }
}
```

---

## 3. Налаштовані сервери для проєкту

| Назва сервера | Провайдер / Команда | Призначення |
| :--- | :--- | :--- |
| **`postgres-jemini`** | `npx -y @modelcontextprotocol/server-postgres` | Інспекція бази даних PostgreSQL, робота з таблицями ротатора та векторної пам'яті `pgvector`. |
| **`github`** | `npx -y @modelcontextprotocol/server-github` | Керування гілками `dev`/`main`, відкриття Issues для багів та формування PR. |

---

## 4. Керування та діагностика

- **Інтерактивна панель**: введіть `/mcp` у полі вводу Antigravity для перегляду статусу серверів, перезавантаження та інспекції логів.
- **Безпека секретів**: файл `.agents/mcp_config.json` внесено до `.gitignore`, а для репозиторію використовується безпечний шаблон `.agents/mcp_config.example.json`.
