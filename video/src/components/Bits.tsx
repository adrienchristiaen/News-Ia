import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT, SAFE, W, H } from "../theme";

export const Kicker: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ fontFamily: FONT.caps, fontSize: 40, letterSpacing: 6, color: C.accent, textAlign: "center" }}>
    — {text} —
  </div>
);

export const Headline: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 200 } });
  return (
    <div
      style={{
        fontFamily: FONT.display,
        fontWeight: 900,
        fontSize: text.length > 34 ? 84 : 98,
        lineHeight: 1.04,
        textAlign: "center",
        color: C.ink,
        opacity: s,
        transform: `translateY(${(1 - s) * 40}px)`,
      }}
    >
      {text}
    </div>
  );
};

export const StatBadge: React.FC<{ value: string; label: string }> = ({ value, label }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - 14, fps, config: { damping: 12, stiffness: 120 } });
  return (
    <div
      style={{
        transform: `scale(${s}) rotate(-3deg)`,
        background: C.accent,
        color: C.paper,
        padding: "14px 34px 18px",
        textAlign: "center",
        boxShadow: `6px 6px 0 ${C.ink}`,
        border: `3px solid ${C.ink}`,
      }}
    >
      <div style={{ fontFamily: FONT.display, fontWeight: 900, fontSize: 96, lineHeight: 1 }}>{value}</div>
      <div style={{ fontFamily: FONT.body, fontSize: 26, marginTop: 4, maxWidth: 520 }}>{label}</div>
    </div>
  );
};

export const SourceChip: React.FC<{ publisher: string }> = ({ publisher }) => (
  <div
    style={{
      position: "absolute",
      left: SAFE.side,
      top: H - SAFE.bottom + 20,
      fontFamily: FONT.body,
      fontSize: 30,
      color: C.inkSoft,
      borderTop: `2px solid ${C.ink}`,
      paddingTop: 10,
      width: W - 2 * SAFE.side - 120,
    }}
  >
    Source : <b style={{ color: C.ink }}>{publisher}</b>
  </div>
);

export const ProgressBar: React.FC<{ total: number }> = ({ total }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: 0, bottom: 0, width: W, height: 12, background: "rgba(29,23,16,0.15)" }}>
      <div style={{ width: `${interpolate(frame, [0, total], [0, 100], { extrapolateRight: "clamp" })}%`, height: "100%", background: C.accent }} />
    </div>
  );
};
