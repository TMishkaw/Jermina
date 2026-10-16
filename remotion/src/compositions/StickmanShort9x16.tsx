import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { StickmanRig } from "../components/StickmanRig";
import { KaraokeSubtitles } from "../components/KaraokeSubtitles";
import { CyberParticlesBackground } from "../components/CyberParticlesBackground";
import { AnimationType, EyeExpression, MouthExpression } from "../components/kinematic_presets";

export interface StickmanCue {
  fromFrame: number;
  durationInFrames: number;
  animation: AnimationType;
  eyeType: EyeExpression;
  mouthType: MouthExpression;
  prop?: "microphone" | "sword" | "coffee" | "laptop" | "none";
}

export interface SubtitleCue {
  text: string;
  startFrame: number;
  endFrame: number;
  highlight?: boolean;
}

export interface StickmanShortConfig {
  id: string;
  title: string;
  hookText: string;
  accentColor: string;
  audioSrc?: string;
  stickmanCues: StickmanCue[];
  subtitles: SubtitleCue[];
}

export const defaultStickmanShortConfig: StickmanShortConfig = {
  id: "sample_short_01",
  title: "AI Live Autonomous Production",
  hookText: "СТОП! ВОНИ ЗНОВУ ЗРОБИЛИ ЦЕ?!",
  accentColor: "#00F0FF",
  stickmanCues: [
    { fromFrame: 0, durationInFrames: 60, animation: "surprised", eyeType: "wide", mouthType: "gasp", prop: "none" },
    { fromFrame: 60, durationInFrames: 120, animation: "talk", eyeType: "neutral", mouthType: "talking", prop: "microphone" },
    { fromFrame: 180, durationInFrames: 90, animation: "laugh", eyeType: "happy", mouthType: "smile", prop: "coffee" },
    { fromFrame: 270, durationInFrames: 90, animation: "point_up", eyeType: "wink", mouthType: "smile", prop: "none" },
  ],
  subtitles: [
    { text: "СТОП!", startFrame: 5, endFrame: 25, highlight: true },
    { text: "Вони знову перевернули все догори дриґом...", startFrame: 30, endFrame: 75 },
    { text: "Gemini 3.8 Live синтезує живі емоції без затримок!", startFrame: 80, endFrame: 150, highlight: true },
    { text: "Підписуйся на канал Jemini та пиши код разом з нами!", startFrame: 160, endFrame: 240 },
  ],
};

export const StickmanShort9x16: React.FC<{ config?: StickmanShortConfig }> = ({
  config = defaultStickmanShortConfig,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Find active stickman cue
  const activeCue = config.stickmanCues.find(
    (c) => frame >= c.fromFrame && frame < c.fromFrame + c.durationInFrames
  ) || config.stickmanCues[0];

  // Hook animation for first 60 frames (2 seconds)
  const hookSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  const hookOpacity = interpolate(frame, [50, 65], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#07090E",
        color: "#F8FAFC",
        fontFamily: "'Inter', sans-serif",
        overflow: "hidden",
      }}
    >
      {/* 1. Optional Voice Track */}
      {config.audioSrc && <Audio src={staticFile(config.audioSrc)} />}

      {/* 2. Cyberpunk / Tech Blueprint Grid */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          pointerEvents: "none",
        }}
      />

      {/* 3. Floating Cyber Particles */}
      <CyberParticlesBackground accentColor={config.accentColor} count={24} />

      {/* 4. Giant Ambient Radial Glow */}
      <div
        style={{
          position: "absolute",
          top: "45%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 600,
          height: 600,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${config.accentColor}25 0%, transparent 70%)`,
          filter: "blur(70px)",
          pointerEvents: "none",
        }}
      />

      {/* 5. First 2 Seconds: Golden Acting Standard 3s Hook */}
      {frame < 65 && (
        <div
          style={{
            position: "absolute",
            top: 220,
            left: 60,
            right: 60,
            textAlign: "center",
            opacity: hookOpacity,
            transform: `scale(${hookSpring})`,
            zIndex: 10,
          }}
        >
          <div
            style={{
              display: "inline-block",
              padding: "12px 28px",
              background: "rgba(239, 68, 68, 0.9)",
              color: "#FFF",
              fontWeight: 900,
              fontSize: 44,
              letterSpacing: 2,
              borderRadius: 16,
              boxShadow: "0 0 35px rgba(239, 68, 68, 0.7)",
              textTransform: "uppercase",
            }}
          >
            {config.hookText}
          </div>
        </div>
      )}

      {/* 6. Dynamic 2.5D Stickman Character */}
      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
        }}
        viewBox="0 0 1080 1920"
      >
        <StickmanRig
          x={540}
          y={1050}
          scale={2.2}
          animation={activeCue.animation}
          eyeType={activeCue.eyeType}
          mouthType={activeCue.mouthType}
          prop={activeCue.prop}
          color="#FFFFFF"
          glowColor={config.accentColor}
          strokeWidth={7}
        />
      </svg>

      {/* 7. Kinetic Karaoke Subtitles at bottom center */}
      <div
        style={{
          position: "absolute",
          bottom: 240,
          left: 40,
          right: 40,
          zIndex: 20,
        }}
      >
        <KaraokeSubtitles
          cues={config.subtitles}
          accentColor={config.accentColor}
          variant="shorts"
          style={{ fontSize: 48 }}
        />
      </div>

      {/* 8. Modern Glassmorphic Top Brand Pill */}
      <div
        style={{
          position: "absolute",
          top: 80,
          left: "50%",
          transform: "translateX(-50%)",
          padding: "10px 24px",
          borderRadius: 9999,
          background: "rgba(15, 23, 42, 0.75)",
          backdropFilter: "blur(12px)",
          border: `1px solid ${config.accentColor}55`,
          display: "flex",
          alignItems: "center",
          gap: 12,
          zIndex: 30,
        }}
      >
        <div
          style={{
            width: 12,
            height: 12,
            borderRadius: "50%",
            background: config.accentColor,
            boxShadow: `0 0 12px ${config.accentColor}`,
          }}
        />
        <span style={{ fontSize: 22, fontWeight: 700, letterSpacing: 1.5, color: "#E2E8F0" }}>
          JERMINA • AI STUDIO
        </span>
      </div>
    </AbsoluteFill>
  );
};
