import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { MetricData } from "../types/digest";

interface BentoCardProps {
  category: string;
  title: string;
  subtitle?: string;
  description: string;
  accentColor: string;
  delayFrames?: number;
  metric?: MetricData;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}

export const BentoCard: React.FC<BentoCardProps> = ({
  category,
  title,
  subtitle,
  description,
  accentColor,
  delayFrames = 0,
  metric,
  style = {},
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delayFrames,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 120 },
  });

  const translateY = interpolate(progress, [0, 1], [35, 0]);
  const opacity = interpolate(progress, [0, 1], [0, 1]);
  const scale = interpolate(progress, [0, 1], [0.95, 1]);

  return (
    <div
      style={{
        transform: `translateY(${translateY}px) scale(${scale})`,
        opacity,
        background: "rgba(17, 19, 25, 0.88)",
        backdropFilter: "blur(24px)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 24,
        color: "#F8FAFC",
        fontFamily: "Inter, sans-serif",
        boxShadow: `0 20px 40px -15px rgba(0,0,0,0.7), 0 0 25px -10px ${accentColor}33`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        position: "relative",
        overflow: "hidden",
        ...style,
      }}
    >
      {/* Top Subtle Brand Gradient Line */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 3,
          background: `linear-gradient(90deg, ${accentColor} 0%, transparent 100%)`,
        }}
      />

      {/* Header with Category Tag and Optional Metric */}
      <div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 12,
          }}
        >
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              padding: "4px 10px",
              borderRadius: 6,
              background: `${accentColor}1A`,
              color: accentColor,
              border: `1px solid ${accentColor}44`,
            }}
          >
            {category}
          </span>

          {metric && (
            <div
              style={{
                fontFamily: "monospace",
                fontSize: 13,
                color: "#94A3B8",
                background: "rgba(255, 255, 255, 0.05)",
                padding: "4px 10px",
                borderRadius: 8,
                border: "1px solid rgba(255, 255, 255, 0.06)",
              }}
            >
              <span>{metric.label}: </span>
              <strong style={{ color: "#F8FAFC", fontWeight: 700 }}>
                {metric.value}
              </strong>
            </div>
          )}
        </div>

        {subtitle && (
          <div
            style={{
              fontSize: 15,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "#94A3B8",
              marginBottom: 6,
            }}
          >
            {subtitle}
          </div>
        )}

        <h3
          style={{
            fontSize: 32,
            fontWeight: 800,
            lineHeight: 1.25,
            margin: "0 0 14px 0",
            letterSpacing: "-0.02em",
            color: "#FFFFFF",
          }}
        >
          {title}
        </h3>

        <p
          style={{
            fontSize: 20,
            lineHeight: 1.5,
            color: "#CBD5E1",
            margin: 0,
          }}
        >
          {description}
        </p>
      </div>

      {children && <div style={{ marginTop: 14 }}>{children}</div>}
    </div>
  );
};
