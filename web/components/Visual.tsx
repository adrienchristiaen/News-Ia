import { engravingGeometry } from "@/lib/engraving";
import type { Visual as V } from "@/lib/episodes";

const W = 640;

/** Illustration de journal « vivante » : gravure dessinée ligne à ligne puis légère respiration ; ou image/vidéo en sépia. */
export function Visual({ visual, seed, episodeId, height = 300 }: { visual?: V; seed: string; episodeId: string; height?: number }) {
  const src = visual?.src ? `/ep/${episodeId}/${visual.src}` : null;
  let media: React.ReactNode;
  if (visual?.kind === "video" && src) {
    media = <video className="photo" src={src} autoPlay loop muted playsInline />;
  } else if (visual?.kind === "image" && src) {
    // eslint-disable-next-line @next/next/no-img-element
    media = <img className="photo" src={src} alt={visual.alt ?? ""} />;
  } else {
    const g = engravingGeometry(seed + (visual?.alt ?? ""), W, height);
    media = (
      <svg className="engraving" viewBox={`0 0 ${W} ${height}`} role="img" aria-label={visual?.alt ?? "Illustration"} preserveAspectRatio="xMidYMid slice">
        <circle cx={g.sunX * W} cy={g.sunY} r={g.sunR} className="sun" />
        {g.rows.map((d, i) => (
          <path key={i} d={d} className={i % 5 === 0 ? "ridge heavy" : "ridge"} style={{ animationDelay: `${i * 35}ms` }} />
        ))}
      </svg>
    );
  }
  return (
    <figure className="visual">
      <div className="frame">{media}</div>
      {visual?.alt && <figcaption>{visual.alt}</figcaption>}
    </figure>
  );
}
