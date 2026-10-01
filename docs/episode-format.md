# Format de `episode.json`

| Champ | Description |
|---|---|
| `id`, `title`, `date`, `number?` | identité du numéro (`id` = nom du dossier, ex. `2026-w40`) |
| `hook`, `outro` | accroche et clôture, lues à voix haute |
| `segments[]` | 3 à 5 sujets : `id`, `kicker`, `headline`, `text` (voix off), `stat?`, `sources[]` (obligatoire), `visual?` |
| `visual` | `{ "kind": "engraving" | "image" | "video", "alt": "légende", "src": "assets/x.jpg" }` |
| `social` | `caption` et `hashtags` pour `legende.txt` |
| `gazette` | version « presse écrite » : `headline`, `lede`, `articles[]` (un par segment, plusieurs paragraphes) |
| `demo` | `true` pour un numéro d'exemple, masqué dès qu'un vrai numéro existe |

Ordre de lecture à voix haute : `hook` → `segments[].text` → `outro`. Débit de référence : 2,6 mots/s.
