---
name: remotion-motion-designer
description: >-
  Programmatic motion graphics and video generation using Remotion v4+ (React, TypeScript, Tailwind, Skia).
  Creates viral 9:16 and 16:9 animations, kinetic typography, spring-physics motion, audio waveforms, HUD overlays,
  and deterministic code-driven video rendering without manual keyframes.
---

# Remotion Motion Designer Skill

## Overview
This skill provides automated motion graphics design and video production via **Remotion v4+**.
Instead of manual keyframing in GUI editors, motion graphics are defined as deterministic React components driven by `useCurrentFrame()`, `useVideoConfig()`, `interpolate()`, and `spring()`.

---

## 1. Core Principles & Animation Physics

### 12 Rules of Animation in Code
1. **Squash and Stretch**: Scale distortion preserving volume (`scaleX = 1 + stretch`, `scaleY = 1 / (1 + stretch)`).
2. **Anticipation**: Backward movement before forward action (`frame < 5 ? interpolate(frame, [0, 5], [0, -15]) : ...`).
3. **Staging & Pacing**: Keep focus on a single primary element at a time; 3-second viral hook rule.
4. **Follow-Through & Overlapping Action**: Secondary elements lag behind primary motion by 2-6 frames.
5. **Slow In and Slow Out**: Use natural easing curve or `spring()` damping.
6. **Exaggeration**: Dynamic overshoot on springs for energy and punchiness.

### Spring Physics Presets
Remotion `spring()` calculates natural physical motion based on damping, mass, and stiffness:

```typescript
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

// 1. BOUNCY (Playful, cartoonish, high energy)
const bouncySpring = spring({
  frame,
  fps,
  config: { damping: 8, mass: 0.5, stiffness: 120 },
});

// 2. SNAPPY (Fast UI, tech HUD, abrupt and sharp)
const snappySpring = spring({
  frame,
  fps,
  config: { damping: 20, mass: 0.8, stiffness: 250 },
});

// 3. BUTTERY (Cinematic, smooth, luxury, elegant)
const butterySpring = spring({
  frame,
  fps,
  config: { damping: 18, mass: 1.2, stiffness: 80 },
});

// 4. HEAVY (Impactful, weighty, title drops)
const heavySpring = spring({
  frame,
  fps,
  config: { damping: 26, mass: 2.5, stiffness: 140 },
});
```

---

## 2. Standard Composition Standards

### Vertical 9:16 (Shorts / TikTok / Reels)
- **Width**: `1080`
- **Height**: `1920`
- **FPS**: `30` or `60`
- **Safe Area**: Top `150px` (header icons) and Bottom `280px` (captions, audio title, action buttons) reserved.
- **Duration**: 450 to 1740 frames (15s – 58s).

### Kinetic Typography Template
```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface KineticTextProps {
  words: string[];
  highlightIndices?: number[];
  baseColor?: string;
  highlightColor?: string;
}

export const KineticTypography: React.FC<KineticTextProps> = ({
  words,
  highlightIndices = [1],
  baseColor = "#FFFFFF",
  highlightColor = "#38BDF8",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div className="flex flex-wrap items-center justify-center gap-4 px-12">
      {words.map((word, i) => {
        const delay = i * 4;
        const localFrame = Math.max(0, frame - delay);
        
        const scale = spring({
          frame: localFrame,
          fps,
          config: { damping: 12, mass: 0.6, stiffness: 180 },
        });

        const opacity = interpolate(localFrame, [0, 4], [0, 1], {
          extrapolateRight: "clamp",
        });

        const isHighlight = highlightIndices.includes(i);

        return (
          <span
            key={i}
            style={{
              transform: `scale(${scale})`,
              opacity,
              color: isHighlight ? highlightColor : baseColor,
              textShadow: isHighlight ? "0 0 25px rgba(56, 189, 248, 0.75)" : "none",
            }}
            className="text-6xl font-black uppercase tracking-tight"
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
```

---

## 3. Cyberpunk HUD & Procedural Overlays

### HUD Grid & Scanning Line Overlay
```tsx
import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const CyberHUDOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const { height, durationInFrames } = useVideoConfig();

  const scanY = interpolate(
    frame % 90,
    [0, 90],
    [0, height],
    { extrapolateRight: "clamp" }
  );

  return (
    <div className="absolute inset-0 pointer-events-none z-30">
      {/* Background Matrix/Grid */}
      <div 
        className="w-full h-full opacity-10"
        style={{
          backgroundImage: "linear-gradient(#06b6d4 1px, transparent 1px), linear-gradient(90deg, #06b6d4 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }}
      />
      {/* Scanning laser line */}
      <div
        className="absolute left-0 right-0 h-1 bg-cyan-400 opacity-60 shadow-[0_0_15px_#22d3ee]"
        style={{ top: `${scanY}px` }}
      />
      {/* Corner Brackets */}
      <div className="absolute top-8 left-8 w-8 h-8 border-t-2 border-l-2 border-cyan-400" />
      <div className="absolute top-8 right-8 w-8 h-8 border-t-2 border-r-2 border-cyan-400" />
      <div className="absolute bottom-8 left-8 w-8 h-8 border-b-2 border-l-2 border-cyan-400" />
      <div className="absolute bottom-8 right-8 w-8 h-8 border-b-2 border-r-2 border-cyan-400" />
    </div>
  );
};
```

---

## 4. Execution & CLI Render Workflow

### Project Initialization
```bash
# In project directory
npx create-video@latest remotion-studio --template=blank
cd remotion-studio
npm install tailwindcss lucide-react @remotion/media-utils
```

### Headless Render Command
```bash
# Render vertical Short to MP4
npx remotion render src/index.ts MainScene out/short_render.mp4 --props='{"theme":"cyberpunk"}' --gl=angle
```
