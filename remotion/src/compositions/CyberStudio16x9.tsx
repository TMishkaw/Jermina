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
import { AnimationType, EyeExpression, MouthExpression } from "../components/kinematic_presets";

export interface StickmanCue16x9 {
  fromFrame: number;
  durationInFrames: number;
  animation: AnimationType;
  eyeType: EyeExpression;
  mouthType: MouthExpression;
  prop?: "microphone" | "sword" | "coffee" | "laptop" | "none";
  emoji?: string | null;
  customPose?: Record<string, number>;
}

export interface SubtitleCue16x9 {
  text: string;
  startFrame: number;
  endFrame: number;
  highlight?: boolean;
}

export interface CyberStudio16x9Config {
  id: string;
  title: string;
  hookText: string;
  accentColor: string;
  audioSrc?: string;
  totalFrames?: number;
  audioRms?: number[];
  stickmanCues: StickmanCue16x9[];
  subtitles: SubtitleCue16x9[];
}

export const defaultCyberStudio16x9Config: CyberStudio16x9Config = {
  id: "sample_widescreen_01",
  title: "Jemini Autonomous Video Production Widescreen",
  hookText: "ЯК ШТУЧНИЙ ІНТЕЛЕКТ ПОВНІСТЮ АВТОНОМНО СТВОРЮЄ КОНТЕНТ",
  accentColor: "#00F0FF",
  stickmanCues: [
    { fromFrame: 0, durationInFrames: 60, animation: "surprised", eyeType: "wide", mouthType: "gasp", prop: "none" },
    { fromFrame: 60, durationInFrames: 120, animation: "talk", eyeType: "neutral", mouthType: "talking", prop: "microphone" },
    { fromFrame: 180, durationInFrames: 90, animation: "point_up", eyeType: "neutral", mouthType: "talking", prop: "laptop" },
    { fromFrame: 270, durationInFrames: 90, animation: "laugh", eyeType: "happy", mouthType: "smile", prop: "coffee" },
  ],
  subtitles: [
    { text: "ВІТАЮ В СТУДІЇ JEMINI!", startFrame: 5, endFrame: 35, highlight: true },
    { text: "Сьогодні розбираємо повний цикл автономного продакшну 16:9.", startFrame: 40, endFrame: 95 },
    { text: "Синтез мовлення Gemini 3.8 Live WebSocket, ліпсінк та Form 2-B HUD.", startFrame: 100, endFrame: 175, highlight: true },
    { text: "Підписуйтесь на канал та автоматизуйте створення контенту!", startFrame: 180, endFrame: 260 },
  ],
};

