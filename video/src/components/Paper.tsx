import React from "react";
import { AbsoluteFill } from "remotion";
import { C } from "../theme";

/** Fond « papier de journal » : dégradé chaud, vignette et grain fixe (SVG), sans image externe. */
export const Paper: React.FC<{ children?: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse at 50% 38%, ${C.paper} 0%, ${C.paper} 45%, ${C.paperDark} 100%)`,
    }}
  >
    <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.22, mixBlendMode: "multiply" }}>
      <filter id="grain">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" />
        <feColorMatrix values="0 0 0 0 0.25  0 0 0 0 0.18  0 0 0 0 0.08  0 0 0 0.9 0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#grain)" />
    </svg>
    {children}
  </AbsoluteFill>
);
