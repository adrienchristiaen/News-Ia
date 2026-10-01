import React, { useMemo } from "react";
import { Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";
import type { Visual } from "../types";

function hash(s: string) {
  let h = 2166136261;
  for (const ch of s) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return () => ((h = Math.imul(h ^ (h >>> 15), 2246822507)) >>> 0) / 4294967296;
}

/**
 * Gravure procédurale : des lignes d'encre horizontales déformées par un relief (soleil, collines).
 * Une graine dérivée du texte alt donne une image différente par séquence, sans fichier image.
 */
const ProceduralEngraving: React.FC<{ seed: string; w: number; h: number; progress: number }> = ({ seed, w, h, progress }) => {
  const geo = useMemo(() => {
    const rnd = hash(seed);
    const bumps = Array.from({ length: 4 }, () => ({ x: 0.1 + rnd() * 0.8, s: 0.07 + rnd() * 0.14, a: 0.5 + rnd() * 0.9 }));
    const sunX = 0.2 + rnd() * 0.6;
    const n = 46;
    const rows: string[] = [];
    for (let i = 0; i < n; i++) {
      const depth = i / (n - 1);                       // 0 = loin (haut), 1 = devant (bas)
      const y0 = h * 0.30 + depth * h * 0.66;
      const amp = h * 0.32 * (0.3 + 0.7 * depth);
      let d = "";
      for (let x = 0; x <= w; x += 6) {
        const u = x / w;
        const ridge = bumps.reduce((acc, b) => acc + b.a * Math.exp(-Math.pow((u - b.x) / b.s, 2)), 0);
        const wobble = Math.sin(u * 22 + i * 0.9) * 1.6;
        d += `${x === 0 ? "M" : "L"}${x},${(y0 - amp * ridge * 0.55 + wobble).toFixed(1)} `;
      }
      rows.push(d + `L${w},${h + 4} L0,${h + 4} Z`);  // fermé vers le bas : masque les lignes derrière
    }
    return { rows, sunX };
  }, [seed, w, h]);
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: "block" }}>
      <circle cx={geo.sunX * w} cy={h * 0.26} r={h * 0.15} fill={C.accent} opacity={0.88 * Math.min(1, progress * 2)} />
      {geo.rows.map((d, i) => (
        <path
          key={i}
          d={d}
          fill="#f0e6cd"
          stroke={C.ink}
          strokeWidth={1.3 + (i % 5 === 0 ? 0.9 : 0)}
          strokeLinejoin="round"
          opacity={interpolate(progress, [i / 70, i / 70 + 0.3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
        />
      ))}
    </svg>
  );
};

export const Engraving: React.FC<{ visual?: Visual; seed: string; width: number; height: number }> = ({ visual, seed, width, height }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = Math.min(1, frame / (fps * 1.1));
  const zoom = 1 + frame * 0.0006; // lent « Ken Burns » : la gravure respire
  const alt = visual?.alt;
  const media =
    visual?.kind === "image" && visual.src ? (
      <Img src={staticFile(visual.src)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(1) sepia(0.55) contrast(1.15)" }} />
    ) : visual?.kind === "video" && visual.src ? (
      <OffthreadVideo src={staticFile(visual.src)} muted style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(1) sepia(0.55) contrast(1.15)" }} />
    ) : (
      <ProceduralEngraving seed={seed + (alt ?? "")} w={width} h={height} progress={progress} />
    );
  return (
    <div style={{ width, color: C.ink }}>
      <div style={{ border: `4px double ${C.ink}`, padding: 10, background: "rgba(255,250,235,0.35)" }}>
        <div style={{ width: width - 28 - 8, height, overflow: "hidden", transform: "translateZ(0)" }}>
          <div style={{ width: "100%", height: "100%", transform: `scale(${zoom})`, transformOrigin: "50% 60%" }}>{media}</div>
        </div>
      </div>
      {alt && (
        <div style={{ fontFamily: FONT.body, fontStyle: "italic", fontSize: 25, textAlign: "center", marginTop: 12, color: C.inkSoft }}>
          {alt}
        </div>
      )}
    </div>
  );
};
