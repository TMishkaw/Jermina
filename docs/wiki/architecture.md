# Архітектурна специфікація бібліотеки Jemini

## 1. Загальна концепція та мета
**Jemini** — це незалежна, модульна Python-бібліотека з відкритим кодом (GitHub репозиторій `TMishkaw/Jermina`), призначена для повного циклу автоматизованого створення контенту, публікації, аналізу ефективності та саморозвитку контент-каналів на базі Gemini API.

## 2. Архітектура середовищ (Git Flow)
- **Контур ядра бібліотеки (`jemini-core`):**
  - `dev`: гілка активної розробки функцій та багфіксів.
  - `Antigravity`: тестовий псевдореальний контур. Тестувальники фіксують зауваження через GitHub Issues.
  - `main` / `release`: стабільна продакшен-ревізія бібліотеки.
- **Контур контент-проєктів (Каналів):**
  - Ізольовані середовища з автономією в межах сценаріїв та налаштувань.

## 3. Модулі ядра
1. **Core Engine & Context Layers (`jemini.core`)**: Core Invariants &rarr; Domain Knowledge &rarr; Channel Specific.
2. **API Key Rotator (`jemini.rotator`)**: Пул ключів, перехоплення 429, Hot Standby.
3. **Multimodal Analyzer & Synthesis (`jemini.multimodal`)**: Gemini 3.8 Live API WebSocket, Golden Acting Standard.
4. **Publisher (`jemini.publisher`)**: YouTube Shorts/Video та TikTok.
5. **Analytics & Evolution (`jemini.analytics`)**: Метрики, контрольовані експерименти, генерація Issue/PR.
6. **Storage & REST API (`jemini.storage`, `jemini.api`, `jemini.wiki`)**: PostgreSQL + pgvector, FastAPI, OpenAPI Swagger, вбудована Wiki.