export const CyberStudio16x9: React.FC<{ config?: CyberStudio16x9Config }> = ({
  config = defaultCyberStudio16x9Config,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Find active stickman cue
  const activeCue = config.stickmanCues.find(
    (c) => frame >= c.fromFrame && frame < c.fromFrame + c.durationInFrames
  ) || config.stickmanCues[0];

  // RMS reactivity
  const rms = config.audioRms && config.audioRms[frame] !== undefined ? config.audioRms[frame] : 0.05;

  // Entrance animations
  const studioEntrance = spring({ frame, fps, config: { damping: 14 } });
  const hookOpacity = interpolate(frame, [0, 15, 80, 95], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#06080F",
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        overflow: "hidden",
      }}
    >
      {/* 1. Synced Master Audio Track */}
      {config.audioSrc && (
        <Audio
          src={staticFile(config.audioSrc)}
          volume={1.0}
        />
      )}

      {/* 2. Cyber Matrix Particle Canvas (Widescreen 1920x1080) */}
      <CyberParticlesBackground
        accentColor={config.accentColor}
        density={45}
        speed={1.0}
      />

      {/* 3. Studio Top Header Bar (1920px) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 70,
          background: "linear-gradient(180deg, rgba(10, 14, 26, 0.95) 0%, rgba(10, 14, 26, 0) 100%)",
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 40px",
          zIndex: 30,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#EF4444",
              boxShadow: "0 0 10px #EF4444",
              animation: "pulse 1.5s infinite",
            }}
          />
          <span style={{ color: "#F8FAFC", fontWeight: 800, fontSize: 18, letterSpacing: "0.1em" }}>
            JEMINI BROADCAST // LIVE 16:9
          </span>
          <span
            style={{
              fontSize: 12,
              padding: "3px 8px",
              borderRadius: 4,
              backgroundColor: `${config.accentColor}22`,
              color: config.accentColor,
              border: `1px solid ${config.accentColor}55`,
              fontWeight: 700,
            }}
          >
            4K UHD 60FPS
          </span>
        </div>

        <div style={{ color: "rgba(255,255,255,0.6)", fontSize: 14, fontWeight: 500 }}>
          {config.title.toUpperCase()}
        </div>
      </div>

      {/* 4. Left Zone: Studio Presenter Stage (Stickman Rig) */}
      <div
        style={{
          position: "absolute",
          left: 40,
          top: 90,
          bottom: 120,
          width: 780,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "flex-end",
          zIndex: 15,
        }}
      >
        {/* Audio Reactor Orb behind character */}
        <div style={{ position: "absolute", bottom: 260, zIndex: 5 }}>
          <AudioReactorOrb
            rms={rms}
            accentColor={config.accentColor}
            size={280}
          />
        </div>

        {/* 2.5D Stickman Character */}
        <svg
          style={{
            width: "100%",
            height: "100%",
            zIndex: 10,
            pointerEvents: "none",
          }}
          viewBox="0 0 780 870"
        >
          <StickmanRig
            x={390}
            y={680}
            scale={1.75}
            animation={activeCue.animation}
            customPose={activeCue.customPose}
            eyeType={activeCue.eyeType}
            mouthType={activeCue.mouthType}
            prop={activeCue.prop}
            emoji={activeCue.emoji}
            color="#FFFFFF"
            glowColor={config.accentColor}
            strokeWidth={6}
          />
        </svg>

        {/* Presenter Podium Base */}
        <div
          style={{
            position: "absolute",
            bottom: 40,
            width: 480,
            height: 40,
            background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent)",
            borderRadius: 8,
            borderBottom: `2px solid ${config.accentColor}`,
            boxShadow: `0 10px 30px ${config.accentColor}33`,
            zIndex: 8,
          }}
        />
      </div>

      {/* 5. Right Zone: Interactive Cyber Terminal & Form 2-B HUD Blueprint */}
      <div
        style={{
          position: "absolute",
          right: 60,
          top: 100,
          bottom: 140,
          width: 1000,
          zIndex: 20,
          transform: `scale(${Math.min(1, studioEntrance)})`,
          opacity: Math.min(1, studioEntrance),
        }}
      >
        {/* Kinetic Hook (Frames 0 - 90) */}
        {frame < 95 && (
          <div
            style={{
              position: "absolute",
              top: 40,
              left: 20,
              right: 20,
              opacity: hookOpacity,
              zIndex: 25,
            }}
          >
            <KineticHook
              primaryText="УВАГА!"
              accentText={config.hookText}
              badgeText="AUTONOMOUS 16:9 BROADCAST"
              accentColor={config.accentColor}
            />
          </div>
        )}

        {/* Switch between Terminal (0-180) and Form 2-B Blueprint (180+) */}
        {frame < 190 ? (
          <div style={{ marginTop: 40 }}>
            <TerminalWindow
              title="jemini-core // orchestrator.stream"
              command="python -m jemini.cli render --widescreen --channel stickman_lab"
              outputLines={[
                "✓ Pipeline: 16:9 Widescreen Mode Active (1920x1080 @ 30fps)",
                "✓ Gemini 3.8 Live WebSocket Connected (24kHz Mono PCM)",
                "✓ Key Rotator: key_01 active (Free-tier hot standby ready)",
                "✓ Kinematic Stickman Rig: 2.5D studio presenter engaged",
                "✓ Procedural Audio: whoosh, hit, chime frequency synthesis",
              ]}
              accentColor={config.accentColor}
            />
          </div>
        ) : (
          <div style={{ marginTop: 20 }}>
            <Forma2BBlueprint accentColor={config.accentColor} />
          </div>
        )}
      </div>

      {/* 6. Lower Third Cinematic Karaoke Subtitles (1920px) */}
      <div
        style={{
          position: "absolute",
          bottom: 65,
          left: 100,
          right: 100,
          zIndex: 28,
        }}
      >
        <KaraokeSubtitles
          cues={config.subtitles}
          accentColor={config.accentColor}
          variant="standard"
          style={{ fontSize: 38 }}
        />
      </div>

      {/* 7. Bottom Breaking Live Ticker (Full 1920px Width) */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 44,
          zIndex: 35,
        }}
      >
        <BreakingTicker
          items={[
            "JEMINI AUTONOMOUS STUDIO",
            "16:9 WIDESCREEN & 9:16 SHORTS DUAL ENGINE",
            "GEMINI 3.8 LIVE WEBSOCKET AUDIO",
            "FORM 2-B HUD VECTOR BLUEPRINT",
            "AUTOMATED YOUTUBE & TIKTOK PUBLISHING",
          ]}
          speed={3}
          backgroundColor="#080A10"
          textColor="#F8FAFC"
        />
      </div>
    </AbsoluteFill>
  );
};
