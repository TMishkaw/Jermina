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
        border: "1px solid rgba(255, 255, 255, 0.12)",
        borderRadius: 12,
        overflow: "hidden",
        fontFamily: "monospace",
        fontSize: 12,
        boxShadow: "0 15px 35px rgba(0,0,0,0.6)",
      }}
    >
      {/* Title bar */}
      <div
        style={{
          background: "rgba(255, 255, 255, 0.04)",
          padding: "8px 12px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid rgba(255, 255, 255, 0.06)",
        }}
      >
        <div style={{ display: "flex", gap: 6 }}>
          <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#FF5F56" }} />
          <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#FFBD2E" }} />
          <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#27C93F" }} />
        </div>
        <div style={{ color: "#64748B", fontSize: 11 }}>{title}</div>
        <div style={{ width: 36 }} />
      </div>

      {/* Terminal Body */}
      <div style={{ padding: "12px 16px", color: "#E2E8F0", lineHeight: 1.6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, color: accentColor }}>
          <span style={{ color: "#38BDF8" }}>❯</span>
          <span>{command}</span>
          {showCursor && (
            <span
              style={{
                display: "inline-block",
                width: 7,
                height: 14,
                background: accentColor,
              }}
            />
          )}
        </div>

        <div style={{ marginTop: 8, color: "#94A3B8" }}>
          {outputLines.map((line, idx) => (
            <div key={idx} style={{ color: line.startsWith("✓") || line.startsWith(">>>") ? "#34D399" : "#94A3B8" }}>
              {line}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
