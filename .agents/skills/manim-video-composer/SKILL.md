---
name: manim-video-composer
description: >-
  Mathematical, procedural vector graphics and kinetic architectural flowcharts using Python and Manim Community (manimce).
  Produces high-precision vector animations, data graphs, cyber HUD grids, and schematic breakdowns
  (e.g., multi-agent system diagrams, Form 2-B blueprints) formatted for 9:16 Shorts/TikTok and 16:9 widescreen.
---

# Manim Video Composer Skill

## Overview
This skill provides procedural 2D/3D vector motion graphics and mathematical animation using **Manim Community** (`manimce`).
It is designed for generating high-density technical diagrams, kinetic flowcharts (e.g. system architectures, "Форма 2-Б"), neural network graphs, mathematical curves, and HUD telemetry with sub-pixel precision.

---

## 1. Vertical 9:16 Configuration (Shorts / TikTok)

By default, Manim targets 16:9 (1920x1080). For short-form viral technical content, configure vertical output directly in Python or CLI:

### Vertical Config Snippet
```python
from manim import *

# Vertical 9:16 1080x1920 60FPS setup
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0B0E14"
```

---

## 2. Kinetic Blueprint / Architecture Diagram ("Форма 2-Б")

```python
from manim import *

class Forma2BArchitecture(Scene):
    def construct(self):
        # 1. Background Grid Telemetry
        grid = NumberPlane(
            x_range=[-4.5, 4.5, 1],
            y_range=[-8, 8, 1],
            background_line_style={
                "stroke_color": TEAL_E,
                "stroke_width": 1,
                "stroke_opacity": 0.2,
            }
        )
        self.add(grid)

        # 2. Header & Title (Kinetic Typography)
        title = Text("ФОРМА 2-Б", font="sans-serif", weight=BOLD, font_size=56, color=CYAN)
        subtitle = Text("MULTI-AGENT NEURAL DISPATCHER", font="sans-serif", font_size=24, color=GRAY_B)
        header_group = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=1.2)

        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2), run_time=1.2)

        # 3. Core Architecture Nodes
        box_brain = RoundedRectangle(corner_radius=0.2, height=1.6, width=6.5, color=BLUE_D, fill_color="#10192A", fill_opacity=0.9)
        txt_brain = Text("AI Brain Main (who_id = 17)", font_size=28, color=WHITE)
        node_brain = VGroup(box_brain, txt_brain).move_to(UP * 3)

        box_stats = RoundedRectangle(corner_radius=0.2, height=1.4, width=5.8, color=PURPLE_D, fill_color="#1E1428", fill_opacity=0.9)
        txt_stats = Text("AI Statistician (who_id = 16)", font_size=26, color=WHITE)
        node_stats = VGroup(box_stats, txt_stats).move_to(DOWN * 0.5)

        box_exec = RoundedRectangle(corner_radius=0.2, height=1.4, width=5.8, color=GREEN_D, fill_color="#10251E", fill_opacity=0.9)
        txt_exec = Text("Autonomous Actors (VFX & Code)", font_size=26, color=WHITE)
        node_exec = VGroup(box_exec, txt_exec).move_to(DOWN * 3.8)

        # 4. Animated Connectors
        arrow_1 = Arrow(start=node_brain.get_bottom(), end=node_stats.get_top(), color=CYAN, buff=0.15)
        arrow_2 = Arrow(start=node_stats.get_bottom(), end=node_exec.get_top(), color=PURPLE, buff=0.15)

        # Execution Sequence
        self.play(Create(box_brain), Write(txt_brain), run_time=0.8)
        self.play(GrowArrow(arrow_1), run_time=0.5)
        self.play(Create(box_stats), Write(txt_stats), run_time=0.8)
        self.play(GrowArrow(arrow_2), run_time=0.5)
        self.play(Create(box_exec), Write(txt_exec), run_time=0.8)

        # 5. Data Flow Pulse (Glowing Dot moving along arrow)
        pulse = Dot(color=YELLOW, radius=0.12).move_to(arrow_1.get_start())
        self.add(pulse)
        self.play(MoveAlongPath(pulse, arrow_1), rate_func=linear, run_time=0.6)
        self.play(MoveAlongPath(pulse, arrow_2), rate_func=linear, run_time=0.6)
        self.play(FadeOut(pulse))
        
        self.wait(1.5)
```

---

## 3. Telemetry HUD Waveform Generator

```python
from manim import *
import numpy as np

class AudioTelemetryWave(Scene):
    def construct(self):
        # Sine Wave Curve with dynamic updater
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-3, 3, 1],
            x_length=8,
            y_length=4,
            axis_config={"color": BLUE_C, "stroke_width": 2},
        ).to_edge(DOWN, buff=2)

        curve = axes.plot(lambda x: np.sin(x * 2.5), color=CYAN, stroke_width=4)
        glow_curve = curve.copy().set_stroke(color=TEAL, width=12, opacity=0.4)

        self.play(Create(axes), Create(glow_curve), Create(curve), run_time=1.5)
        self.wait(1)
```

---

## 4. Headless CLI Rendering Commands

### Installation
```bash
pip install manim
```

### Rendering Options
```bash
# Fast Preview (480p, quick render)
manim -ql script_scene.py Forma2BArchitecture

# High Quality 1080p (60fps) MP4 Export
manim -qh --format=mp4 script_scene.py Forma2BArchitecture

# Transparent Movie (ProRes 4444 / PNG sequence) for overlaying in Remotion/Premiere
manim -qh --format=mov -t script_scene.py Forma2BArchitecture
```
