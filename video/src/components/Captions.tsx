import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT, W, SAFE, H } from "../theme";
import type { Word } from "../types";

const CHUNK = 4; // mots affichés ensemble

/** Sous-titres mot à mot : le mot prononcé est surligné, le bloc change toutes les 4 mots. */
export const Captions: React.FC<{ words: Word[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  let idx = words.findIndex((w) => t >= w.start && t < w.end + 0.12);
  if (idx < 0) idx = words.findLastIndex((w) => w.start <= t);
  if (idx < 0) return null;
  const first = Math.floor(idx / CHUNK) * CHUNK;
  const chunk = words.slice(first, first + CHUNK);
  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.side,
        width: W - 2 * SAFE.side,
        top: H - SAFE.bottom - 330,
        height: 330,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        alignContent: "center",
        gap: "0 26px",
        fontFamily: FONT.display,
        fontWeight: 700,
        fontSize: 92,
        lineHeight: 1.12,
        color: C.ink,
        textAlign: "center",
      }}
    >
      {chunk.map((w, i) => {
        const active = first + i === idx;
        return (
          <span
            key={first + i}
            style={{
              color: active ? C.paper : C.ink,
              background: active ? C.accent : "transparent",
              padding: "0 14px",
              borderRadius: 6,
              transform: active ? "rotate(-1.5deg) scale(1.04)" : "none",
              opacity: first + i > idx ? 0.28 : 1,
            }}
          >
            {w.text}
          </span>
        );
      })}
    </div>
  );
};
