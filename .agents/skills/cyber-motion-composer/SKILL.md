---
name: cyber-motion-composer
description: Declarative, modular cybernetic motion graphics and VFX pipeline for 9:16 Shorts/TikTok videos. Combines kinetic typography, Form 2-B HUD architecture, laser guides, and GPU optical bloom via the Cyber-VFX Scene Graph.
---

# Cyber Motion Composer Skill

Use this skill when designing, composing, or rendering modular cybernetic motion graphics in Antigravity for the JERMINA studio.

## Core Capabilities
1. **Catalog of Visual Effects**:
   - `fx_typography_reveal`: Letter-by-letter kinetic typing with laser guide cursor and blinding flash lock.
   - `fx_node_flow`: 4-stage interconnected multi-agent pipeline (`Form 2-B`) with piercing laser data pulse.
   - `fx_timeline_layer`: Simulated timeline track HUD with animated keyframe markers.
   - `fx_code_generator`: Algorithmic code editor typing window with syntax highlighting.
   - `fx_property_slider`: Interactive UI parameter diff (+ / -) with live mutating shape viewport.
   - `fx_poll_interface`: Cyberpunk interactive survey checkboxes with glowing selection ticks.

2. **Decoupled Theming**:
   - All effects dynamically inherit tokens from active themes (e.g. `cyber_violet_reference`).
   - Every single parameter (colors, fonts, speeds, flare sizes, bloom radius) is 100% tunable via layer overrides.

3. **Workflow**:
   ```python
   from src.vfx_engine.core.scene_graph import SceneGraph
   from src.vfx_engine.core.renderer import CyberRenderer

   sg = SceneGraph(scene_id="scene_01", theme_id="cyber_violet_reference")
   sg.add_layer(
       layer_id="title",
       effect_id="fx_typography_reveal",
       start_time=0.0,
       duration=4.0,
       overrides={"text": "ШТУЧНИЙ ІНТЕЛЕКТ", "cadence_frames_per_char": 2}
   )
   sg.save_spec("output/scene_01_spec.yaml")

   renderer = CyberRenderer(sg)
   renderer.render("output/video/scene_01.mp4", audio_track_path="output/audio/track.wav")
   ```

4. **MCP Tools Integration**:
   - `list_catalog_effects`: Browse available animations.
   - `get_effect_schema`: Inspect parameter bounds and defaults.
   - `compose_scene`: Validate and save Scene Graph.
   - `render_composition`: Execute final 1080x1920 30FPS master render.
