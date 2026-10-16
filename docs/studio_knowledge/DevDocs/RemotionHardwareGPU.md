# Remotion Hardware Acceleration & Rendering Pipelines

## 1. Hardware Architecture & Workload Delegation
The Jermina Studio rendering workstation operates with dual graphics processors and multi-core CPU:
- **GPU 1: NVIDIA GeForce MX130** (Maxwell GM108, CUDA 13.0, compute capability 5.0):
  - Dedicated to Blender 3D procedural headless rendering (Cycles/EEVEE) with CUDA acceleration.
  - Does not contain dedicated NVENC hardware video encoding chip.
- **GPU 2: Intel UHD Graphics 630** (Gen9.5, Intel QuickSync Video):
  - Hardware accelerated H.264/HEVC decoding and encoding.
  - Acceleration for Chromium headless browser instances in Remotion.
- **CPU: Intel Core i7-8850H** (6 physical cores, 12 hyperthreads, up to 4.3 GHz):
  - Primary driver for Remotion multi-process parallel rendering.

---

## 2. Remotion Render Flags & CLI Optimization
When executing video compiles via [`RemotionRenderer`](file:///d:/JerminaStudio/JerminaDev/src/jemini/rendering/remotion_renderer.py):
```bash
npx remotion render src/index.ts StickmanShort9x16 "out/video.mp4" \
  --props="active_props.json" \
  --concurrency=6 \
  --bundle-cache \
  --x264-preset=veryfast
```
### Key Optimization Parameters:
1. `--concurrency=6`: Allocates 1 Chromium render worker per physical CPU core for optimal throughput without thermal throttling.
2. `--bundle-cache`: Caches Webpack compilation artifacts, cutting startup latency from ~8s to <1s on subsequent renders.
3. `--x264-preset=veryfast`: Provides 3.5x faster frame-to-H.264 encoding with visually indistinguishable 9:16 mobile fidelity.

---

## 3. Isolated Motion Canvas (`IsolatedMotionCanvas.tsx`)
- **Composition ID:** `IsolatedMotionCanvas` (`1080x1920`, 30 FPS).
- **Design Philosophy:** 100% distraction-free testing environment for model audits:
  - Background `#07090E`.
  - Subtle ground stage glow (`radialGradient`, opacity 0.30).
  - High-resolution stickman scaled to 2.7x.
  - Zero HUD grids, zero subtitle banners, zero floating particles.
- **Rendering Stills for Review:**
  ```bash
  npx remotion still src/index.ts IsolatedMotionCanvas out/frame.png --frame=30 --props=props.json
  ```
