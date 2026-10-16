export interface WordTiming {
  word: string;
  startFrame: number;
  endFrame: number;
}

export interface SubtitleCue {
  startFrame: number;
  endFrame: number;
  text: string;
  highlightWords?: string[];
  wordTimings?: WordTiming[];
}

export interface DigestBinding {
  digestId: string; // e.g. "EP01"
  digestTitle: string; // e.g. "JERMINA TECH DIGEST #01"
  partNumber: number; // e.g. 1
  totalParts: number; // e.g. 4
  ctaText?: string; // e.g. "Дивись повний розбір у випуску #01"
  badgeColor?: string;
}

export type ScenePresetType =
  | "preset_hook"
  | "preset_headline"
  | "preset_terminal"
  | "preset_metric"
  | "preset_outro";

export interface PresetScene {
  id: string;
  type: ScenePresetType;
  startFrame: number;
  durationInFrames: number;
  title?: string;
  subtitle?: string;
  description?: string;
  spokenNarration: string;
  subtitles: SubtitleCue[];
  accentColor?: string;
  dataPayload?: Record<string, any>;
}

export interface BentoCardData {
  category: string;
  title: string;
  description: string;
  metric?: {
    label: string;
    value: string;
  };
}

export interface StructuredShortsConfig {
  id: string;
  title: string;
  audioSrc: string;
  totalDurationFrames: number;
  accentColor: string;
  parentDigest: DigestBinding;
  scenes?: PresetScene[];
  bentoCard?: BentoCardData;
  subtitles?: SubtitleCue[];
  audioRms?: number[];
  dateString?: string;
}
