import React from "react";
import { Composition } from "remotion";
import { StickmanShort9x16, defaultStickmanShortConfig } from "./compositions/StickmanShort9x16";
import { CyberStudio16x9, defaultCyberStudio16x9Config } from "./compositions/CyberStudio16x9";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 1. Vertical 9:16 Shorts & TikTok Composition (1080x1920) */}
      <Composition
        id="StickmanShort9x16"
        component={StickmanShort9x16}
        durationInFrames={360}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          config: defaultStickmanShortConfig,
        }}
        calculateMetadata={({ props }) => {
          const frames = (props as { config?: { totalFrames?: number } })?.config?.totalFrames;
          return {
            durationInFrames: frames && frames > 30 ? frames : 360,
          };
        }}
      />

      {/* 2. Horizontal 16:9 Full YouTube Widescreen Composition (1920x1080) */}
      <Composition
        id="CyberStudio16x9"
        component={CyberStudio16x9}
        durationInFrames={360}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          config: defaultCyberStudio16x9Config,
        }}
        calculateMetadata={({ props }) => {
          const frames = (props as { config?: { totalFrames?: number } })?.config?.totalFrames;
          return {
            durationInFrames: frames && frames > 30 ? frames : 360,
          };
        }}
      />
    </>
  );
};
