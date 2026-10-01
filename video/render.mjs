// Rend un épisode : node render.mjs --week 2026-w40 [--still 120] [--out chemin.mp4]
// Prérequis : `newsia align --week <semaine>` (crée timing.json ; utilise words.json si ta voix est transcrite).
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, arr) => (a.startsWith("--") ? [...acc, [a.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : true]] : acc), []),
);
const week = args.week;
if (!week) {
  console.error("Usage : node render.mjs --week 2026-w40 [--still 120] [--out out/x.mp4]");
  process.exit(1);
}
const dir = resolve(here, "..", "episodes", week);
const need = (f) => {
  if (!existsSync(join(dir, f))) {
    console.error(`✗ ${join(dir, f)} introuvable.${f === "timing.json" ? `  Lance d'abord : newsia align --week ${week}` : ""}`);
    process.exit(1);
  }
  return JSON.parse(readFileSync(join(dir, f), "utf8"));
};
const episode = need("episode.json");
const timing = need("timing.json");

// Les fichiers de l'épisode (voix, images) sont copiés dans public/ pour être servis au rendu.
const pub = join(here, "public", "ep", week);
mkdirSync(pub, { recursive: true });
let audioFile = null;
const voice = readdirSync(dir).find((f) => /^voice\.(mp3|wav|m4a|aac|ogg)$/i.test(f));
if (voice) {
  cpSync(join(dir, voice), join(pub, voice));
  audioFile = `ep/${week}/${voice}`;
} else {
  console.warn("⚠ pas de voice.mp3/wav dans l'épisode : rendu muet (timing estimé).");
}
for (const s of episode.segments) {
  const v = s.visual;
  if (v?.src && !/^https?:/.test(v.src)) {
    cpSync(join(dir, v.src), join(pub, v.src), { recursive: true });
    v.src = `ep/${week}/${v.src}`;
  }
}
const propsPath = join(here, "out", `${week}.props.json`);
mkdirSync(dirname(propsPath), { recursive: true });
writeFileSync(propsPath, JSON.stringify({ episode, timing, audioFile }));

const bin = join(here, "node_modules", ".bin", "remotion");
const cmd = args.still
  ? ["still", "src/index.ts", "WeeklyShort", args.out || `out/${week}.png`, `--frame=${args.still}`]
  : ["render", "src/index.ts", "WeeklyShort", args.out || `out/${week}.mp4`];
if (args.frames && !args.still) cmd.push(`--frames=${args.frames}`); // ex. --frames 0-90 : extrait de 3 s pour tester
const r = spawnSync(bin, [...cmd, `--props=${propsPath}`], { cwd: here, stdio: "inherit" });
process.exit(r.status ?? 1);
