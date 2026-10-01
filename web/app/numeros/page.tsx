import Link from "next/link";
import { Masthead } from "@/components/Masthead";
import { allEpisodes, frDate } from "@/lib/episodes";

export const metadata = { title: "Archives" };

export default function Archive() {
  return (
    <main className="paper">
      <Masthead />
      <ul className="archive">
        {allEpisodes().map((e) => (
          <li key={e.id}>
            <Link href={`/numero/${e.id}/`}>
              <span className="n">{e.number !== undefined ? `N° ${e.number}` : e.id}</span>
              <span className="h">{e.gazette?.headline ?? e.title}</span>
              <span className="d">{frDate(e.date)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
