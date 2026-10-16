import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface Forma2BBlueprintProps {
  accentColor?: string;
  title?: string;
}

export const Forma2BBlueprint: React.FC<Forma2BBlueprintProps> = ({
  accentColor = "#00F0FF",
  title = "ФОРМА 2-Б: СИСТЕМА АВТОНОМНИХ АГЕНТІВ",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const scaleProgress = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Animated pulse progress along connectors (repeating 0 to 1 every 40 frames)
  const pulsePhase = (frame % 45) / 45;

  return (
    <div
      style={{
        background: "rgba(11, 14, 20, 0.94)",
        border: `1px solid ${accentColor}44`,
        borderRadius: 16,
        padding: "20px 24px",
        boxShadow: `0 20px 40px rgba(0,0,0,0.7), inset 0 0 20px ${accentColor}11`,
        transform: `scale(${Math.min(1, scaleProgress)})`,
        fontFamily: "sans-serif",
        color: "#FFFFFF",
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Background HUD Grid lines */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `linear-gradient(${accentColor}08 1px, transparent 1px), linear-gradient(90deg, ${accentColor}08 1px, transparent 1px)`,
          backgroundSize: "24px 24px",
          pointerEvents: "none",
        }}
      />

      {/* Header bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: `1px solid ${accentColor}33`,
          paddingBottom: 10,
          marginBottom: 16,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: accentColor,
              boxShadow: `0 0 8px ${accentColor}`,
            }}
          />
          <span style={{ fontSize: 13, fontWeight: 900, letterSpacing: 1.5, color: accentColor }}>
            {title}
          </span>
        </div>
        <span style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>
          SPEC v2.6 // DETERMINISTIC CORE
        </span>
      </div>

      {/* Blueprint Architecture Nodes */}
      <div style={{ display: "flex", flexDirection: "column", gap: 14, position: "relative" }}>
        {/* Node 1: AI Brain & Context */}
        <div
          style={{
            background: "rgba(16, 25, 42, 0.9)",
            border: `1px solid ${accentColor}66`,
            borderRadius: 10,
            padding: "10px 14px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#E2E8F0" }}>
              🧠 Ядро Мозку (who_id = 17)
            </div>
            <div style={{ fontSize: 11, color: "#94A3B8" }}>
              Ієрархічний контекст & 429 Hot Standby
            </div>
          </div>
          <span
            style={{
              fontSize: 10,
              background: `${accentColor}22`,
              color: accentColor,
              padding: "2px 8px",
              borderRadius: 4,
              fontWeight: 800,
            }}
          >
            ACTIVE
          </span>
        </div>

        {/* Connector 1 with traveling photon */}
        <div style={{ height: 16, display: "flex", justifyContent: "center", position: "relative" }}>
          <div style={{ width: 2, background: `${accentColor}44`, height: "100%" }} />
          <div
            style={{
              position: "absolute",
              top: `${pulsePhase * 100}%`,
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#FFFFFF",
              boxShadow: `0 0 10px ${accentColor}`,
            }}
          />
        </div>

        {/* Node 2: Gemini 3.8 Live Speech */}
        <div
          style={{
            background: "rgba(25, 20, 38, 0.9)",
            border: "1px solid rgba(168, 85, 247, 0.5)",
            borderRadius: 10,
            padding: "10px 14px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#E2E8F0" }}>
              🎙️ Голосовий Рушій (Gemini 3.8 Live)
            </div>
            <div style={{ fontSize: 11, color: "#C084FC" }}>
              24kHz PCM стрім • Golden Acting Standard
            </div>
          </div>
          <span
            style={{
              fontSize: 10,
              background: "rgba(168, 85, 247, 0.2)",
              color: "#C084FC",
              padding: "2px 8px",
              borderRadius: 4,
              fontWeight: 800,
            }}
          >
            24kHz MONO
          </span>
        </div>

        {/* Connector 2 with traveling photon */}
        <div style={{ height: 16, display: "flex", justifyContent: "center", position: "relative" }}>
          <div style={{ width: 2, background: "rgba(168, 85, 247, 0.4)", height: "100%" }} />
          <div
            style={{
              position: "absolute",
              top: `${pulsePhase * 100}%`,
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#A855F7",
              boxShadow: "0 0 10px #C084FC",
            }}
          />
        </div>

        {/* Node 3: Remotion 9:16 VFX & LipSync */}
        <div
          style={{
            background: "rgba(16, 37, 30, 0.9)",
            border: "1px solid rgba(52, 211, 153, 0.5)",
            borderRadius: 10,
            padding: "10px 14px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#E2E8F0" }}>
              🎬 Автономний Рендер (Remotion 9:16)
            </div>
            <div style={{ fontSize: 11, color: "#6EE7B7" }}>
              Скелетний ліпсінк • Мультимодальна валідація
            </div>
          </div>
          <span
            style={{
              fontSize: 10,
              background: "rgba(52, 211, 153, 0.2)",
              color: "#34D399",
              padding: "2px 8px",
              borderRadius: 4,
              fontWeight: 800,
            }}
          >
            1080x1920
          </span>
        </div>
      </div>

      {/* Footer telemetry status */}
      <div
        style={{
          marginTop: 16,
          paddingTop: 8,
          borderTop: `1px solid ${accentColor}22`,
          display: "flex",
          justifyContent: "space-between",
          fontSize: 10,
          color: "#64748B",
          fontFamily: "monospace",
        }}
      >
        <span>STATUS: 100% PASS</span>
        <span>VALIDATION SCORE: 9.5/10.0</span>
      </div>
    </div>
  );
};
