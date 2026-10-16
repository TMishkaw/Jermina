export interface MetricData {
  label: string;
  value: string;
  trend?: "up" | "down" | "neutral";
}

export interface NewsTopic {
  id: string;
  category: string;
  brandColor: string;
  title: string;
  subtitle: string;
  description: string;
  codeSnippet?: string;
  metric?: MetricData;
  secondaryInfo?: string;
}

export interface DigestConfig {
  episodeNumber: number;
  seriesTitle: string;
  breakingNews: string[];
  topics: NewsTopic[];
}
