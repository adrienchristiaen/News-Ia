import React from "react";
import { Composition } from "remotion";
import { WeeklyShort } from "./WeeklyShort";
import { FPS, H, W } from "./theme";
import type { VideoProps } from "./types";
import demoEpisode from "../../episodes/demo-w00/episode.json";
import demoTiming from "../../episodes/demo-w00/timing.json";

const defaultProps = { episode: demoEpisode, timing: demoTiming, audioFile: null } as unknown as VideoProps;

export const Root: React.FC = () => (
  <Composition
    id="WeeklyShort"
    component={WeeklyShort}
    width={W}
    height={H}
    fps={FPS}
    durationInFrames={FPS * 60}
    defaultProps={defaultProps}
    calculateMetadata={({ props }) => ({
      durationInFrames: Math.ceil((props.timing.duration + 0.8) * FPS),
    })}
  />
);
