# Стандарти розробки та контрибуції в Jemini (Contributing Guide)

Ласкаво просимо до розробки екосистеми **Jemini** — автономної студії відеовиробництва на базі мультимодальних моделей Google Gemini!

Цей документ визначає стандарти Git Flow, таксономію GitHub Issues, протокол розслідування дефектів (RCA) та критерії готовності коду (Definition of Done). Дотримання цих правил є **суворо обов'язковим** як для розробників, так і для автономних AI-агентів.

---

## 1. Git Flow та керування гілками

Робота над проєктом ведеться за трирівневою моделлю Git Flow:

```text
feature / bugfix / hypothesis (робоча гілка)
            ↓  (Pull Request за шаблоном)
           dev (основна гілка інтеграції та розробки)
            ↓  (Release Candidate)
           test (контур тестування та валідації QA)
            ↓  (Final Tagged Release)
           main (стабільні релізи)
```

### 1.1 Правила найменування робочих гілок
Кожна гілка створюється від актуальної `dev` і прив'язується до відповідного GitHub Issue:
- `feat/issue-<ID>-<slug>` — для нових модулів чи розширення функціоналу (наприклад: `feat/issue-14-tiktok-uploader`).
- `fix/issue-<ID>-<slug>` — для виправлення дефектів за протоколом RCA (наприклад: `fix/issue-21-operator-url-mismatch`).
- `hypothesis/issue-<ID>-<slug>` — для автономних креативних експериментів AI-агентів (наприклад: `hypothesis/issue-33-cyber-matrix-hook`).
- `chore/issue-<ID>-<slug>` — для рефакторингу, оновлення залежностей чи тестів (наприклад: `chore/issue-09-ruff-update`).

> [!WARNING]
> **Прямий пуш у `main`, `release` або `test` заборонено.** Будь-які зміни інтегруються виключно через Pull Request у гілку `dev`.

---

## 2. Стандарт комітів (Conventional Commits)

