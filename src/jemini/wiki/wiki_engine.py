"""Autonomous built-in Wiki Knowledge Base for Jemini."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class WikiEngine:
    """Manages autonomous Wiki articles in docs/wiki/ and renders interactive portal."""

    def __init__(self, wiki_root: Path | str | None = None):
        base = (
            Path(wiki_root)
            if wiki_root
            else Path(__file__).resolve().parent.parent.parent.parent / "docs" / "wiki"
        )
        self.wiki_root = base

    def list_articles(self) -> list[dict[str, Any]]:
        """Lists metadata for all markdown articles in docs/wiki/."""
        if not self.wiki_root.exists():
            return []
        articles = []
        for f in sorted(self.wiki_root.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            first_line = content.splitlines()[0] if content.splitlines() else f.stem
            title = first_line.lstrip("#").strip() if first_line.startswith("#") else f.stem
            articles.append({
                "article_name": f.stem,
                "title": title,
                "file_path": str(f),
                "size_bytes": f.stat().st_size,
                "word_count": len(content.split()),
            })
        return articles

    def get_article(self, name: str) -> str | None:
        """Retrieves raw markdown text of a wiki article."""
        clean_name = name.removesuffix(".md").strip().lower()
        for f in self.wiki_root.glob("*.md"):
            if f.stem.lower() == clean_name:
                return f.read_text(encoding="utf-8")
        return None

    def render_html(self) -> str:
        """Renders interactive HTML portal listing all dynamic articles."""
        articles = self.list_articles()
        article_items = "\n".join(
            f'<li><a href="/wiki/articles/{a["article_name"]}"><strong>{a["title"]}</strong></a> '
            f'<span style="color:#64748b; font-size:0.85rem;">({a["article_name"]}.md &bull; {a["word_count"]} words)</span></li>'
            for a in articles
        )

        return f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Jemini Autonomous Wiki & Knowledge Base</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b1120; color: #f8fafc; margin: 0; padding: 2rem; }}
        .container {{ max-width: 960px; margin: 0 auto; background: #1e293b; padding: 2.5rem; border-radius: 14px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 0.5rem; }}
        h2 {{ color: #818cf8; margin-top: 1.8rem; }}
        h3 {{ color: #34d399; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; background: #0284c7; color: white; margin-right: 0.5rem; font-weight: 600; }}
        .badge-green {{ background: #059669; }}
        .badge-purple {{ background: #7c3aed; }}
        pre {{ background: #020617; padding: 1rem; border-radius: 8px; overflow-x: auto; color: #a5f3fc; border: 1px solid #1e293b; }}
        ul {{ line-height: 1.8; }}
        a {{ color: #38bdf8; text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}
        .articles-box {{ background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 1.5rem; margin-top: 1rem; }}
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
        
        <h2>📚 Каталог статей бази знань Wiki ({len(articles)} статей)</h2>
        <div class="articles-box">
            <ul>
                {article_items}
            </ul>
        </div>

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
            <li><strong>jemini-studio-docs:</strong> Швидкий пошук у базі знань, перегляд статей Wiki та виконання викликів REST API.</li>
            <li><strong>postgres-jemini:</strong> Пряма інспекція бази даних PostgreSQL та таблиць пам'яті агентів без ручного введення запитів.</li>
            <li><strong>github:</strong> Автономне відкриття GitHub Issues для багів та генерація Pull Requests.</li>
        </ul>

        <h2>5. Інтерактивні посилання</h2>
        <ul>
            <li><a href="/docs">Інтерактивна OpenAPI документація (Swagger UI)</a></li>
            <li><a href="/redoc">ReDoc документація</a></li>
            <li><a href="/rotator/status">Поточний стан ротатора ключів</a></li>
            <li><a href="/wiki/articles">JSON Каталог усіх статей Wiki</a></li>
        </ul>
    </div>
</body>
</html>
"""
