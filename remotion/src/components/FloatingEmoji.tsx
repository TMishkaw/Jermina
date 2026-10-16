import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface FloatingEmojiProps {
  emoji?: string;
  fromFrame: number;
  durationInFrames: number;
  x?: number;
  y?: number;
  size?: number;
  accentColor?: string;
}

export const FloatingEmoji: React.FC<FloatingEmojiProps> = ({
  emoji,
  fromFrame,
  durationInFrames,
  x = 670,
  y = 860,
  size = 96,
  accentColor = "#00F0FF",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!emoji || frame < fromFrame || frame >= fromFrame + durationInFrames) {
    return null;
  }

  const localFrame = frame - fromFrame;
  const progress = spring({
    frame: localFrame,
    fps,
    config: { damping: 10, stiffness: 180 },
  });

  // Fade out in last 8 frames
  const fadeOut = interpolate(localFrame, [durationInFrames - 8, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Gentle float hovering and slight rotation
  const hoverY = Math.sin((localFrame / 30) * Math.PI * 2) * 12;
  const hoverRotate = Math.cos((localFrame / 30) * Math.PI * 2) * 8;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y + hoverY,
        transform: `translate(-50%, -50%) scale(${progress}) rotate(${hoverRotate}deg)`,
        opacity: fadeOut,
        fontSize: size,
        zIndex: 28,
        filter: `drop-shadow(0 0 24px ${accentColor}88) drop-shadow(0 0 10px rgba(0,0,0,0.85))`,
        userSelect: "none",
        pointerEvents: "none",
        lineHeight: 1,
      }}
    >
      {emoji}
    </div>
  );
};
