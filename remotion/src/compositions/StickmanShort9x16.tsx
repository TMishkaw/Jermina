import React from "react";
import { AbsoluteFill, Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { StickmanRig } from "../components/StickmanRig";
import { KaraokeSubtitles } from "../components/KaraokeSubtitles";
import { CyberParticlesBackground } from "../components/CyberParticlesBackground";
import { AudioReactorOrb } from "../components/AudioReactorOrb";
import { KineticHook } from "../components/KineticHook";
import { TerminalWindow } from "../components/TerminalWindow";
import { BreakingTicker } from "../components/BreakingTicker";
import { Forma2BBlueprint } from "../components/Forma2BBlueprint";
import { FloatingEmoji } from "../components/FloatingEmoji";
import { AnimationType, EyeExpression, MouthExpression } from "../components/kinematic_presets";

export interface StickmanCue {
  fromFrame: number;
  durationInFrames: number;
  animation: AnimationType;
  eyeType: EyeExpression;
  mouthType: MouthExpression;
  prop?: "microphone" | "sword" | "coffee" | "laptop" | "none";
  emoji?: string;
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
  totalFrames?: number;
  audioRms?: number[];
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
  const activeCue =
    config.stickmanCues.find(
      (c) => frame >= c.fromFrame && frame < c.fromFrame + c.durationInFrames
    ) || config.stickmanCues[0];

  // Current audio energy
  const currentEnergy = config.audioRms && config.audioRms[frame] !== undefined
    ? config.audioRms[frame]
    : 0.15;

  // Hook fadeout after 65 frames
  const hookOpacity = interpolate(frame, [50, 65], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Terminal window slide-in and fade
  const terminalEntrance = spring({
    frame: frame - 70,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  const tickerItems = [
    "JEMINI 2.4.0 ONLINE",
    "GEMINI 3.8 LIVE WEBSOCKET ACTIVE",
    "ZERO LATENCY 24kHz AUDIO",
    "AUTONOMOUS STICKMAN RIG",
    "PGVECTOR MEMORY INDEXED",
  ];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#07090E",
        color: "#F8FAFC",
        fontFamily: "'Inter', sans-serif",
        overflow: "hidden",
      }}
    >
      {/* 1. Audio Track */}
      {config.audioSrc && <Audio src={staticFile(config.audioSrc)} />}

      {/* 2. Cyberpunk Grid */}
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

      {/* 4. Ambient Radial Glow */}
      <div
        style={{
          position: "absolute",
          top: "45%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${config.accentColor}25 0%, transparent 70%)`,
          filter: "blur(80px)",
          pointerEvents: "none",
        }}
      />

      {/* 5. Top Brand Pill */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: "50%",
          transform: "translateX(-50%)",
          padding: "10px 28px",
          borderRadius: 9999,
          background: "rgba(15, 23, 42, 0.85)",
          backdropFilter: "blur(14px)",
          border: `1px solid ${config.accentColor}66`,
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
            boxShadow: `0 0 14px ${config.accentColor}`,
          }}
        />
        <span style={{ fontSize: 22, fontWeight: 800, letterSpacing: 2, color: "#E2E8F0" }}>
          JERMINA • AI STUDIO
        </span>
      </div>

      {/* 6. Audio Reactor Orb (Top Center - Visible in Opening & Outro) */}
      {(frame < 70 || frame >= (config.totalFrames ? config.totalFrames - 45 : 340)) && (
        <div
          style={{
            position: "absolute",
            top: 130,
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 5,
          }}
        >
          <AudioReactorOrb
            color={config.accentColor}
            size={220}
            label="GEMINI 3.8 LIVE"
            statusText="24kHz ACTING STREAM"
            audioEnergy={currentEnergy}
            isSpeaking={currentEnergy > 0.1}
          />
        </div>
      )}

      {/* 7. Opening Kinetic Hook (Frames 0-65) */}
      {frame < 68 && (
        <div
          style={{
            position: "absolute",
            top: 360,
            left: 0,
            right: 0,
            opacity: hookOpacity,
            zIndex: 25,
          }}
        >
          <KineticHook
            primaryText="СТОП!"
            accentText={config.hookText}
            badgeText="AI VIRAL BREAKTHROUGH"
            accentColor={config.accentColor}
          />
        </div>
      )}

      {/* 8. Cyber Terminal Window (Frames 70-220, full size, unscaled readability) */}
      {frame >= 70 && frame < 225 && (
        <div
          style={{
            position: "absolute",
            top: 200,
            left: 40,
            right: 40,
            transform: `translateY(${(1 - Math.min(1, terminalEntrance)) * 30}px)`,
            opacity: Math.min(1, terminalEntrance),
            zIndex: 12,
          }}
        >
          <TerminalWindow
            title="jemini-orchestrator // stream"
            command="python -m jemini.cli render --live"
            outputLines={[
              "✓ KeyRotator acquired: key_01 (Free Hot Standby)",
              "✓ Gemini 3.8 Live WebSocket connected (24kHz PCM)",
              "✓ Stickman Rig: kinematic lip-sync synced",
              "✓ Procedural SFX: whoosh, hit, chime injected",
            ]}
            accentColor={config.accentColor}
          />
        </div>
      )}

      {/* 8.5 Forma 2-B HUD Vector Blueprint (Frames 225+, full scale 1.0, maximum mobile legibility) */}
      {frame >= 225 && frame < (config.totalFrames ? config.totalFrames - 45 : 340) && (
        <div
          style={{
            position: "absolute",
            top: 200,
            left: 40,
            right: 40,
            zIndex: 12,
          }}
        >
          <Forma2BBlueprint accentColor={config.accentColor} />
        </div>
      )}

      {/* 8.8 Presenter Holographic Platform (Feet anchor line above subtitles) */}
      <div
        style={{
          position: "absolute",
          top: 1590,
          left: 200,
          right: 200,
          height: 3,
          background: `linear-gradient(90deg, transparent, ${config.accentColor}99 30%, ${config.accentColor} 50%, ${config.accentColor}99 70%, transparent)`,
          boxShadow: `0 0 16px ${config.accentColor}`,
          zIndex: 20,
        }}
      />

      {/* 9. Dynamic 2.5D Stickman Character (Presenter Foreground Layer: zIndex 25) */}
      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
          zIndex: 25,
        }}
        viewBox="0 0 1080 1920"
      >
        <StickmanRig
          x={540}
          y={1400}
          scale={1.8}
          animation={activeCue.animation}
          customPose={activeCue.customPose}
          eyeType={activeCue.eyeType}
          mouthType={activeCue.mouthType}
          prop={activeCue.prop}
          color="#FFFFFF"
          glowColor={config.accentColor}
          strokeWidth={7}
        />
      </svg>

      {/* 9.5 Floating Semantic Emoji (Reactive to spoken topic) */}
      {activeCue.emoji && (
        <FloatingEmoji
          emoji={activeCue.emoji}
          fromFrame={activeCue.fromFrame}
          durationInFrames={activeCue.durationInFrames}
          x={720}
          y={1040}
          size={110}
          accentColor={config.accentColor}
        />
      )}

      {/* 10. Kinetic Karaoke Subtitles */}
      <div
        style={{
          position: "absolute",
          bottom: 220,
          left: 40,
          right: 40,
          zIndex: 25,
        }}
      >
        <KaraokeSubtitles
          cues={config.subtitles}
          accentColor={config.accentColor}
          variant="shorts"
          style={{ fontSize: 46 }}
        />
      </div>

      {/* 11. Breaking Live Ticker (Bottom Bar) */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 35,
        }}
      >
        <BreakingTicker
          items={tickerItems}
          speed={4}
          backgroundColor="#080A10"
          textColor="#F8FAFC"
        />
      </div>
    </AbsoluteFill>
  );
};
