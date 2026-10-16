import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface KineticHookProps {
  primaryText: string;
  strikeThroughText?: string;
  accentText: string;
  badgeText?: string;
  accentColor?: string;
}

export const KineticHook: React.FC<KineticHookProps> = ({
  primaryText,
  strikeThroughText,
  accentText,
  badgeText = "BREAKING TECH 2026",
  accentColor = "#EEFF04",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const scale = spring({
    frame,
    fps,
    config: { damping: 10, mass: 0.5, stiffness: 220 },
  });

  // Strikethrough laser progress (frames 20 - 45)
  const strikeProgress = interpolate(frame, [15, 35], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Background subtle pulse
  const flashOpacity = interpolate(frame, [0, 5, 12], [0.8, 1, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 40px",
        textAlign: "center",
        position: "relative",
        background: "transparent",
      }}
    >
      {/* Opening strobe flash */}
      {flashOpacity > 0 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "#FFFFFF",
            opacity: flashOpacity,
            pointerEvents: "none",
          }}
        />
      )}

      {/* Semi-transparent Frosted Glass Panel Container */}
      <div
        style={{
          background: "rgba(13, 17, 23, 0.40)", // Напівпрозоре скло 40% згідно із запитом
          backdropFilter: "blur(28px)",
          border: `2px solid ${accentColor}77`,
          borderRadius: 28,
          padding: "44px 36px",
          maxWidth: "960px",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: `0 20px 50px rgba(0,0,0,0.5), 0 0 35px -5px ${accentColor}33`,
          transform: `scale(${scale})`,
        }}
      >
        {/* Top Cyber Badge */}
        <div
          style={{
            fontFamily: "monospace",
            fontSize: 16,
            fontWeight: 800,
            color: accentColor,
            letterSpacing: "0.2em",
            marginBottom: 24,
            padding: "6px 18px",
            border: `1.5px solid ${accentColor}88`,
            borderRadius: 10,
            background: `${accentColor}20`,
            boxShadow: `0 0 15px ${accentColor}44`,
          }}
        >
          {badgeText}
        </div>

        {/* Primary Hook Line */}
        <h1
          style={{
            fontFamily: "Inter, sans-serif",
            fontSize: 54,
            fontWeight: 900,
            lineHeight: 1.15,
            color: "#FFFFFF",
            textTransform: "uppercase",
            letterSpacing: "-0.02em",
            margin: 0,
            textAlign: "center",
          }}
        >
          {primaryText}
        </h1>

        {/* Strikethrough Line if present */}
        {strikeThroughText && (
          <div
            style={{
              position: "relative",
              display: "inline-block",
              marginTop: 20,
            }}
          >
            <span
              style={{
                fontFamily: "Inter, sans-serif",
                fontSize: 44,
                fontWeight: 800,
                color: "#94A3B8",
                textTransform: "uppercase",
                letterSpacing: "-0.02em",
              }}
            >
              {strikeThroughText}
            </span>
            {/* Animated red strike line */}
            <div
              style={{
                position: "absolute",
                top: "52%",
                left: 0,
                width: `${strikeProgress}%`,
                height: 6,
                background: "#EF4444",
                boxShadow: "0 0 18px #EF4444",
                borderRadius: 3,
              }}
            />
          </div>
        )}

        {/* Explosive Accent Punch */}
        <div
          style={{
            fontFamily: "Inter, sans-serif",
            fontSize: 60,
            fontWeight: 900,
            color: accentColor,
            textTransform: "uppercase",
            letterSpacing: "-0.03em",
            marginTop: 24,
            textAlign: "center",
            textShadow: `0 0 35px ${accentColor}88`,
          }}
        >
          {accentText}
        </div>
      </div>
    </div>
  );
};
