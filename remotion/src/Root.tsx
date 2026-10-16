import React from "react";
import { Composition } from "remotion";
import { StickmanShort9x16, defaultStickmanShortConfig } from "./compositions/StickmanShort9x16";

export const RemotionRoot: React.FC = () => {
  return (
    <>
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
      />
    </>
  );
};
