"""Autonomous built-in Wiki Knowledge Base for Jemini."""

class WikiEngine:
    """Renders interactive documentation and architectural blueprints."""

    def render_html(self) -> str:
        return """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Jemini Autonomous Wiki & Knowledge Base</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b1120; color: #f8fafc; margin: 0; padding: 2rem; }
        .container { max-width: 960px; margin: 0 auto; background: #1e293b; padding: 2.5rem; border-radius: 14px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 0.5rem; }
        h2 { color: #818cf8; margin-top: 1.8rem; }
        h3 { color: #34d399; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; background: #0284c7; color: white; margin-right: 0.5rem; font-weight: 600; }
        .badge-green { background: #059669; }
        .badge-purple { background: #7c3aed; }
        pre { background: #020617; padding: 1rem; border-radius: 8px; overflow-x: auto; color: #a5f3fc; border: 1px solid #1e293b; }
        ul { line-height: 1.8; }
        a { color: #38bdf8; text-decoration: none; font-weight: 500; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 Jemini Architecture & Wiki Portal</h1>
        <p>
            <span class="badge">dev</span>
            <span class="badge badge-green">v0.2.0</span>
            <span class="badge badge-purple">Gemini 3.8 Live</span>
            <span class="badge">PostgreSQL + pgvector</span>
        </p>
        
        <h2>1. Підсистема 1: Key Rotator & Quota Manager</h2>
        <ul>
            <li><strong>Пріоритет Free-Tier:</strong> Система завжди спочатку вичерпує безкоштовні квоти. Платні ключі (Paid) підключаються лише як резерв або для критичних важких завдань.</li>
            <li><strong>Model-Specific Cooldown:</strong> Помилка 429 блокує виключно пару [ключ + модель]. Якщо ключ вичерпав ліміт важкої моделі, він залишається доступним для легких моделей.</li>
            <li><strong>Hot Standby:</strong> Миттєве безшовне перемикання на резервний ключ при отриманні 429 без обриву стримів чи завдань.</li>
        </ul>

        <h2>2. Підсистема 2: Універсальний Gemini Live API Engine</h2>
        <ul>
            <li><strong>Сценарій А (Video Intelligence):</strong> Мультимодальний аналіз фреймів та аудіо з генерацією структурованого JSON-звіту (хук, темп, акторські стандарти).</li>
            <li><strong>Сценарій Б (Live Stream Vision):</strong> Візуальний парсер прямих трансляцій (TikTok/YouTube) — детекція подарунків, коментарів, лайків, дій глядачів для майбутніх батлів.</li>
            <li><strong>Сценарій В (AI Voice TTS):</strong> Акторське втілення мовлення (Zephyr, Aoede, Fenrir, Kore) за еталонним Golden Acting Standard (vocal fry, живий сміх, шепіт).</li>
        </ul>

        <h2>3. Global Quality Gates & Engineering Standards</h2>
        <ul>
            <li><strong>Сувора типізація:</strong> Повна статична типізація для всіх моделей та функцій.</li>
            <li><strong>Піраміда тестування:</strong> 100% покриття критичних шляхів (Unit + Integration + Fault Injection для симуляції 429).</li>
            <li><strong>Graceful Degradation:</strong> Збій другорядного модуля не зупиняє основний конвеєр.</li>
            <li><strong>Векторна пам'ять (pgvector):</strong> Накопичення досвіду експериментів, помилок парсингу та патернів успішних сценаріїв.</li>
        </ul>

        <h2>4. Model Context Protocol (MCP) Інтеграція</h2>
        <ul>
            <li><strong>Воркспейс-конфіг:</strong> <code>.agents/mcp_config.json</code> для нативних AI-інструментів.</li>
            <li><strong>postgres-jemini:</strong> Пряма інспекція бази даних PostgreSQL та таблиць пам'яті агентів без ручного введення запитів.</li>
            <li><strong>github:</strong> Автономне відкриття GitHub Issues для багів та генерація Pull Requests.</li>
        </ul>

        <h2>5. Можливості платформи Antigravity</h2>
        <ul>
            <li><strong>Scheduled Tasks:</strong> Періодичне виконання фонових завдань за розкладом на базі Gemini 3.8 Flash.</li>
            <li><strong>JSON Hooks:</strong> Перехоплення життєвого циклу агента (pre-tool, post-response, loop stop) через локальні shell-скрипти.</li>
            <li><strong>Voice Transcription:</strong> Живе введення та очищення голосових промтів через <code>Ctrl + M</code>.</li>
            <li><strong>Remote Control & VCS:</strong> Мобільний контроль агентів через браузер та Git-нативна панель дифу/комітів.</li>
        </ul>

        <h2>6. Кастомні субагенти (.agents/agents)</h2>
        <ul>
            <li><strong>Ізоляція Worktree:</strong> Режим <code>branch</code> дозволяє субагентам працювати у фонових Git worktrees.</li>
            <li><strong>Формат .md з YAML:</strong> Декларативне визначення інструментів, моделі та політики виконання.</li>
            <li><strong>video-evaluator:</strong> Вбудований субагент аудиту контенту та дотримання Golden Acting Standard.</li>
        </ul>

        <h2>7. Інтерактивні посилання</h2>
        <ul>
            <li><a href="/docs">Інтерактивна OpenAPI документація (Swagger UI)</a></li>
            <li><a href="/redoc">ReDoc документація</a></li>
            <li><a href="/rotator/status">Поточний стан ротатора ключів</a></li>
        </ul>
    </div>
</body>
</html>
"""
