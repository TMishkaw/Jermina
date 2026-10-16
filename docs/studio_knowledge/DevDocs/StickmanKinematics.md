# Stickman Kinematics & Rigging Specification

## 1. Coordinate Geometry & Angle Standards (`StickmanRig.tsx`)
In `StickmanRig.tsx`, joint angles are calculated via forward kinematics relative to the root anchor and segment rotation:
```typescript
const getSegmentEnd = (startX: number, startY: number, length: number, angleDeg: number) => {
  const rad = (angleDeg * Math.PI) / 180;
  return {
    x: startX + Math.sin(rad) * length,
    y: startY + Math.cos(rad) * length,
  };
};
```

### Fundamental Directional Rules:
- **`0°` (Neutral / Down):** Segment points directly downwards along $+Y$.
- **Negative Angles (`-θ°`):** Segment rotates counter-clockwise towards the **LEFT** ($-X$).
- **Positive Angles (`+θ°`):** Segment rotates clockwise towards the **RIGHT** ($+X$).
- **`±180°` (Up):** Segment points straight upwards along $-Y$.

### Symmetrical Two-Handed Poses:
For symmetrical gestures (`heart_hands`, `shrug`, `explain`, `stop`, `celebrate`, `idle`), limbs **MUST** possess balanced opposite shoulder angles:
- **Left Arm:** `leftShoulderAngle < 0` (flaring leftward) with proportional `leftElbowAngle`.
- **Right Arm:** `rightShoulderAngle > 0` (flaring rightward) with inverted `rightElbowAngle`.
> [!WARNING]
> Assigning negative angles to both shoulders (e.g. `leftShoulderAngle: -50, rightShoulderAngle: -50`) causes the right arm to fold across the chest or overlap the left side, breaking anatomical naturalness.

---

## 2. Core Kinematic Motion Cycles

| Preset | Left Arm (Shoulder / Elbow) | Right Arm (Shoulder / Elbow) | Intent & Silhouette Readability |
| :--- | :--- | :--- | :--- |
| **`heart_hands`** | $-145^\circ$ / $-70^\circ$ | $+145^\circ$ / $+70^\circ$ | High arch over head meeting at pulsing neon heart |
| **`shrug`** | $-55^\circ$ / $+90^\circ$ | $+55^\circ$ / $-90^\circ$ | Wide questioning shrug with open palms outward |
| **`explain`** | $-34^\circ + \text{waveL}$ / $+45^\circ$ | $+34^\circ + \text{waveR}$ / $-45^\circ$ | Two-handed conversational gesticulation on both sides |
| **`point_user`** | $-24^\circ$ / $+110^\circ$ | $-65^\circ + \text{pulse}$ / $+6^\circ$ | Left hand resting on left hip, right hand pointing at camera |
| **`stop`** | $-75^\circ$ / $+15^\circ$ | $+75^\circ$ / $-15^\circ$ | Both palms thrust forward with defensive body brace |
| **`idle`** | $-10^\circ$ / $+12^\circ$ | $+10^\circ$ / $-12^\circ$ | Relaxed resting posture with breathing micro-flex |
| **`celebrate`** | $-130^\circ$ / $+20^\circ$ | $+130^\circ$ / $-20^\circ$ | V-shaped celebratory victory wave |

---

## 3. Organic Motion Principles

### 3.1 S-Curve Pose Blending (`interpolatePose`)
- All transitions between cues must use a 12-frame smoothstep S-curve:
  $$t = p^2 \cdot (3 - 2p)$$
- Eliminates mechanical linear snapping between gestures.

### 3.2 Overlapping Action (Secondary Motion)
- Forearms lag upper arm movement by $\approx 90\text{ ms}$ ($\Delta t = 0.09\text{ s}$).
- Prevents robotic unison movement and gives realistic joint elasticity.

### 3.3 Dynamic Quadratic Bezier Spine
- The spine is rendered via a smooth Bezier curve:
  `M 0 hipY Q spineBend midY 0 shoulderY`
- Breathing and speaking volume (`audioRms`) induce continuous micro-flexion.
