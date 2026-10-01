/** Gravure procédurale (même algorithme que le template vidéo) : relief de lignes d'encre avec masquage des lignes cachées. */
function hash(s: string) {
  let h = 2166136261;
  for (const ch of s) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return () => ((h = Math.imul(h ^ (h >>> 15), 2246822507)) >>> 0) / 4294967296;
}

export function engravingGeometry(seed: string, w: number, h: number) {
  const rnd = hash(seed);
  const bumps = Array.from({ length: 4 }, () => ({ x: 0.1 + rnd() * 0.8, s: 0.07 + rnd() * 0.14, a: 0.5 + rnd() * 0.9 }));
  const sunX = 0.2 + rnd() * 0.6;
  const n = 46;
  const rows: string[] = [];
  for (let i = 0; i < n; i++) {
    const depth = i / (n - 1);
    const y0 = h * 0.3 + depth * h * 0.66;
    const amp = h * 0.32 * (0.3 + 0.7 * depth);
    let d = "";
    for (let x = 0; x <= w; x += 6) {
      const u = x / w;
      const ridge = bumps.reduce((acc, b) => acc + b.a * Math.exp(-Math.pow((u - b.x) / b.s, 2)), 0);
      const wobble = Math.sin(u * 22 + i * 0.9) * 1.6;
      d += `${x === 0 ? "M" : "L"}${x},${(y0 - amp * ridge * 0.55 + wobble).toFixed(1)} `;
    }
    rows.push(d + `L${w},${h + 4} L0,${h + 4} Z`);
  }
  return { rows, sunX, sunY: h * 0.26, sunR: h * 0.15 };
}
