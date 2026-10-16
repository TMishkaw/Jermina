# YouTube Semantic Category Selection & Channel Governance

## 1. Automated Semantic Category Selection
The [`CategorySelector`](file:///d:/JerminaStudio/JerminaDev/src/jemini/publishing/category_selector.py) module dynamically assigns the optimal YouTube `categoryId` based on title, script keywords, and thematic genre:

| Category ID | YouTube Category Name | Primary Triggers & Topics |
| :---: | :--- | :--- |
| **`28`** | **Science & Technology** | AI, LLM, Neural Networks, Gemini, Code, Python, Cybernetics, Robotics, Shaders |
| **`27`** | **Education** | Tutorials, How-To, Explanations, Deep Dives, Academic Breakdowns |
| **`24`** | **Entertainment** | Satire, Sketches, Comedy Memes, Channel Parodies, Cyberpunk Fiction |
| **`22`** | **People & Blogs** | Personal Reflections, Vlogs, Community Q&A, Creator Stories |

---

## 2. Watcher & Verification Cron
- Automated channel verification runs periodically (`0 */2 * * *`) via background scheduler.
- Verifies that published videos are public, active, properly indexed, and assigned the correct category ID.
