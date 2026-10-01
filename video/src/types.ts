export type Source = { title: string; url: string; publisher: string };
export type Visual = { kind: "engraving" | "image" | "video"; alt?: string; src?: string | null };
export type Segment = {
  id: string;
  kicker?: string;
  headline: string;
  text: string;
  stat?: { value: string; label: string } | null;
  sources: Source[];
  visual?: Visual;
};
export type Episode = {
  id: string;
  number?: number;
  title: string;
  date: string;
  hook?: string;
  segments: Segment[];
  outro?: string;
  social?: { caption: string; hashtags: string[] };
};
export type Word = { text: string; start: number; end: number; unit: string };
export type Timing = {
  mode: "estimate" | "transcript";
  duration: number;
  units: { id: string; start: number; end: number }[];
  words: Word[];
};
export type VideoProps = { episode: Episode; timing: Timing; audioFile?: string | null };
