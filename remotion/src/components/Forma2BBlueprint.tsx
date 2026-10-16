import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

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
        border: `2px solid ${accentColor}66`,
        borderRadius: 24,
        padding: "26px 30px",
        boxShadow: `0 24px 48px rgba(0,0,0,0.7), inset 0 0 25px ${accentColor}18`,
        transform: `scale(${Math.min(1, scaleProgress)})`,
        fontFamily: "'Inter', sans-serif",
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
          backgroundSize: "32px 32px",
          pointerEvents: "none",
        }}
      />

      {/* Header bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: `2px solid ${accentColor}33`,
          paddingBottom: 16,
          marginBottom: 20,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: "50%",
              background: accentColor,
              boxShadow: `0 0 14px ${accentColor}`,
            }}
          />
          <span style={{ fontSize: 26, fontWeight: 900, letterSpacing: 1.5, color: accentColor }}>
            {title}
          </span>
        </div>
        <span style={{ fontSize: 18, color: "#94A3B8", fontFamily: "monospace", fontWeight: 700 }}>
          SPEC v2.6 // CORE
        </span>
      </div>

      {/* Blueprint Architecture Nodes */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16, position: "relative" }}>
        {/* Node 1: AI Brain & Context */}
        <div
          style={{
            background: "rgba(16, 25, 42, 0.92)",
            border: `1.5px solid ${accentColor}66`,
            borderRadius: 14,
            padding: "16px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#F8FAFC", marginBottom: 4 }}>
              🧠 Ядро Мозку (who_id = 17)
            </div>
            <div style={{ fontSize: 20, color: "#94A3B8", fontWeight: 500 }}>
              Ієрархічний контекст & 429 Hot Standby
            </div>
          </div>
          <span
            style={{
              fontSize: 18,
              background: `${accentColor}25`,
              color: accentColor,
              padding: "6px 14px",
              borderRadius: 8,
              fontWeight: 800,
              letterSpacing: 1,
              border: `1px solid ${accentColor}55`,
            }}
          >
            ACTIVE
          </span>
        </div>

        {/* Connector 1 with traveling photon */}
        <div style={{ height: 18, display: "flex", justifyContent: "center", position: "relative" }}>
          <div style={{ width: 3, background: `${accentColor}55`, height: "100%" }} />
          <div
            style={{
              position: "absolute",
              top: `${pulsePhase * 100}%`,
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: "#FFFFFF",
              boxShadow: `0 0 14px ${accentColor}`,
            }}
          />
        </div>

        {/* Node 2: Gemini 3.8 Live Speech */}
        <div
          style={{
            background: "rgba(25, 20, 38, 0.92)",
            border: "1.5px solid rgba(168, 85, 247, 0.6)",
            borderRadius: 14,
            padding: "16px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#F8FAFC", marginBottom: 4 }}>
              🎙️ Голосовий Рушій (Gemini 3.8 Live)
            </div>
            <div style={{ fontSize: 20, color: "#D8B4FE", fontWeight: 500 }}>
              24kHz PCM стрім • Golden Acting Standard
            </div>
          </div>
          <span
            style={{
              fontSize: 18,
              background: "rgba(168, 85, 247, 0.25)",
              color: "#D8B4FE",
              padding: "6px 14px",
              borderRadius: 8,
              fontWeight: 800,
              letterSpacing: 1,
              border: "1px solid rgba(168, 85, 247, 0.5)",
            }}
          >
            24kHz MONO
          </span>
        </div>

        {/* Connector 2 with traveling photon */}
        <div style={{ height: 18, display: "flex", justifyContent: "center", position: "relative" }}>
          <div style={{ width: 3, background: "rgba(168, 85, 247, 0.5)", height: "100%" }} />
          <div
            style={{
              position: "absolute",
              top: `${pulsePhase * 100}%`,
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: "#C084FC",
              boxShadow: "0 0 14px #C084FC",
            }}
          />
        </div>

        {/* Node 3: Remotion 9:16 VFX & LipSync */}
        <div
          style={{
            background: "rgba(16, 37, 30, 0.92)",
            border: "1.5px solid rgba(52, 211, 153, 0.6)",
            borderRadius: 14,
            padding: "16px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#F8FAFC", marginBottom: 4 }}>
              🎬 Автономний Рендер (Remotion 9:16)
            </div>
            <div style={{ fontSize: 20, color: "#86EFAC", fontWeight: 500 }}>
              Скелетний ліпсінк • Мультимодальна валідація
            </div>
          </div>
          <span
            style={{
              fontSize: 18,
              background: "rgba(52, 211, 153, 0.25)",
              color: "#86EFAC",
              padding: "6px 14px",
              borderRadius: 8,
              fontWeight: 800,
              letterSpacing: 1,
              border: "1px solid rgba(52, 211, 153, 0.5)",
            }}
          >
            1080x1920
          </span>
        </div>
      </div>

      {/* Footer telemetry status */}
      <div
        style={{
          marginTop: 20,
          paddingTop: 12,
          borderTop: `2px solid ${accentColor}25`,
          display: "flex",
          justifyContent: "space-between",
          fontSize: 18,
          color: "#94A3B8",
          fontFamily: "monospace",
          fontWeight: 700,
        }}
      >
        <span>STATUS: 100% PASS</span>
        <span>VALIDATION SCORE: 9.5/10.0</span>
      </div>
    </div>
  );
};
