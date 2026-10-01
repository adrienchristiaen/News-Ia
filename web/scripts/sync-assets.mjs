// Copie les médias des épisodes (images/vidéos citées dans episode.json, short.mp4) vers public/ep/<id>/
import { cpSync, existsSync, mkdirSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const eps = join(root, "episodes");
for (const id of readdirSync(eps, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name)) {
  const dst = join(root, "web", "public", "ep", id);
  for (const sub of ["assets", "visuals"]) {
    const from = join(eps, id, sub);
    if (existsSync(from)) {
      mkdirSync(dst, { recursive: true });
      cpSync(from, join(dst, sub), { recursive: true });
    }
  }
  const short = join(eps, id, "short.mp4");
  if (existsSync(short)) {
    mkdirSync(dst, { recursive: true });
    cpSync(short, join(dst, "short.mp4"));
  }
}
console.log("✓ médias des épisodes synchronisés");
