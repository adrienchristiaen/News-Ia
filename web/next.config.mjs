// Site 100 % statique (HTML généré au build) : se déploie tel quel sur Vercel, Netlify ou GitHub Pages.
/** @type {import('next').NextConfig} */
export default {
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
  // Les épisodes et la config de marque vivent à la racine du repo, un niveau au-dessus.
  outputFileTracingRoot: new URL("..", import.meta.url).pathname,
};
