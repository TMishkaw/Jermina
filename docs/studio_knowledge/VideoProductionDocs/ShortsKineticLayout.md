# Vertical 9:16 Shorts Kinetic Layout & UI Safe Zones

## 1. Resolution & Canvas Standards
- **Aspect Ratio:** `9:16` (Vertical Full-Screen).
- **Pixel Dimensions:** `1080 x 1920` px.
- **Frame Rate:** `30 FPS`.
- **Target Video Duration:** $25\text{–}58$ seconds (optimal algorithm retention window).

---

## 2. Mobile Platform UI Safe Zones (YouTube Shorts & TikTok)
Mobile client applications render persistent native interface overlays that cover substantial portions of the screen. All critical storytelling elements (stickman head, animated subtitles, emoji props) must strictly reside inside the **Active Content Zone**:

```
 0 px   ┌──────────────────────────────────────────────┐
        │  [ TOP EXCLUSION ZONE: 0 - 220 px ]          │ ◄ Channel name, search icon, phone status bar
220 px  ├──────────────────────────────────────────────┤
        │                                              │
        │                                              │
        │         ACTIVE CONTENT ZONE                  │
        │         (Width: 80 - 940 px)                 │ ◄ Stickman character, kinetic text, props
        │         (Height: 240 - 1520 px)              │
        │                                        ┌───┐ │
        │                                        │ ♥ │ │ ◄ RIGHT INTERACTION MARGIN
        │                                        ├───┤ │   (Width: 940 - 1080 px)
        │                                        │ 💬│ │   Like, Dislike, Comment,
        │                                        ├───┤ │   Share, Remix buttons
        │                                        │ ↗ │ │
1520 px ├────────────────────────────────────────┴───┤ │
        │  [ BOTTOM EXCLUSION ZONE: 1520 - 1920 px ]   │ ◄ Video title (2 lines), Avatar, Subscribe, Sound
1920 px └──────────────────────────────────────────────┘
```

---

## 3. Stickman Character Staging
- **Anchor Coordinates:** Center $X = 540\text{ px}$, Base Ground $Y = 1160\text{ px}$.
- **Character Scale:** `scale = 2.7` in [`StickmanShort9x16.tsx`](file:///d:/JerminaStudio/JerminaDev/remotion/src/compositions/StickmanShort9x16.tsx).
- **Head & Eye Line:** Rests between $Y = 720\text{–}850\text{ px}$, perfectly centered in the mobile viewer's primary visual focal plane.
- **Floor Glow Stage:** Centered ellipse at $Y = 1580\text{ px}$, width $700\text{ px}$, height $120\text{ px}$.

---

## 4. Kinetic Subtitle Typography
- **Position:** Fixed at $Y \approx 420\text{–}480\text{ px}$ (upper-middle chest level).
- **Pacing:** Maximum 3 to 4 words visible simultaneously.
- **Font Styling:**
  - Font Family: `Inter`, `Montserrat`, or `SF Pro Display`, font-weight 900 (Black).
  - Size: $58\text{–}68\text{ px}$.
  - Text Color: `#FFFFFF` with primary keyword highlighting in cyan `#00F0FF` or gold `#FFD700`.
  - Drop Shadow: `0px 4px 16px rgba(0, 0, 0, 0.85)` + neon glow outline.
- **Animation:** Spring-physics pop-in on every active word cadence.
