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
        borderRadius: 20,
        padding: "16px 22px",
        boxShadow: `0 20px 40px rgba(0,0,0,0.7), inset 0 0 25px ${accentColor}18`,
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
          paddingBottom: 12,
          marginBottom: 14,
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
          <span style={{ fontSize: 28, fontWeight: 900, letterSpacing: 1.5, color: accentColor }}>
            {title}
          </span>
        </div>
        <span style={{ fontSize: 20, color: "#CBD5E1", fontFamily: "monospace", fontWeight: 700 }}>
          SPEC v2.6 // CORE
        </span>
      </div>

      {/* Blueprint Architecture Nodes */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10, position: "relative" }}>
        {/* Node 1: AI Brain & Context */}
        <div
          style={{
            background: "rgba(16, 25, 42, 0.95)",
            border: `1.5px solid ${accentColor}77`,
            borderRadius: 14,
            padding: "14px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#FFFFFF", marginBottom: 2 }}>
              🧠 Ядро Мозку (who_id = 17)
            </div>
            <div style={{ fontSize: 19, color: "#CBD5E1", fontWeight: 600 }}>
              Ієрархічний контекст & 429 Hot Standby
            </div>
          </div>
          <span
            style={{
              fontSize: 17,
              background: `${accentColor}25`,
              color: accentColor,
              padding: "5px 14px",
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
        <div style={{ height: 12, display: "flex", justifyContent: "center", position: "relative" }}>
          <div style={{ width: 3, background: `${accentColor}55`, height: "100%" }} />
          <div
            style={{
              position: "absolute",
              top: `${pulsePhase * 100}%`,
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#FFFFFF",
              boxShadow: `0 0 12px ${accentColor}`,
            }}
          />
        </div>

        {/* Node 2: Gemini 3.8 Live Speech */}
        <div
          style={{
            background: "rgba(25, 20, 38, 0.95)",
            border: "1.5px solid rgba(168, 85, 247, 0.7)",
            borderRadius: 14,
            padding: "14px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#FFFFFF", marginBottom: 2 }}>
              🎙️ Голосовий Рушій (Gemini 3.8 Live)
            </div>
            <div style={{ fontSize: 19, color: "#E9D5FF", fontWeight: 600 }}>
              24kHz PCM стрім • Golden Acting Standard
            </div>
          </div>
          <span
            style={{
              fontSize: 17,
              background: "rgba(168, 85, 247, 0.25)",
              color: "#E9D5FF",
              padding: "5px 14px",
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
        <div style={{ height: 12, display: "flex", justifyContent: "center", position: "relative" }}>
          <div style={{ width: 3, background: "rgba(168, 85, 247, 0.5)", height: "100%" }} />
          <div
            style={{
              position: "absolute",
              top: `${pulsePhase * 100}%`,
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#C084FC",
              boxShadow: "0 0 12px #C084FC",
            }}
          />
        </div>

        {/* Node 3: Remotion 9:16 VFX & LipSync */}
        <div
          style={{
            background: "rgba(16, 37, 30, 0.95)",
            border: "1.5px solid rgba(52, 211, 153, 0.7)",
            borderRadius: 14,
            padding: "14px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#FFFFFF", marginBottom: 2 }}>
              🎬 Автономний Рендер (Remotion 9:16)
            </div>
            <div style={{ fontSize: 19, color: "#BBF7D0", fontWeight: 600 }}>
              Скелетний ліпсінк • Мультимодальна валідація
            </div>
          </div>
          <span
            style={{
              fontSize: 17,
              background: "rgba(52, 211, 153, 0.25)",
              color: "#BBF7D0",
              padding: "5px 14px",
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
          marginTop: 14,
          paddingTop: 10,
          borderTop: `2px solid ${accentColor}25`,
          display: "flex",
          justifyContent: "space-between",
          fontSize: 16,
          color: "#94A3B8",
          fontFamily: "monospace",
          fontWeight: 700,
        }}
      >
        <span>NODE: #17 CORE ARCHITECTURE</span>
        <span>STREAM: 24kHz PCM // LIVE</span>
      </div>
    </div>
  );
};