Повідомлення комітів мають чітко слідувати специфікації [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <опис дій у наказовому способі>
```

- **Типи (`type`):**
  - `feat`: новий функціонал, сервіс, компонент чи команда CLI.
  - `fix`: виправлення дефекту (супроводжується юніт-тестом).
  - `perf`: оптимізація продуктивності рендеру або споживання пам'яті/квот.
  - `refactor`: реорганізація коду без зміни публічного API.
  - `test`: додавання або оновлення тестового сьюту.
  - `chore`: оновлення залежностей, конфігурації або допоміжних скриптів.
  - `docs`: оновлення документації, матриць або скілів.
- **Область (`scope`):** `core`, `rotator`, `voice`, `remotion`, `database`, `publishing`, `analytics`, `scheduling`, `operator`, `cli`.

*Приклади валідних комітів:*
- `feat(remotion): mount Forma 2-B HUD vector blueprint schematic`
- `fix(publishing): resolve shorts_url attribute mismatch in OperatorReviewService`
- `chore(labels): add standardized GitHub issue labels automation`

---

## 3. Протокол розслідування дефектів (Root-Cause First Protocol)

У системі діє політика **Zero Quick-Fix**: суворо заборонено «глушити» помилки пустими `try-except pass` або додавати локальні перевірки, які маскують архітектурні дефекти.

Кожен дефект розслідується за 4 обов'язковими кроками:
1. **Крок 1 (RCA - Root Cause Analysis):** З'ясувати, чому базова схема Pydantic, типізація або архітектурний контракт дозволили появу некоректного стану.
2. **Крок 2 (Systemic Fix):** Посилити архітектурний контракт (звузити типи, додати валідатор, змінити інтерфейс базового класу або таблиці БД).
3. **Крок 3 (Defect Fix):** Точково усунути локальний дефект у коді реалізації.
4. **Крок 4 (Regression Lock):** Написати ізольований юніт-тест у `tests/`, який надійно фіксує сценарій збою і запобігає повторенню дефекту.

---

## 4. Таксономія GitHub Issues та форми (.github/ISSUE_TEMPLATE)

Для створення завдань використовуються інтерактивні форми GitHub Issue Forms (`.yml`):

| Шаблон | Назва | Для кого / Призначення |
| :--- | :--- | :--- |
| [`01_defect_rca.yml`](.github/ISSUE_TEMPLATE/01_defect_rca.yml) | **RCA Defect** | Звіт про помилку з обов'язковими полями симптомів, логів, RCA-аналізу та назви регресійного тесту. |
| [`02_core_feature.yml`](.github/ISSUE_TEMPLATE/02_core_feature.yml) | **Core Feature** | Запит на розробку нової функціональності ядра, пайплайну чи сервісу. |
| [`03_agent_hypothesis.yml`](.github/ISSUE_TEMPLATE/03_agent_hypothesis.yml) | **Agent Hypothesis** | Креативна гіпотеза саморозвитку від Trend Scout або Feedback Loop (Спостереження $\rightarrow$ Гіпотеза $\rightarrow$ Експеримент $\rightarrow$ Метрика). |
| [`04_channel_onboarding.yml`](.github/ISSUE_TEMPLATE/04_channel_onboarding.yml) | **Channel Onboarding** | Реєстрація нового каналу (ніша, колір Remotion, голосовий архетип Gemini 3.8 Live). |
| [`05_task_chore.yml`](.github/ISSUE_TEMPLATE/05_task_chore.yml) | **Task / Chore** | Технічний борг, рефакторинг, оновлення залежностей або інфраструктури. |

---

## 5. Система міток (GitHub Labels Taxonomy)

Мітки структуровані за 5 ключовими префіксами для зручної фільтрації та пошуку:

### 5.1 Типи (`type:*`)
- `type:defect-rca` (`#d73a4a`) — Дефект з обов'язковим RCA протоколом.
- `type:core-feature` (`#a2eeef`) — Новий функціонал ядра або сервісу.
- `type:agent-hypothesis` (`#7057ff`) — Автономна гіпотеза розвитку від AI-агента.
- `type:channel-onboard` (`#0075ca`) — Реєстрація нового каналу контенту.
- `type:chore` (`#cfd3d7`) — Технічний борг або рефакторинг.

### 5.2 Компоненти (`comp:*`)
- `comp:core` (`#1d76db`) — Ядро системи, контекстний рушій, моделі.
- `comp:rotator` (`#f9d0c4`) — Key Rotator та обробка 429 Hot Standby.
- `comp:voice-live` (`#b60205`) — Gemini 3.8 Live API WebSocket синтез мовлення.
- `comp:remotion` (`#008672`) — Remotion 9:16 відео, HUD, Stickman Rig, VFX.
- `comp:database` (`#5319e7`) — PostgreSQL, pgvector, пам'ять та міграції.
- `comp:publishing` (`#e99695`) — YouTube Shorts Publisher, інтеграція соцмереж.
- `comp:analytics` (`#0e8a16`) — Retention Feedback Loop та контур самонавчання.
- `comp:scheduling` (`#fbca04`) — Trend Scout та персистентна черга завдань.
- `comp:operator` (`#c2e0c6`) — Пульт модерації оператора (Human-in-the-Loop).
- `comp:cli` (`#d4c5f9`) — CLI інтерфейс, аргументи, E2E раннер.

### 5.3 Канали (`channel:*`)
- `channel:stickman_lab` (`#00f0ff`) — Канал Stickman Lab (акцент `#00F0FF`, голос `Zephyr`).
- `channel:cyber_matrix` (`#00ff66`) — Канал Cyber Matrix (акцент `#00FF66`, голос `Fenrir`).
- `channel:crypto_pulse` (`#ffb800`) — Канал Crypto Pulse (акцент `#FFB800`, голос `Aoede`).
- `channel:science_genesis` (`#9d00ff`) — Канал Science Genesis (акцент `#9D00FF`, голос `Kore`).
- `channel:global` (`#ffffff`) — Загальний рівень для всієї екосистеми.

### 5.4 Пріоритети (`priority:*`)
- `priority:blocker-p0` (`#b60205`) — P0 Блокер: повна зупинка генерації або витік ресурсів.
- `priority:high-p1` (`#d93f0b`) — P1 Високий: порушує роботу важливого каналу чи сцени.
- `priority:medium-p2` (`#fbca04`) — P2 Середній: штатний пріоритет функціоналу.
- `priority:low-p3` (`#0e8a16`) — P3 Низький: другорядне завдання або оптимізація.

### 5.5 Джерела / Авторство (`origin:*`)
- `origin:human` (`#5319e7`) — Створено людиною-розробником або оператором.
- `origin:agent-scout` (`#1d76db`) — Створено автономним Trend Scout.
- `origin:agent-retention` (`#0052cc`) — Створено контуром Feedback Loop.
- `origin:virtual-art-director` (`#6f42c1`) — Створено мультимодальним валідатором якості.

> [!TIP]
> Для синхронізації всіх міток у репозиторії запустіть скрипт:
> ```powershell
> .\.venv\Scripts\python.exe scripts/setup_github_labels.py
> ```

---

## 6. Definition of Done (DoD) для Pull Request

Перед злиттям будь-якого Pull Request у гілку `dev` перевірте чекліст:
1. [ ] **Коректна прив'язка:** У PR вказано `Closes #<ID>` на відкрите Issue.
2. [ ] **RCA перевірка (для фіксів):** Заповнено всі 4 пункти протоколу RCA.
3. [ ] **100% тест-сьют:** Усі юніт-тести проходять успішно:
   ```powershell
   .\.venv\Scripts\pytest.exe tests/ -v
   ```
4. [ ] **Лінтер без помилок:** Статичний аналіз коду повертає код 0:
   ```powershell
   .\.venv\Scripts\ruff.exe check src/ tests/ scripts/
   ```
5. [ ] **Zero Secret Leaks:** Жодних ключів API, токенів чи `config/client_secret.json` у змінах.
6. [ ] **Modern Gemini API SDK:** Використання виключно `from google import genai` (заборонено застарілі `google-generativeai` та моделі `gemini-1.5-*`).
7. [ ] **Remotion build (якщо зачіпалися React/VFX компоненти):**
   ```powershell
   cd remotion; npm run build; cd ..
   ```
