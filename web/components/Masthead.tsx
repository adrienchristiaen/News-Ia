import Link from "next/link";
import { brand, frDate } from "@/lib/episodes";

export function Masthead({ date, number }: { date?: string; number?: number }) {
  return (
    <header className="masthead">
      <div className="rule thick" />
      <Link href="/" className="nameplate">{brand.name}</Link>
      <p className="tagline">{brand.tagline}</p>
      <div className="rule" />
      <nav className="dateline">
        <span>{number !== undefined ? `N° ${number}` : "Édition hebdomadaire"}</span>
        <span className="date">{date ? frDate(date) : "Tous les numéros"}</span>
        <Link href="/numeros/">Archives</Link>
      </nav>
      <div className="rule thick" />
    </header>
  );
}
