import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SubtitleCue } from "../types/presets";

interface KaraokeSubtitlesProps {
  cues: SubtitleCue[];
  accentColor?: string;
  variant?: "shorts" | "widescreen";
  style?: React.CSSProperties;
  currentFrame?: number;
}

export const KaraokeSubtitles: React.FC<KaraokeSubtitlesProps> = ({
  cues,
  accentColor = "#EEFF04",
  variant = "shorts",
  style = {},
  currentFrame,
}) => {
  const remotionFrame = useCurrentFrame();
  const frame = typeof currentFrame === "number" ? currentFrame : remotionFrame;
  const { fps } = useVideoConfig();

  // Find active subtitle cue
  const activeCue = cues.find(
    (c) => frame >= c.startFrame && frame <= c.endFrame
  );

  if (!activeCue) {
    return null;
  }

  const duration = Math.max(1, activeCue.endFrame - activeCue.startFrame);
  const elapsed = frame - activeCue.startFrame;

  // Spring entrance for new cue
  const pop = spring({
    frame: elapsed,
    fps,
    config: { damping: 14, mass: 0.5, stiffness: 200 },
  });

  const words = activeCue.text.split(" ");
  let currentWordIndex = -1;

  if (activeCue.wordTimings && activeCue.wordTimings.length > 0) {
    // Exact word timestamp match
    const foundIdx = activeCue.wordTimings.findIndex(
      (wt) => frame >= wt.startFrame && frame <= wt.endFrame
    );
    if (foundIdx !== -1) {
      currentWordIndex = foundIdx;
    } else {
      // Find the latest word that has started
      const lastStartedIdx = activeCue.wordTimings.findLastIndex(
        (wt) => frame >= wt.startFrame
      );
      currentWordIndex = lastStartedIdx !== -1 ? lastStartedIdx : 0;
    }
  } else {
    // Proportional fallback
    const wordDuration = duration / words.length;
    currentWordIndex = Math.min(
      words.length - 1,
      Math.floor(elapsed / wordDuration)
    );
  }

  const isShorts = variant === "shorts";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        padding: isShorts ? "0 24px" : "0 32px",
        zIndex: 50,
        pointerEvents: "none",
        ...style,
      }}
    >
      <div
        style={{
          background: "rgba(8, 9, 12, 0.92)",
          backdropFilter: "blur(20px)",
          border: `1px solid ${accentColor}55`,
          boxShadow: `0 10px 30px rgba(0,0,0,0.8), 0 0 20px -5px ${accentColor}33`,
          borderRadius: isShorts ? 18 : 14,
          padding: isShorts ? "20px 32px" : "12px 28px",
          maxWidth: isShorts ? "96%" : "85%",
          textAlign: "center",
          transform: `scale(${pop})`,
          transition: "transform 0.05s ease-out",
        }}
      >
        <p
          style={{
            margin: 0,
            fontSize: isShorts ? 36 : 20,
            fontWeight: 800,
            lineHeight: 1.35,
            fontFamily: "Inter, sans-serif",
            letterSpacing: "-0.01em",
            color: "#FFFFFF",
          }}
        >
          {words.map((word, idx) => {
            const isActive = idx === currentWordIndex;
            const isHighlighted =
              activeCue.highlightWords?.some((h) =>
                word.toLowerCase().includes(h.toLowerCase())
              ) ?? false;

            let wordColor = "#FFFFFF";
            let shadow = "none";
            let scale = 1;

            if (isActive) {
              wordColor = accentColor;
              shadow = `0 0 15px ${accentColor}`;
              scale = 1.08;
            } else if (isHighlighted) {
              wordColor = "#38BDF8";
            }

            return (
              <span
                key={idx}
                style={{
                  display: "inline-block",
                  color: wordColor,
                  textShadow: shadow,
                  transform: `scale(${scale})`,
                  margin: "0 4px",
                  transition: "color 0.1s ease, transform 0.1s ease",
                }}
              >
                {word}
              </span>
            );
          })}
        </p>
      </div>
    </div>
  );
};
