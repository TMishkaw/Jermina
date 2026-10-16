# YouTube Semantic Category Selection & Channel Governance

## 1. Overview
YouTube video categorization directly influences recommendations, algorithmic indexing, and audience demographic routing. The [`CategorySelector`](file:///d:/JerminaStudio/JerminaDev/src/jemini/publishing/category_selector.py) module dynamically assigns the optimal YouTube `categoryId` based on script keywords, thematic genre, title, and channel anchor profile.

---

## 2. Complete Official YouTube Categories (Global & UA Region)
The table below documents all 31 YouTube Category IDs defined in the YouTube Data API v3, their assignability, and our automated semantic matching rules:

| Category ID | Official Category Name | Assignable for Videos | Ukrainian / English Primary Semantic Triggers | Studio Matching Priority |
| :---: | :--- | :---: | :--- | :---: |
| **`1`** | **Film & Animation** | ✅ Yes | анімація, animation, blender, 3d, кінематика, мультфільм, короткометражка, cgi, render | High (1.2) |
| **`2`** | **Autos & Vehicles** | ✅ Yes | авто, автомобілі, електрокар, tesla, двигун, транспорт, тюнінг, тест-драйв | Low (0.5) |
| **`10`** | **Music** | ✅ Yes | музика, саундтрек, пісня, біт, трек, вокал, synthwave, soundtrack, audio | Medium (0.8) |
| **`15`** | **Pets & Animals** | ✅ Yes | тварини, коти, собаки, природа, фауна, pets, wildlife | Low (0.5) |
| **`17`** | **Sports** | ✅ Yes | спорт, тренування, фітнес, матч, футбол, змагання, athletics | Low (0.5) |
| **`18`** | **Short Movies** | ⚠️ Regional | короткометражне кіно, міні-фільм, short film, кінематограф | Low (0.6) |
| **`19`** | **Travel & Events** | ✅ Yes | подорожі, туризм, міста, виставка, конференція, travel, vlog trip | Medium (0.7) |
| **`20`** | **Gaming** | ✅ Yes | геймінг, ігри, проходження, стрім гри, gameplay, unreal engine, unity, steam | Medium (1.0) |
| **`21`** | **Videoblogging** | ⚠️ Regional | відеоблог, лайфстайл, повсякденність, vlogger, vlog diary | Medium (0.8) |
| **`22`** | **People & Blogs** | ✅ Yes | щоденник, відповіді на коментарі, відповідає хейтерам, моє життя, особисте, підписник | **High (1.4)** |
| **`23`** | **Comedy** | ✅ Yes | стендап, standup, гумор, жарт, мем, смішн, прикол, баги, фейл, іронія, сатира, ржака | **High (1.5)** |
| **`24`** | **Entertainment** | ✅ Yes | краш-тест, парадокс, битва, проти, vs, челендж, шоу, експеримент, інтрига, розслідування | **High (1.1)** |
| **`25`** | **News & Politics** | ✅ Yes | огляд тижня, новини, події, реліз, анонс, злив, скандал, закон, заборона, news, фактах | **High (1.3)** |
| **`26`** | **Howto & Style** | ✅ Yes | як створити, покроковий гайд, туторіал, як зробити, 0 гривень, швидкий старт, лайфхак, manual | **High (1.3)** |
| **`27`** | **Education** | ✅ Yes | як мислить, тест тюрінга, як працює, теорія, що таке, пояснення, розбір, чому саме, аналітика | **Core Anchor (1.2)** |
| **`28`** | **Science & Technology** | ✅ Yes | штучний інтелект, ші, ai, нейромереж, робот, gemini, llm, квантовий, кібербезпека, api, код, agi | **Primary Anchor (1.0)** |
| **`29`** | **Nonprofits & Activism** | ✅ Yes | благодійність, волонтерство, збір коштів, донати, ініціатива, nonprofit | Medium (0.9) |
| **`30`** | **Movies** | ❌ System only | повнометражне кіно (резервовано для платних ліцензійних фільмів) | N/A |
| **`31`** | **Anime/Animation** | ❌ Regional | аніме, японська анімація, manga, anime | Low (0.5) |
| **`32`** | **Action/Adventure** | ❌ System only | екшн, бойовик, пригодницькі фільми | N/A |
| **`33`** | **Classics** | ❌ System only | класичне ретро-кіно | N/A |
| **`34`** | **Comedy (Movies)** | ❌ System only | кінокомедії | N/A |
| **`35`** | **Documentary** | ✅ Yes | документальний фільм, документалка, хроніка, історія технологій | Medium (1.0) |
| **`36`** | **Drama** | ❌ System only | драматичне кіно | N/A |
| **`37`** | **Family** | ❌ System only | сімейний контент | N/A |
| **`38`** | **Foreign** | ❌ System only | іноземні фільми | N/A |
| **`39`** | **Horror** | ❌ System only | фільми жахів | N/A |
| **`40`** | **Sci-Fi/Fantasy** | ❌ System only | наукова фантастика, фентезі (кінокатегорія) | N/A |
| **`41`** | **Thriller** | ❌ System only | трилери | N/A |
| **`42`** | **Shorts** | ❌ System only | зарезервовано для внутрішнього форматування платформи | N/A |
| **`43`** | **Shows** | ❌ System only | телевізійні шоу | N/A |
| **`44`** | **Trailers** | ❌ System only | трейлери та тизери кінофільмів | N/A |

---

## 3. Semantic Priority & Weight Resolution
In case of ambiguous or overlapping content (e.g. an AI comedy standup with coding tutorials), [`CategorySelector`](file:///d:/JerminaStudio/JerminaDev/src/jemini/publishing/category_selector.py) computes a weighted score for each candidate category:

$$\text{Score}(\text{Cat}) = \text{BaseWeight}(\text{Cat}) \times \sum_{k \in \text{Matches}} \text{KeywordWeight}(k) \times \text{FieldMultiplier}$$

### Field Multipliers:
- **Title Matches:** $2.5\times$ (Title has the highest algorithmic significance).
- **Tag Exact Matches:** $1.5\times$.
- **Description Body Matches:** $1.0\times$.

### Priority Rules:
1. **Comedy Override:** If standup or satirical comedy markers are dominant in the title (`"стендап"`, `"жарт"`, `"мем"`), Category `23` takes precedence over pure tech `28`.
2. **Howto / Educational Guidance:** If title begins with `"Як створити..."` or contains `"0 гривень"`, Category `26` (Howto) or `27` (Education) wins.
3. **Channel Identity Fallback:** If confidence is below $0.4$, the selector falls back to the default channel anchor: **`28` (Science & Technology)** for `stickman_lab`.

---

## 4. Verification & Watcher Cron
- **Command:** `jemini youtube-verify --channel-id <CHANNEL_ID> --count 5`
- **Background Daemon Task:** Executes every 2 hours (`0 */2 * * *`).
- **Audit Checks:**
  1. Video status is `public` and `embeddable`.
  2. `categoryId` matches intended semantic classification.
  3. No processing warnings, copyright flags, or algorithmic suppressions.
