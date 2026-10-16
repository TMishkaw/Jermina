---
name: remotion-three
description: >-
  Procedural 3D motion graphics via code using Remotion, React Three Fiber (R3F), and Three.js.
  Specialized for rendering 3D models (e.g., germina_blueprint_head.obj, neeloo_head.obj) with frame-accurate
  deterministic camera control, holographic materials, neon sweeps, and particle systems for 9:16 vertical videos.
---

# Remotion Three (Procedural 3D Motion Graphics)

## Overview
This skill provides automated 3D motion graphics and procedural scene rendering using **@remotion/three** and **React Three Fiber**.
Unlike standard interactive WebGL (which relies on non-deterministic real-time `useFrame()`), this skill uses Remotion's frame synchronization (`useCurrentFrame()`), guaranteeing **100% deterministic, frame-by-frame rendering** without dropped frames or jitter.

---

## 1. Core Architecture: Frame Synchronization Rule

> [!IMPORTANT]
> **NEVER use `useFrame()` for video animations in Remotion!**
> `useFrame(state, delta)` depends on the host machine's wall-clock frame rate and will desynchronize during video rendering.
> **ALWAYS use `useCurrentFrame()` and `interpolate()` or `spring()` from `remotion`.**

```tsx
import { useCurrentFrame, interpolate } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useRef } from "react";
import * as THREE from "three";

export const ProceduralMesh: React.FC = () => {
  const frame = useCurrentFrame();
  const meshRef = useRef<THREE.Mesh>(null);

  // Deterministic 360-degree rotation across 180 frames
  const rotationY = interpolate(frame, [0, 180], [0, Math.PI * 2]);
  const bounceY = Math.sin(frame * 0.08) * 0.15;

  return (
    <mesh ref={meshRef} rotation={[0, rotationY, 0]} position={[0, bounceY, 0]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#06b6d4" roughness={0.3} metalness={0.8} />
    </mesh>
  );
};
```

---

## 2. Loading JERMINA 3D Models (`.obj` / `.glb`)

JERMINA assets are located at:
- `D:\JERMINA\germina_blueprint_head.obj`
- `D:\JERMINA\germina_head.obj`
- `D:\JERMINA\neeloo_head.obj`
- `D:\JERMINA\assets\models\germina_full_head_bust.obj`

### OBJ Loader Component with Hologram Wireframe
```tsx
import React, { useMemo } from "react";
import { useLoader } from "@react-three/fiber";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader.js";
import { staticFile, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import * as THREE from "three";

interface HeadModelProps {
  objPath: string; // e.g. staticFile("germina_blueprint_head.obj")
  accentColor?: string;
  wireframeOnly?: boolean;
}

export const JerminaHeadScene: React.FC<HeadModelProps> = ({
  objPath,
  accentColor = "#00F0FF",
  wireframeOnly = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const obj = useLoader(OBJLoader, objPath);

  // Clone geometry and set materials
  const clonedScene = useMemo(() => {
    const clone = obj.clone(true);
    clone.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        mesh.material = new THREE.MeshStandardMaterial({
          color: new THREE.Color(accentColor),
          wireframe: wireframeOnly,
          emissive: new THREE.Color(accentColor),
          emissiveIntensity: 0.6,
          roughness: 0.2,
          metalness: 0.9,
        });
      }
    });
    return clone;
  }, [obj, accentColor, wireframeOnly]);

  // Entrance spring animation
  const scale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 1.2, stiffness: 100 },
  });

  // Orbital rotation
  const rotationY = interpolate(frame, [0, 300], [0, Math.PI * 2]);
  const scanSweep = Math.sin(frame * 0.05) * 2;

  return (
    <group scale={scale} rotation={[0.1, rotationY, 0]} position={[0, -0.5, 0]}>
      <primitive object={clonedScene} />
      {/* Dynamic Scan Light Bar */}
      <pointLight position={[0, scanSweep, 2]} color="#FF007F" intensity={3.5} distance={5} />
    </group>
  );
};
```

---

## 3. Full Composition Wrapper for 9:16 Vertical Video

```tsx
import React from "react";
import { ThreeCanvas } from "@remotion/three";
import { Composition, staticFile } from "remotion";
import { JerminaHeadScene } from "./JerminaHeadScene";

export const Jermina3DShort: React.FC = () => {
  return (
    <div className="w-full h-full bg-[#05070E] relative">
      <ThreeCanvas
        width={1080}
        height={1920}
        camera={{ position: [0, 0, 5], fov: 45 }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 10, 5]} intensity={1.5} color="#FFFFFF" />
        <pointLight position={[-4, -2, -2]} intensity={2.0} color="#00F0FF" />
        
        <JerminaHeadScene objPath={staticFile("germina_blueprint_head.obj")} />
      </ThreeCanvas>
    </div>
  );
};
```

---

## 4. Environment & Dependencies Setup

```bash
npm install three @types/three @react-three/fiber @remotion/three @react-three/drei
```
To bundle static 3D OBJ/GLB assets, place them in the Remotion `public/` directory or reference them using `staticFile()`.
