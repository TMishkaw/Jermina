import React from "react";
import { useCurrentFrame } from "remotion";
import { DigestBinding } from "../types/presets";

interface DigestBindingBadgeProps {
  binding: DigestBinding;
  accentColor?: string;
}

export const DigestBindingBadge: React.FC<DigestBindingBadgeProps> = ({
  binding,
  accentColor = "#38BDF8",
}) => {
  const frame = useCurrentFrame();
  const pulse = Math.sin(frame * 0.1) * 0.05 + 1;

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        background: "rgba(15, 23, 42, 0.9)",
        border: `1px solid ${accentColor}66`,
        borderRadius: 30,
        padding: "6px 16px",
        boxShadow: `0 4px 15px rgba(0,0,0,0.5), 0 0 12px -3px ${accentColor}44`,
        transform: `scale(${pulse})`,
        transition: "transform 0.05s ease-out",
      }}
    >
      {/* Red Dot / Link Icon */}
      <div
        style={{
          width: 8,
          height: 8,
          borderRadius: "50%",
          background: "#EF4444",
          boxShadow: "0 0 8px #EF4444",
        }}
      />

      <span
        style={{
          fontFamily: "monospace",
          fontSize: 11,
          fontWeight: 800,
          color: "#F8FAFC",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
        }}
      >
        {binding.digestTitle} • ЧАСТИНА {binding.partNumber}/{binding.totalParts}
      </span>

      <span
        style={{
          fontSize: 12,
          color: accentColor,
          fontWeight: 800,
        }}
      >
        ↗
      </span>
    </div>
  );
};
