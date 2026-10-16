import React from "react";
import { useCurrentFrame } from "remotion";

interface BreakingTickerProps {
  items: string[];
  speed?: number; // pixels per frame
  backgroundColor?: string;
  textColor?: string;
}

export const BreakingTicker: React.FC<BreakingTickerProps> = ({
  items,
  speed = 3.5,
  backgroundColor = "#07080C",
  textColor = "#F8FAFC",
}) => {
  const frame = useCurrentFrame();

  const fullText = items.join("   ///   ");
  // Infinite looping translation calculation
  const offset = (frame * speed) % 2400;

  return (
    <div
      style={{
        width: "100%",
        height: 48,
        backgroundColor,
        borderTop: "1px solid rgba(255, 255, 255, 0.08)",
        display: "flex",
        alignItems: "center",
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Red 'LIVE TICKER' badge on left */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          background: "#EF4444",
          color: "#FFFFFF",
          padding: "0 16px",
          height: "100%",
          fontFamily: "monospace",
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: "0.1em",
          zIndex: 10,
          boxShadow: "10px 0 20px rgba(0,0,0,0.8)",
        }}
      >
        <div
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            backgroundColor: "#FFFFFF",
            boxShadow: "0 0 6px #FFFFFF",
          }}
        />
        BREAKING
      </div>

      {/* Marquee Content */}
      <div
        style={{
          display: "flex",
          whiteSpace: "nowrap",
          transform: `translateX(-${offset}px)`,
          fontFamily: "monospace",
          fontSize: 13,
          fontWeight: 600,
          letterSpacing: "0.06em",
          color: textColor,
          paddingLeft: 40,
        }}
      >
        <span>{fullText}</span>
        <span style={{ marginLeft: 60 }}>{fullText}</span>
      </div>
    </div>
  );
};
