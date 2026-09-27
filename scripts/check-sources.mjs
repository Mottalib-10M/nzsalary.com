#!/usr/bin/env node
/**
 * check-sources.mjs — les sources officielles citées répondent-elles encore ? (RECETTE-SITE.md §17.4)
 *
 * Lit toutes les URL externes du code source (paramètres, pages, composants — hors schema.org, polices,
 * outils Google/Bing, réseaux sociaux, exemples) et les ouvre une à une.
 * Échoue sur les liens MORTS : 404, 410, ou page « introuvable » servie avec un code 200 (le SEPE
 * répond 200 avec « No encontrada »). Signale sans bloquer les liens INJOIGNABLES (5xx, connexion
 * refusée, délai : panne du serveur, pas du lien — le SEPE était en 503 le 2026-09-18) et BLOQUÉS
 * aux robots (403, 429) : à revérifier à la main avant de conclure.
 *
 * Usage : node check-sources.mjs <dossier-du-site>   → code 1 si une source est morte.
 */
import { readdir, readFile } from 'node:fs/promises';
import { join, resolve, basename } from 'node:path';

const site = process.argv[2];
if (!site) { console.error('usage: check-sources.mjs <site-dir>'); process.exit(2); }

async function* walk(d) {
  for (const e of await readdir(d, { withFileTypes: true })) {
    const p = join(d, e.name);
    // `scripts` est exclu : les controleurs portent dans leur propre texte
    // d'usage des URL d'exemple (« https://domaine », « http://x ») qui
    // ressortaient comme des sources mortes du site. Un controle qui signale
    // ses propres lignes d'aide apprend a ignorer ses avertissements.
    if (e.isDirectory()) { if (!/node_modules|dist|out|_archives|scripts|\.astro|\.git/.test(e.name)) yield* walk(p); }
    // Le HTML compte : un site écrit à la main n'a ni .astro ni .tsx, et ses
    // sources officielles ne vivent que là. Sans cette extension, le contrôle
    // annonçait « 0 source » sur netsalaire.com — un échec déguisé en succès.
    // `package-lock.json` ne contient que des archives npm : des centaines d'URL
    // qui ne sont pas des sources et noient le résultat.
    else if (/^package-lock\.json$/.test(e.name)) continue;
    else if (/\.(json|ts|tsx|astro|mjs|html)$/.test(e.name)) yield p;
  }
}
const urls = new Set();
// clarity.ms et formspree.io ne sont pas des sources : l'un est une balise de
// mesure, l'autre un point d'envoi de formulaire qui refuse le GET (405).
const IGNORE = /(schema\.org|w3\.org|clarity\.ms|formspree\.io|googletagmanager|google-analytics|googleapis|gstatic|google\.com|bing\.com|indexnow|fonts\.|example\.|localhost|127\.0\.0\.1|twitter\.com|x\.com|facebook\.com|linkedin\.com|wa\.me|mailto:|\$\{)/;
// Astro et Next rangent leurs sources dans `src` ; un site écrit à la main a ses
// pages à la racine. On parcourt la racine dans tous les cas : `src` en fait
// partie, et un `src` réduit à une feuille de style ne prouve rien.
for await (const f of walk(site)) {
  const txt = await readFile(f, 'utf8');
  for (const m of txt.matchAll(/https?:\/\/[^"'`\s)<>]+/g)) {
    const u = m[0].replace(/#.*$/, '').replace(/[.,;]+$/, '');
    if (!IGNORE.test(u) && !u.includes(basename(resolve(site)))) urls.add(u);
  }
}

const NOT_FOUND = /(page not found|no encontrada|página no encontrada|pagina niet gevonden|seite nicht gefunden|page introuvable|404 not found|error 404)/i;
const dead = [], blocked = [], down = [];
await Promise.all([...urls].map(async (u) => {
  try {
    const r = await fetch(u, { redirect: 'follow', signal: AbortSignal.timeout(30000), headers: { 'user-agent': 'Mozilla/5.0 (check-sources)' } });
    const body = r.ok ? (await r.text()).slice(0, 4000) : '';
    if (r.status === 403 || r.status === 429) blocked.push(`${r.status} ${u}`);
    else if (r.status >= 500) down.push(`${r.status} ${u}`);
    else if (r.status >= 400) dead.push(`${r.status} ${u}`);
    else if (NOT_FOUND.test(body.replace(/<[^>]+>/g, ' '))) dead.push(`200 mais « introuvable » ${u}`);
  } catch (e) { down.push(`${e.name === 'TimeoutError' ? 'délai' : 'connexion'} ${u}`); }
}));
console.log(`check-sources: ${urls.size} source(s), ${dead.length} morte(s), ${down.length} injoignable(s), ${blocked.length} bloquée(s) aux robots`);
dead.forEach((d) => console.log('  ✗ ' + d));
down.forEach((d) => console.log('  ~ ' + d + '  (serveur en panne ? à revérifier)'));
blocked.forEach((d) => console.log('  ? ' + d + '  (à vérifier à la main)'));
process.exit(dead.length ? 1 : 0);
