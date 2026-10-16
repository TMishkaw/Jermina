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
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }
        .container { max-width: 900px; margin: 0 auto; background: #1e293b; padding: 2rem; border-radius: 12px; border: 1px solid #334155; }
        h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 0.5rem; }
        h2 { color: #818cf8; margin-top: 1.5rem; }
        .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.8rem; background: #0284c7; color: white; margin-right: 0.5rem; }
        pre { background: #0b0f19; padding: 1rem; border-radius: 8px; overflow-x: auto; color: #a5f3fc; }
        ul { line-height: 1.7; }
        a { color: #38bdf8; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 Jemini Architecture & Wiki Portal</h1>
        <p><span class="badge">dev</span> <span class="badge">v0.1.0</span> <span class="badge">PostgreSQL + pgvector</span> <span class="badge">Gemini 3.8 Live</span></p>
        
        <h2>1. Дворівнева ізоляція (Git Flow)</h2>
        <ul>
            <li><strong>jemini-core:</strong> Гілка <code>dev</code> (активна розробка), середовище <code>Antigravity</code> (тестування, фіксація Issues), гілка <code>main/release</code> (стабільна продакшен-версія).</li>
            <li><strong>Контент-проєкти:</strong> Автономні канали, що підключають <code>jemini</code> як версіоновану залежність без прямих правок у коді бібліотеки.</li>
        </ul>

        <h2>2. П'ять базових модулів</h2>
        <ul>
            <li><strong>Модуль 1 (Brain & Context):</strong> Тришарова ієрархія (Core Invariants &rarr; Domain Knowledge &rarr; Channel Specific).</li>
            <li><strong>Модуль 2 (Rotator & Quotas):</strong> Пул API-ключів, автоматична обробка 429 та Hot Standby без розриву з'єднань.</li>
            <li><strong>Модуль 3 (Multimodal & Voice):</strong> Live API 3.8 WebSocket (24kHz PCM), Golden Acting Standard (Zephyr, Aoede, Fenrir, Kore).</li>
            <li><strong>Модуль 4 (Publisher):</strong> Таргетована публікація на YouTube (Shorts + Video) та TikTok.</li>
            <li><strong>Модуль 5 (Analytics & Evolution):</strong> Метрики залученості, контрольовані експерименти та ескалація PR/Issues.</li>
        </ul>

        <h2>3. Посилання та API</h2>
        <ul>
            <li><a href="/docs">Інтерактивна OpenAPI документація (Swagger UI)</a></li>
            <li><a href="/redoc">ReDoc документація</a></li>
            <li><a href="/rotator/status">Поточний стан ротатора ключів</a></li>
        </ul>
    </div>
</body>
</html>
"""
