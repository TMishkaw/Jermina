---
name: stickman-animation-composer
description: End-to-end programmatic stickman animation engine across Remotion (2D SVG/React), Manim (Python vector), and Blender (3D armature). Generates expressive skeletal motions, walk/run cycles, lip-sync gestures, fight choreography, and viral 9:16 Shorts.
---

# Stickman Animation Composer Skill

Ця навичка надає повний стек інструментів для створення, кінематичного моделювання та програмного рендерингу анімацій персонажів у стилі **Stickman** (стікмен / схематичний чоловічок).

Підтримуються 3 виробничі рушії:
1. **Remotion 2D (React + SVG + Canvas)**: інтерактивний веб-монтаж, 9:16 Shorts, синхронізація жестикуляції з аудіо.
2. **Manim Community (Python)**: векторні експлейнери, інтеграція з математичними формулами та кодом.
3. **Blender EEVEE (Python `bpy`)**: 3D неонові скелети, камери, кінематографічне освітлення та мокап.

---

## 1. Коли активувати цю навичку
- Створення динамічних або комедійних 9:16 роликів для YouTube Shorts / TikTok за участю стікмена.
- Потреба у візуалізації ідей, коду або складних концептів через живого схематичного персонажа.
- Створення анімації бійок (stickman fight), бігу, падінь, лекційного виступу чи емоційних реакцій.
- Автоматизація генерації відео, де стікмен говорить голосом з `jermina-voice`.

---

## 2. Швидкий старт: Remotion 2D (Рекомендований для Shorts)

Компоненти розташовані у `templates/remotion/`:
- `StickmanRig.tsx`: повний векторний компонент із суглобами ліктів/колін, поворотом корпусу та нахилом голови.
- `kinematic_presets.ts`: математичні функції обчислення кутів для 9 станів:
  `idle`, `walk`, `run`, `talk`, `point`, `jump`, `punch`, `shocked`, `celebrate`.
- `FacialExpressions.tsx`: очі (`neutral`, `happy`, `angry`, `surprised`, `dead`, `wink`, `suspicious`) та рот (`neutral`, `smile`, `open`, `talking`, `gasp`, `smirk`).

### Приклад використання в Remotion:
```tsx
import React from "react";
import { StickmanRig } from "./templates/remotion/StickmanRig";

export const StickmanScene: React.FC = () => {
  return (
    <div style={{ width: 1080, height: 1920, backgroundColor: "#0C0D14" }}>
      {/* Головний персонаж: пояснює тему з мікрофоном */}
      <StickmanRig
        animation="talk"
        x={540}
        y={1250}
        scale={1.4}
        color="#00FFAA"
        glowColor="#00FFAA"
        prop="microphone"
        eyeType="wink"
        mouthType="talking"
      />
    </div>
  );
};
```

---

## 3. Python Manim: Векторні експлейнери

Розташування: `templates/manim/stickman_scene.py`

Використовується для технічних та навчальних відео. Клас `Stickman` наслідує `VGroup` та підтримує прямі команди:
```python
char = Stickman(color="#00FFAA")
self.play(char.wave_gesture())       # Помахати рукою
self.play(char.point_at(formula))    # Вказати рукою на об'єкт
```

Запуск рендеру:
```bash
manim -pql templates/manim/stickman_scene.py StickmanExplainerScene
```

---

## 4. Blender `bpy`: 3D неонові кібер-стікмени

Розташування: `templates/blender/generate_stickman_rig.py`

Будує повноцінний 3D Armature (Hips, Spine, Shoulders, Forearms, Thighs, Shins), накладає неоновий Emission-матеріал і прораховує ходу формулами в headless режимі:
```bash
blender --background --python templates/blender/generate_stickman_rig.py -- output/video/stickman_3d.mp4
```

---

## 5. Режисура та хореографія (Choreography Guide)
Для отримання високого утримання аудиторії (retention > 70%) обов'язково дотримуйся [Choreography Guide](file:///D:/JERMINA/.agents/skills/stickman-animation-composer/references/choreography_guide.md):
- Випередження жесту: жест стікмена починається за **2–4 кадри** до промовлення ключового слова.
- Удар / панч: 4 кадри замах, **1–2 кадри** на сам удар, пауза контакту на 2 кадри.
- Комедійний стоп-кадр: фіксація пози на моменті панчлайну з очима `dead` або `smirk`.
