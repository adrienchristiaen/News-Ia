import type { Metadata } from "next";
import "@fontsource/playfair-display/700.css";
import "@fontsource/playfair-display/900.css";
import "@fontsource/im-fell-english-sc/400.css";
import "@fontsource/source-serif-4/400.css";
import "@fontsource/source-serif-4/400-italic.css";
import "@fontsource/source-serif-4/700.css";
import "./globals.css";
import { brand } from "@/lib/episodes";

export const metadata: Metadata = {
  title: { default: brand.name, template: `%s · ${brand.name}` },
  description: brand.tagline,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const c = brand.colors;
  const vars = { "--paper": c.paper, "--paper-dark": c.paperDark, "--ink": c.ink, "--ink-soft": c.inkSoft, "--accent": c.accent, "--gold": c.gold } as React.CSSProperties;
  return (
    <html lang="fr">
      <body style={vars}>{children}</body>
    </html>
  );
}
