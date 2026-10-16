import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";

interface FloatingCyberParticle {
  id: number;
  xPercent: number;
  baseYPercent: number;
  size: number;
  speed: number;
  orbitPhase: number;
  type: "cross" | "dot" | "code_fragment" | "ring" | "diamond";
  text?: string;
  depth: number;
}

interface CyberParticlesBackgroundProps {
  accentColor: string;
  count?: number;
  audioEnergy?: number;
}

const SNIPPETS = ["01", "24kHz", "LIVE", "PCM", "GENAI", "3.8", "AI//SYS", "0xFF", "TOKEN", "WAV"];

export const CyberParticlesBackground: React.FC<CyberParticlesBackgroundProps> = ({
  accentColor,
  count = 22,
  audioEnergy,
}) => {
  const frame = useCurrentFrame();

  // Pseudo-deterministic particle generation based on indices
  const particles: FloatingCyberParticle[] = useMemo(() => {
    return Array.from({ length: count }).map((_, i) => {
      const types: FloatingCyberParticle["type"][] = ["cross", "dot", "code_fragment", "ring", "diamond"];
      const type = types[i % types.length];
      const text = SNIPPETS[i % SNIPPETS.length];
      const xPercent = (17 * (i + 1) * 31) % 88 + 6; // Stay between 6% and 94%
      const baseYPercent = (23 * (i + 1) * 47) % 84 + 8; // Stay between 8% and 92%
      const size = 6 + (i % 5) * 3;
      const speed = 0.4 + (i % 4) * 0.25;
      const orbitPhase = (i * 1.33);
      const depth = 0.3 + ((i % 5) / 5) * 0.7; // Depth for parallax

      return {
        id: i,
        xPercent,
        baseYPercent,
        size,
        speed,
        orbitPhase,
        type,
        text,
        depth,
      };
    });
  }, [count]);

  // Audio-reactivity rhythmic factor (use gentle real audio energy if provided)
  const audioPulse =
    typeof audioEnergy === "number"
      ? audioEnergy * 0.4
      : (Math.pow(Math.sin(frame * 0.25), 4) * 0.3 +
        Math.abs(Math.sin(frame * 0.12)) * 0.2);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
        pointerEvents: "none",
        zIndex: 2,
      }}
    >
      {particles.map((p) => {
        // Chaotic dynamic floating + audio reaction kick
        const floatY = Math.sin(frame * 0.05 * p.speed + p.orbitPhase) * 24 * p.depth;
        const floatX = Math.cos(frame * 0.04 * p.speed + p.orbitPhase) * 18 * p.depth;
        const audioKick = audioPulse * (10 + p.size * 1.5) * p.depth;
        const currentScale = 1 + audioPulse * 0.35 * p.depth;
        const currentOpacity = (0.25 + 0.5 * p.depth + audioPulse * 0.35);

        const posX = `calc(${p.xPercent}% + ${floatX}px)`;
        const posY = `calc(${p.baseYPercent}% + ${floatY - audioKick}px)`;

        return (
          <div
            key={p.id}
            style={{
              position: "absolute",
              left: posX,
              top: posY,
              transform: `translate(-50%, -50%) scale(${currentScale})`,
              opacity: Math.min(1, currentOpacity),
              color: p.id % 3 === 0 ? accentColor : "#94A3B8",
              fontFamily: "monospace",
              userSelect: "none",
            }}
          >
            {p.type === "cross" && (
              <span
                style={{
                  fontSize: p.size * 1.8,
                  fontWeight: 900,
                  textShadow: p.id % 3 === 0 ? `0 0 10px ${accentColor}` : "none",
                }}
              >
                +
              </span>
            )}

            {p.type === "dot" && (
              <div
                style={{
                  width: p.size,
                  height: p.size,
                  borderRadius: "50%",
                  background: p.id % 2 === 0 ? accentColor : "#FFFFFF",
                  boxShadow: `0 0 12px ${accentColor}`,
                }}
              />
            )}

            {p.type === "ring" && (
              <div
                style={{
                  width: p.size * 2,
                  height: p.size * 2,
                  borderRadius: "50%",
                  border: `1.5px solid ${accentColor}`,
                  boxShadow: `0 0 10px ${accentColor}88`,
                }}
              />
            )}

            {p.type === "diamond" && (
              <div
                style={{
                  width: p.size * 1.2,
                  height: p.size * 1.2,
                  transform: "rotate(45deg)",
                  border: `1px solid ${accentColor}`,
                  background: `${accentColor}33`,
                }}
              />
            )}

            {p.type === "code_fragment" && (
              <div
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  letterSpacing: "0.15em",
                  padding: "2px 6px",
                  borderRadius: 4,
                  border: `1px solid ${accentColor}44`,
                  background: "rgba(10, 15, 25, 0.6)",
                  boxShadow: `0 0 8px ${accentColor}33`,
                  color: "#E2E8F0",
                }}
              >
                {p.text}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
