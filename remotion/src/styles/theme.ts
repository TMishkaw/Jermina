export interface ThemePalette {
  id: string;
  name: string;
  bgBase: string;
  cardSurface: string;
  cardBorder: string;
  textPrimary: string;
  textMuted: string;
  accentGoogle: string;
  accentAnthropic: string; // Violet as requested, easily swappable
  accentOpenAI: string;
  accentVibe: string;
  accentKinetic: string;
  accentLive: string;
}

export const defaultTheme: ThemePalette = {
  id: "cyber_titanium",
  name: "Cyber Titanium & Violet Studio",
  bgBase: "#08090C",
  cardSurface: "rgba(17, 19, 25, 0.88)",
  cardBorder: "rgba(255, 255, 255, 0.08)",
  textPrimary: "#F8FAFC",
  textMuted: "#94A3B8",
  accentGoogle: "#4285F4",
  accentAnthropic: "#A855F7", // Swapped from brown to vibrant violet!
  accentOpenAI: "#10A37F",
  accentVibe: "#06B6D4",
  accentKinetic: "#EEFF04",
  accentLive: "#00F0FF",
};

// Easily swappable alternate themes
export const themePresets: Record<string, ThemePalette> = {
  default: defaultTheme,
  deep_violet: {
    ...defaultTheme,
    accentAnthropic: "#C084FC", // Lighter lilac violet
    accentKinetic: "#F43F5E",
  },
  neon_cyber: {
    ...defaultTheme,
    accentAnthropic: "#9333EA", // Electric purple
    accentGoogle: "#38BDF8",
    accentOpenAI: "#34D399",
  },
};
