import fs from "node:fs";
import path from "node:path";
import brandJson from "../../config/brand.json";

export const brand = brandJson;

export type Source = { title: string; url: string; publisher: string };
export type Visual = { kind: "engraving" | "image" | "video"; alt?: string; src?: string | null };
export type Segment = {
  id: string; kicker?: string; headline: string; text: string;
  stat?: { value: string; label: string } | null; sources: Source[]; visual?: Visual;
};
export type Article = { segment: string; headline: string; body: string[] };
export type Episode = {
  id: string; number?: number; title: string; date: string; demo?: boolean;
  hook?: string; segments: Segment[]; outro?: string;
  gazette?: { headline: string; lede: string; articles: Article[] };
  social?: { caption: string; hashtags: string[] };
};

const ROOT = path.resolve(process.cwd(), "..", "episodes");

/** Tous les numéros, du plus récent au plus ancien. Le numéro de démo n'apparaît que s'il n'y a rien d'autre. */
export function allEpisodes(): Episode[] {
  const dirs = fs.readdirSync(ROOT, { withFileTypes: true }).filter((d) => d.isDirectory());
  const eps = dirs
    .map((d) => path.join(ROOT, d.name, "episode.json"))
    .filter((p) => fs.existsSync(p))
    .map((p) => JSON.parse(fs.readFileSync(p, "utf8")) as Episode);
  const real = eps.filter((e) => !e.demo);
  return (real.length ? real : eps).sort((a, b) => b.date.localeCompare(a.date));
}

export const getEpisode = (id: string) => allEpisodes().find((e) => e.id === id);
export const hasShort = (id: string) => fs.existsSync(path.join(process.cwd(), "public", "ep", id, "short.mp4"));

export const frDate = (iso: string) =>
  new Date(iso + "T12:00:00").toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
