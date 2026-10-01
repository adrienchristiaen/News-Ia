import brand from "../../config/brand.json";

export const B = brand;
export const C = brand.colors;
export const FONT = {
  display: '"Playfair Display", Georgia, serif',
  body: '"Source Serif 4", Georgia, serif',
  caps: '"IM Fell English SC", "Playfair Display", Georgia, serif',
};
export const W = 1080;
export const H = 1920;
export const FPS = 30;
// Zones réservées par les interfaces TikTok / Reels / Shorts (boutons, légende) : on n'y met rien d'essentiel.
export const SAFE = { top: 150, bottom: 420, side: 70 };
