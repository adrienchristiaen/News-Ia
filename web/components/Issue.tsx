import { Masthead } from "./Masthead";
import { Visual } from "./Visual";
import { brand, hasShort, type Article, type Episode, type Segment } from "@/lib/episodes";

function Sources({ s }: { s: Segment }) {
  return (
    <p className="sources">
      Sources :{" "}
      {s.sources.map((src, i) => (
        <span key={src.url}>
          {i > 0 && " · "}
          <a href={src.url} target="_blank" rel="noopener noreferrer">{src.publisher}</a>
        </span>
      ))}
    </p>
  );
}

function Story({ ep, seg, art }: { ep: Episode; seg: Segment; art?: Article }) {
  const body = art?.body ?? [seg.text];
  return (
    <article className="story">
      {seg.kicker && <p className="kicker">{seg.kicker}</p>}
      <h2>{art?.headline ?? seg.headline}</h2>
      <Visual visual={seg.visual} seed={seg.id + seg.headline} episodeId={ep.id} />
      {seg.stat && (
        <p className="stat"><b>{seg.stat.value}</b><span>{seg.stat.label}</span></p>
      )}
      <div className="body">
        {body.map((p, i) => <p key={i} className={i === 0 ? "dropcap" : undefined}>{p}</p>)}
      </div>
      <Sources s={seg} />
    </article>
  );
}

export function Issue({ ep }: { ep: Episode }) {
  const g = ep.gazette;
  const byId = new Map(ep.segments.map((s) => [s.id, s]));
  const artOf = (id: string) => g?.articles.find((a) => a.segment === id);
  const [lead, ...rest] = ep.segments;
  return (
    <main className="paper">
      <Masthead date={ep.date} number={ep.number} />
      {ep.demo && <p className="demo">Numéro de démonstration : contenu fictif, pour voir la mise en page.</p>}

      <section className="une">
        <div className="une-text">
          <p className="kicker">À la une</p>
          <h1>{g?.headline ?? ep.title}</h1>
          {g?.lede && <p className="lede">{g.lede}</p>}
        </div>
        <aside className="spoken">
          <p className="kicker">Le journal parlé</p>
          {hasShort(ep.id) ? (
            <video controls playsInline preload="metadata" src={`/ep/${ep.id}/short.mp4`} />
          ) : (
            <div className="novideo">La vidéo de ce numéro arrive.<br />Sur TikTok, Instagram et YouTube Shorts : <b>{brand.handle}</b></div>
          )}
          <ul className="brief">
            {ep.segments.map((s) => <li key={s.id}><b>{s.kicker}</b> {s.headline}</li>)}
          </ul>
        </aside>
      </section>

      <div className="rule" />
      <section className="lead-story">
        <Story ep={ep} seg={lead} art={artOf(lead.id)} />
      </section>
      <div className="rule" />
      <section className="columns">
        {rest.map((s) => <Story key={s.id} ep={ep} seg={byId.get(s.id)!} art={artOf(s.id)} />)}
      </section>

      <footer className="foot">
        <div className="rule thick" />
        <p>{brand.name} · {brand.tagline} · Chaque fait est relié à ses sources : clique, vérifie, doute.</p>
      </footer>
    </main>
  );
}
