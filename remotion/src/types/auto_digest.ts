import { SubtitleCue } from "./presets";

export interface AutoDigestTopic {
  id: string;
  categoryTag: string;
  topicLabel: string;
  accentColor: string;
  audioFile: string;
  startFrame: number;
  durationInFrames: number;
  heroCard: {
    category: string;
    title: string;
    subtitle: string;
    description: string;
    metric: {
      label: string;
      value: string;
    };
  };
  cardA: {
    category: string;
    title: string;
    description: string;
    metric: {
      label: string;
      value: string;
    };
  };
  cardB: {
    category: string;
    title: string;
    description: string;
    metric: {
      label: string;
      value: string;
    };
  };
}

export interface AutoDigestProps {
  digestId: number;
  episodeNumber: string;
  dateString: string;
  tickerItems: string[];
  totalFrames: number;
  topics: AutoDigestTopic[];
  subtitles: SubtitleCue[];
  audioRms: number[];
}
