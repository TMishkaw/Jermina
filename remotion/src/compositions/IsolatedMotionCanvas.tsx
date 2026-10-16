import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { StickmanRig } from "../components/StickmanRig";
import { AnimationType, EyeExpression, MouthExpression, StickmanPose } from "../components/kinematic_presets";

export interface IsolatedMotionCanvasConfig {
  animation: AnimationType;
  eyeType?: EyeExpression;
  mouthType?: MouthExpression;
  prop?: "microphone" | "sword" | "coffee" | "laptop" | "heart" | "stop_sign" | "watch" | "none";
  emoji?: string | null;
  customPose?: Partial<StickmanPose>;
  accentColor?: string;
  totalFrames?: number;
  audioRms?: number[];
}

export const defaultIsolatedMotionCanvasConfig: IsolatedMotionCanvasConfig = {
  animation: "heart_hands",
  eyeType: "happy",
  mouthType: "smile",
  prop: "none",
  emoji: "❤️",
  accentColor: "#00F0FF",
  totalFrames: 60,
};

/**
 * Isolated Clean Motion Canvas for Live API Audit & A/B Kinematic Review.
 * 
 * Excludes ALL visual noise (no HUD, no subtitles, no particles, no banners)
 * so that Gemini Live API visual evaluation stays 100% focused on character
 * pose, joint kinematics, action readability, and naturalness.
 */
export const IsolatedMotionCanvas: React.FC<{ config?: IsolatedMotionCanvasConfig }> = ({
  config = defaultIsolatedMotionCanvasConfig,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const accentColor = config.accentColor || "#00F0FF";
  const rms = config.audioRms && config.audioRms[frame] !== undefined ? config.audioRms[frame] : 0.05;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#07090E",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      {/* 1. Subtle, clean ground stage reference line */}
      <svg
        style={{
          position: "absolute",
          bottom: 280,
          width: 700,
          height: 120,
          zIndex: 5,
          pointerEvents: "none",
        }}
        viewBox="0 0 700 120"
      >
        <defs>
          <radialGradient id="stageGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={accentColor} stopOpacity="0.30" />
            <stop offset="60%" stopColor={accentColor} stopOpacity="0.06" />
            <stop offset="100%" stopColor="#07090E" stopOpacity="0" />
          </radialGradient>
        </defs>
        <ellipse cx="350" cy="60" rx="300" ry="26" fill="url(#stageGlow)" />
        <line
          x1="60"
          y1="60"
          x2="640"
          y2="60"
          stroke="rgba(255, 255, 255, 0.15)"
          strokeWidth="1.5"
          strokeDasharray="4 4"
        />
      </svg>

      {/* 2. Prominent Isolated Stickman Character (occupies central 75% of viewport) */}
      <svg
        style={{
          width: 1080,
          height: 1920,
          zIndex: 10,
          pointerEvents: "none",
        }}
        viewBox="0 0 1080 1920"
      >
        <StickmanRig
          x={540}
          y={1160}
          scale={2.7}
          animation={config.animation}
          cues={[
            {
              fromFrame: 0,
              durationInFrames: config.totalFrames || 60,
              animation: config.animation,
              eyeType: config.eyeType || "neutral",
              mouthType: config.mouthType || "talking",
              prop: config.prop || "none",
              emoji: config.emoji || null,
              customPose: config.customPose,
            },
          ]}
          audioRms={rms}
          customPose={config.customPose}
          eyeType={config.eyeType || "neutral"}
          mouthType={config.mouthType || "talking"}
          prop={config.prop || "none"}
          emoji={config.emoji || null}
          color="#FFFFFF"
          glowColor={accentColor}
          strokeWidth={6.5}
        />
      </svg>
    </AbsoluteFill>
  );
};
