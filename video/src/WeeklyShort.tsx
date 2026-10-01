import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import "@fontsource/playfair-display/700.css";
import "@fontsource/playfair-display/900.css";
import "@fontsource/im-fell-english-sc/400.css";
import "@fontsource/source-serif-4/400.css";
import "@fontsource/source-serif-4/400-italic.css";
import "@fontsource/source-serif-4/700.css";
import { B, C, FONT, H, SAFE, W } from "./theme";
import type { Segment, VideoProps } from "./types";
import { Paper } from "./components/Paper";
import { Masthead } from "./components/Masthead";
import { Engraving } from "./components/Engraving";
import { Captions } from "./components/Captions";
import { Headline, Kicker, ProgressBar, SourceChip, StatBadge } from "./components/Bits";

const LEAD = 6; // la scène apparaît 6 images avant le premier mot

const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      position: "absolute",
      left: SAFE.side,
      width: W - 2 * SAFE.side,
      top: 330,
      height: H - SAFE.bottom - 330 - 330 - 10,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "flex-start",
      gap: 26,
    }}
  >
    {children}
  </div>
);

const SegmentScene: React.FC<{ s: Segment }> = ({ s }) => {
  const pubs = Array.from(new Set(s.sources.map((x) => x.publisher))).slice(0, 2).join(" · ");
  return (
    <>
      <Stage>
        {s.kicker && <Kicker text={s.kicker} />}
        <Headline text={s.headline} />
        <div style={{ position: "relative", marginTop: 6 }}>
          <Engraving visual={s.visual} seed={s.id + s.headline} width={W - 2 * SAFE.side - 30} height={s.stat ? 330 : 380} />
          {s.stat && (
            <div style={{ position: "absolute", right: -6, top: 150 }}>
              <StatBadge value={s.stat.value} label={s.stat.label} />
            </div>
          )}
        </div>
      </Stage>
      {pubs && <SourceChip publisher={pubs} />}
    </>
  );
};

const HookScene: React.FC<{ title: string; kickers: string[] }> = ({ title, kickers }) => (
  <Stage>
    <Kicker text="À LA UNE CETTE SEMAINE" />
    <Headline text={title} />
    <div style={{ display: "flex", flexWrap: "wrap", gap: 14, justifyContent: "center", marginTop: 12 }}>
      {kickers.map((k) => (
        <span key={k} style={{ fontFamily: FONT.caps, fontSize: 36, letterSpacing: 3, border: `3px solid ${C.ink}`, padding: "6px 22px", color: C.ink }}>
          {k}
        </span>
      ))}
    </div>
    <div style={{ marginTop: 10 }}>
      <Engraving seed={title} width={W - 2 * SAFE.side - 30} height={250} />
    </div>
  </Stage>
);

const OutroScene: React.FC = () => (
  <Stage>
    <Kicker text="À LA SEMAINE PROCHAINE" />
    <Headline text={B.cta} />
    <div style={{ fontFamily: FONT.caps, fontSize: 64, color: C.accent, marginTop: 24 }}>{B.handle}</div>
    <div style={{ marginTop: 30 }}>
      <Engraving seed="outro" width={W - 2 * SAFE.side - 30} height={260} />
    </div>
  </Stage>
);

export const WeeklyShort: React.FC<VideoProps> = ({ episode, timing, audioFile }) => {
  const { fps, durationInFrames } = useVideoConfig();
  const byId = new Map(episode.segments.map((s) => [s.id, s]));
  const units = timing.units;
  return (
    <AbsoluteFill>
      <Paper>
        <Masthead number={episode.number} date={episode.date} />
        {units.map((u, i) => {
          const from = Math.max(0, Math.round(u.start * fps) - (i === 0 ? 0 : LEAD));
          const next = units[i + 1];
          const to = next ? Math.round(next.start * fps) - LEAD : durationInFrames;
          const body =
            u.id === "hook" ? (
              <HookScene title={episode.title} kickers={episode.segments.map((s) => s.kicker ?? "").filter(Boolean)} />
            ) : u.id === "outro" ? (
              <OutroScene />
            ) : byId.get(u.id) ? (
              <SegmentScene s={byId.get(u.id)!} />
            ) : null;
          return (
            <Sequence key={u.id} from={from} durationInFrames={Math.max(1, to - from)} name={u.id}>
              {body}
            </Sequence>
          );
        })}
        <Captions words={timing.words} />
        <ProgressBar total={durationInFrames} />
      </Paper>
      {audioFile ? <Audio src={staticFile(audioFile)} /> : null}
    </AbsoluteFill>
  );
};
