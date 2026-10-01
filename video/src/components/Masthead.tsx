import React from "react";
import { B, C, FONT, SAFE, W } from "../theme";

const Rule: React.FC<{ thick?: boolean }> = ({ thick }) => (
  <div style={{ height: thick ? 6 : 2, background: C.ink, width: "100%" }} />
);

export const Masthead: React.FC<{ number?: number; date: string }> = ({ number, date }) => {
  const d = new Date(date + "T12:00:00");
  const pretty = d.toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  return (
    <div style={{ position: "absolute", top: SAFE.top - 60, left: SAFE.side, width: W - 2 * SAFE.side, color: C.ink }}>
      <Rule thick />
      <div style={{ fontFamily: FONT.caps, fontSize: Math.min(76, Math.floor(930 / (B.name.length * 0.56))), whiteSpace: "nowrap", textAlign: "center", lineHeight: 1.1, padding: "14px 0 8px", letterSpacing: 1 }}>
        {B.name}
      </div>
      <Rule />
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: FONT.body, fontSize: 26, padding: "8px 4px", textTransform: "capitalize", color: C.inkSoft }}>
        <span>{number !== undefined ? `N° ${number}` : ""}</span>
        <span>{pretty}</span>
        <span>{B.handle}</span>
      </div>
      <Rule thick />
    </div>
  );
};
