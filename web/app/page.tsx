import { Issue } from "@/components/Issue";
import { Masthead } from "@/components/Masthead";
import { allEpisodes } from "@/lib/episodes";

export default function Home() {
  const [latest] = allEpisodes();
  if (!latest) {
    return (
      <main className="paper"><Masthead /><p className="demo">Aucun numéro pour l'instant : lance <code>newsia run</code> puis publie.</p></main>
    );
  }
  return <Issue ep={latest} />;
}
