# Visual Blind Audit & A/B Convergence Protocol

## 1. Zero-Clutter Isolated Testing Standard
When auditing animation poses, extraneous visual elements (subtitles, kinetic hook labels, blueprints, particles) contaminate the vision model's attention.
- **Mandate:** All motion audits must be executed on [`IsolatedMotionCanvas`](file:///d:/JerminaStudio/JerminaDev/remotion/src/compositions/IsolatedMotionCanvas.tsx).
- Focus is strictly constrained to:
  1. *Silhouette clarity at 0.2 seconds on a 9:16 mobile display*.
  2. *Joint anatomical naturalness (elbows, shoulders, spine)*.
  3. *Semantic fidelity to author intent*.

---

## 2. Blind Evaluation Protocol
To prevent confirmation bias, newly developed gestures are presented to the model without explicit labels or text hints:
- Model is prompted blindly:
  1. *What action/gesture is the character performing?*
  2. *What emotion/message is communicated?*
  3. *Are the limbs and joints natural and un-broken?*
  4. *What score (1-10) is assigned?*
- If the model correctly deduces the intended gesture unassisted, the preset passes congruence validation.

---

## 3. Autonomous A/B Convergence Rule
- **The 2-Consecutive-Wins Standard:**
  A modified or newly generated motion variant is committed to PostgreSQL (`stickman_motions`) **ONLY** after winning **2 consecutive rounds** in blind A/B comparison against the baseline.
- **Explainability:**
  Every decision round requires a structured `decision_rationale`, critique of both variants, key differentiator, and `evolution_direction`.
