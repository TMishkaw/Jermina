import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface AudioReactorOrbProps {
  color?: string;
  size?: number;
  label?: string;
  statusText?: string;
  isSpeaking?: boolean;
  audioEnergy?: number;
}

export const AudioReactorOrb: React.FC<AudioReactorOrbProps> = ({
  color = "#00F0FF",
  size = 280,
  label = "AI CORE // ZEPHYR",
  statusText = "24kHz LIVE STREAM",
  isSpeaking = true,
  audioEnergy,
}) => {
  const frame = useCurrentFrame();

  // Real Audio RMS reactivity if supplied, otherwise procedural
  const actualEnergy = typeof audioEnergy === "number" ? audioEnergy : undefined;

  let totalPulse = 0;
  if (actualEnergy !== undefined) {
    // Gentle, refined audio pulse: soft scaling without aggressive bulging
    const jitter = Math.sin(frame * 1.2) * 0.015 * actualEnergy;
    totalPulse = actualEnergy * 0.18 + jitter;
  } else {
    // Procedural fallback
    const speechJitter = Math.sin(frame * 0.9) * 0.02 + Math.cos(frame * 1.4) * 0.015;
    const syllabicPulse = Math.pow(Math.abs(Math.sin(frame * 0.28)), 3) * 0.12;
    const breathPulse = Math.sin(frame * 0.08) * 0.04;
    totalPulse = isSpeaking ? (syllabicPulse + speechJitter + breathPulse) : breathPulse;
  }

  const baseScale = 1 + totalPulse;
  const outerScale = 1 + totalPulse * 0.8;
  const ringScale = 1 + totalPulse * 0.5;

  const rotation = frame * 0.8;
  const counterRotation = -frame * 0.5;

  const glowRadius = interpolate(totalPulse, [0, 0.2], [25, 55], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        width: size,
        height: size,
      }}
    >
      {/* Outer Rotating Segmented Ring */}
      <svg
        width={size}
        height={size}
        style={{
          position: "absolute",
          transform: `rotate(${rotation}deg) scale(${outerScale})`,
          transformOrigin: "center",
          opacity: 0.7,
        }}
        viewBox="0 0 200 200"
      >
        <circle
          cx="100"
          cy="100"
          r="88"
          fill="none"
          stroke={color}
          strokeWidth="1.5"
          strokeDasharray="16 12 4 12"
        />
        <circle
          cx="100"
          cy="100"
          r="78"
          fill="none"
          stroke="rgba(255, 255, 255, 0.25)"
          strokeWidth="1"
          strokeDasharray="4 8"
        />
      </svg>

      {/* Counter-Rotating Inner Ring */}
      <svg
        width={size}
        height={size}
        style={{
          position: "absolute",
          transform: `rotate(${counterRotation}deg) scale(${ringScale})`,
          transformOrigin: "center",
          opacity: 0.85,
        }}
        viewBox="0 0 200 200"
      >
        <circle
          cx="100"
          cy="100"
          r="62"
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeDasharray="30 20 10 20"
        />
      </svg>

      {/* Central Pulsing Plasma Core */}
      <div
        style={{
          width: size * 0.45,
          height: size * 0.45,
          borderRadius: "50%",
          background: `radial-gradient(circle at 35% 35%, #FFFFFF 0%, ${color} 55%, #050811 100%)`,
          boxShadow: `0 0 ${glowRadius}px ${color}, 0 0 ${glowRadius * 1.5}px ${color}88, inset 0 0 25px rgba(255, 255, 255, 0.9)`,
          transform: `scale(${baseScale})`,
          transition: "transform 0.04s ease-out",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          zIndex: 2,
        }}
      >
        {/* Core Crosshair reticle */}
        <div
          style={{
            width: "60%",
            height: "1px",
            background: "rgba(255, 255, 255, 0.7)",
            position: "absolute",
          }}
        />
        <div
          style={{
            height: "60%",
            width: "1px",
            background: "rgba(255, 255, 255, 0.7)",
            position: "absolute",
          }}
        />
      </div>

      {/* Metadata Labels Below Orb */}
      <div
        style={{
          position: "absolute",
          bottom: -45,
          textAlign: "center",
          width: 260,
        }}
      >
        <div
          style={{
            fontFamily: "monospace",
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: "0.15em",
            color: color,
            textShadow: `0 0 10px ${color}`,
          }}
        >
          {label}
        </div>
        <div
          style={{
            fontFamily: "monospace",
            fontSize: 10,
            letterSpacing: "0.1em",
            color: "rgba(255, 255, 255, 0.5)",
            marginTop: 3,
          }}
        >
          {statusText}
        </div>
      </div>
    </div>
  );
};
