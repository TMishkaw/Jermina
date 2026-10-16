import React from "react";
import { useCurrentFrame } from "remotion";

interface TerminalWindowProps {
  title?: string;
  command: string;
  outputLines: string[];
  accentColor?: string;
}

export const TerminalWindow: React.FC<TerminalWindowProps> = ({
  title = "bash - 80x24",
  command,
  outputLines,
  accentColor = "#00F0FF",
}) => {
  const frame = useCurrentFrame();
  const showCursor = Math.floor(frame / 15) % 2 === 0;

  return (
    <div
      style={{
        background: "rgba(9, 11, 16, 0.95)",
        border: "1.5px solid rgba(255, 255, 255, 0.16)",
        borderRadius: 18,
        overflow: "hidden",
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        fontSize: 22,
        boxShadow: "0 20px 45px rgba(0,0,0,0.7)",
      }}
    >
      {/* Title bar */}
      <div
        style={{
          background: "rgba(255, 255, 255, 0.05)",
          padding: "14px 20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1.5px solid rgba(255, 255, 255, 0.08)",
        }}
      >
        <div style={{ display: "flex", gap: 10 }}>
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#FF5F56" }} />
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#FFBD2E" }} />
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#27C93F" }} />
        </div>
        <div style={{ color: "#94A3B8", fontSize: 18, fontWeight: 600 }}>{title}</div>
        <div style={{ width: 42 }} />
      </div>

      {/* Terminal Body */}
      <div style={{ padding: "20px 24px", color: "#F1F5F9", lineHeight: 1.6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, color: accentColor, fontWeight: 700 }}>
          <span style={{ color: "#38BDF8" }}>❯</span>
          <span>{command}</span>
          {showCursor && (
            <span
              style={{
                display: "inline-block",
                width: 10,
                height: 22,
                background: accentColor,
              }}
            />
          )}
        </div>

        <div style={{ marginTop: 12, color: "#CBD5E1" }}>
          {outputLines.map((line, idx) => (
            <div
              key={idx}
              style={{
                color: line.startsWith("✓") || line.startsWith(">>>") ? "#34D399" : "#CBD5E1",
                marginBottom: 6,
                fontWeight: 500,
              }}
            >
              {line}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
