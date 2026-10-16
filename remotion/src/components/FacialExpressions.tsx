import React from "react";

export type EyeExpression = "neutral" | "happy" | "angry" | "surprised" | "dead" | "wink" | "suspicious" | "wide";
export type MouthExpression = "neutral" | "smile" | "open" | "talking" | "gasp" | "frown" | "smirk";

interface FacialExpressionsProps {
  eyeType?: EyeExpression;
  mouthType?: MouthExpression;
  headRadius?: number;
  color?: string;
  strokeWidth?: number;
  talkingOffset?: number; // 0 to 1 for speech modulation
}

export const FacialExpressions: React.FC<FacialExpressionsProps> = ({
  eyeType = "neutral",
  mouthType = "neutral",
  headRadius = 30,
  color = "#000000",
  strokeWidth = 3,
  talkingOffset = 0,
}) => {
  const eyeY = -headRadius * 0.15;
  const leftEyeX = -headRadius * 0.35;
  const rightEyeX = headRadius * 0.35;
  const mouthY = headRadius * 0.35;

  const renderEyes = () => {
    switch (eyeType) {
      case "dead":
        return (
          <>
            {/* Left X */}
            <line x1={leftEyeX - 4} y1={eyeY - 4} x2={leftEyeX + 4} y2={eyeY + 4} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
            <line x1={leftEyeX - 4} y1={eyeY + 4} x2={leftEyeX + 4} y2={eyeY - 4} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
            {/* Right X */}
            <line x1={rightEyeX - 4} y1={eyeY - 4} x2={rightEyeX + 4} y2={eyeY + 4} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
            <line x1={rightEyeX - 4} y1={eyeY + 4} x2={rightEyeX + 4} y2={eyeY - 4} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
          </>
        );
      case "angry":
        return (
          <>
            <circle cx={leftEyeX} cy={eyeY} r={3} fill={color} />
            <circle cx={rightEyeX} cy={eyeY} r={3} fill={color} />
            <line x1={leftEyeX - 6} y1={eyeY - 7} x2={leftEyeX + 5} y2={eyeY - 3} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
            <line x1={rightEyeX + 6} y1={eyeY - 7} x2={rightEyeX - 5} y2={eyeY - 3} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
          </>
        );
      case "wide":
      case "surprised":
        return (
          <>
            <circle cx={leftEyeX} cy={eyeY} r={5} stroke={color} strokeWidth={strokeWidth} fill="none" />
            <circle cx={rightEyeX} cy={eyeY} r={5} stroke={color} strokeWidth={strokeWidth} fill="none" />
          </>
        );
      case "wink":
        return (
          <>
            <line x1={leftEyeX - 5} y1={eyeY} x2={leftEyeX + 5} y2={eyeY} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
            <circle cx={rightEyeX} cy={eyeY} r={3.5} fill={color} />
          </>
        );
      case "suspicious":
        return (
          <>
            <line x1={leftEyeX - 6} y1={eyeY} x2={leftEyeX + 6} y2={eyeY} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
            <line x1={rightEyeX - 6} y1={eyeY} x2={rightEyeX + 6} y2={eyeY} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
          </>
        );
      case "happy":
        return (
          <>
            <path d={`M ${leftEyeX - 5} ${eyeY + 2} Q ${leftEyeX} ${eyeY - 4} ${leftEyeX + 5} ${eyeY + 2}`} stroke={color} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            <path d={`M ${rightEyeX - 5} ${eyeY + 2} Q ${rightEyeX} ${eyeY - 4} ${rightEyeX + 5} ${eyeY + 2}`} stroke={color} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
          </>
        );
      case "neutral":
      default:
        return (
          <>
            <circle cx={leftEyeX} cy={eyeY} r={3.5} fill={color} />
            <circle cx={rightEyeX} cy={eyeY} r={3.5} fill={color} />
          </>
        );
    }
  };

  const renderMouth = () => {
    switch (mouthType) {
      case "smile":
        return (
          <path
            d={`M ${-headRadius * 0.3} ${mouthY} Q 0 ${mouthY + headRadius * 0.3} ${headRadius * 0.3} ${mouthY}`}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
          />
        );
      case "frown":
        return (
          <path
            d={`M ${-headRadius * 0.3} ${mouthY + 4} Q 0 ${mouthY - 4} ${headRadius * 0.3} ${mouthY + 4}`}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
          />
        );
      case "gasp":
        return (
          <ellipse
            cx={0}
            cy={mouthY}
            rx={headRadius * 0.18}
            ry={headRadius * 0.25}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
          />
        );
      case "smirk":
        return (
          <path
            d={`M ${-headRadius * 0.1} ${mouthY} Q ${headRadius * 0.2} ${mouthY} ${headRadius * 0.35} ${mouthY - 4}`}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
          />
        );
      case "talking":
        const currentOpen = 2 + talkingOffset * 10;
        return (
          <ellipse
            cx={0}
            cy={mouthY}
            rx={headRadius * 0.2}
            ry={currentOpen}
            stroke={color}
            strokeWidth={strokeWidth}
            fill={talkingOffset > 0.3 ? color : "none"}
          />
        );
      case "open":
        return (
          <ellipse
            cx={0}
            cy={mouthY}
            rx={headRadius * 0.22}
            ry={headRadius * 0.18}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
          />
        );
      case "neutral":
      default:
        return (
          <line
            x1={-headRadius * 0.22}
            y1={mouthY}
            x2={headRadius * 0.22}
            y2={mouthY}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
        );
    }
  };

  return (
    <g id="stickman-face">
      {renderEyes()}
      {renderMouth()}
    </g>
  );
};
