#!/usr/bin/env node
/**
 * check-layout.mjs — contrôle visuel de la mise en page (RECETTE-SITE.md §10.3 et §17.1).
 *
 * Ce que les contrôleurs HTML ne voient pas : ce que le navigateur dessine.
 *   1. Champs d'une même rangée du calculateur alignés : même haut, même hauteur (±2 px).
 *   2. Tous les champs de saisie du formulaire à la même hauteur (±2 px).
 *   3. Le contenu occupe la largeur du conteneur de la page, aligné sur l'en-tête :
 *      pas de colonne étroite collée à gauche avec un vide à droite.
 *   4. Aucun débordement horizontal à 390 px.
 *   5. Rythme vertical : ≥ 32 px entre le calculateur et ce qui suit ; blanc au-dessus de
 *      chaque H2 du contenu entre 24 et 80 px (ni collé, ni trou) ; entre deux blocs d'un même
 *      texte (paragraphe, tableau, liste) jamais plus de 48 px.
 *   6. Saisie (première page à calculateur) : cliquer puis taper aussitôt « 12 » doit afficher
 *      « 12 » (ni « 2 », ni « 2412 ») ; une valeur trop grande est ramenée au maximum ET
 *      signalée (role="status"), jamais ignorée en silence.
 *   8. Boutons à bascule (role="group" + aria-pressed) : chaque option remplit la hauteur de son
 *      cadre (±4 px), les options ont la même largeur et leur texte tient sur une ligne sans
 *      dépasser — la zone colorée couvre toute l'option.
 *   10. Aide d'un champ coincée : dans une rangée à deux champs, aide sur 2 lignes ou plus dans
 *      une demi-colonne alors que le voisin n'en a pas (elle doit s'étendre sur la rangée).
 *   7. Hydratation (même page) : aucune erreur React (#418…) au chargement le surlendemain du
 *      build, ni sur un lien partagé rechargé. Lire l'URL ou la date du jour pendant le premier
 *      rendu donne un HTML différent de celui du build : l'erreur survient à chaque visite.
 *
 * Usage : node check-layout.mjs <dossier-du-site | https://domaine> [--max 400]
 *   - un dossier : sert <dossier>/dist en local (build frais obligatoire)
 *   - une URL    : lit le sitemap du site en ligne
 * Sortie : liste des pages fautives, code 1 s'il y en a.
 * Nécessite Playwright (global : npm i -g playwright && npx playwright install chromium).
 */
import { createServer } from 'node:http';
import { existsSync } from 'node:fs';
import { readFile, stat } from 'node:fs/promises';
import { join, extname, resolve } from 'node:path';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(join(execSync('npm root -g').toString().trim(), 'playwright'))); }

const arg = process.argv[2];
const MAX = Number((process.argv.find((a) => a.startsWith('--max=')) || '--max=400').split('=')[1]);
if (!arg) { console.error('usage: check-layout.mjs <site-dir | https://domain>'); process.exit(2); }

// Un site qui borne sa colonne de lecture le declare, en disant pourquoi. Sans
// le fichier, le controle d'origine s'applique : c'est le cas de tous les
// sites de calculateur du portefeuille.
const EDITORIAL_FILE = join(arg.replace(/^https?:\/\//, '') === arg ? arg : '.', 'scripts', 'colonne-editoriale.txt');
let EDITORIAL = false;
try {
  const t = await readFile(EDITORIAL_FILE, 'utf8');
  const lignes = t.split('\n').map((l) => l.trim()).filter(Boolean);
  if (!lignes.some((l) => l.startsWith('#'))) {
    console.error(`${EDITORIAL_FILE} : declarer une colonne editoriale demande d'ecrire pourquoi, en commentaire.`);
    process.exit(2);
  }
  EDITORIAL = true;
} catch { /* absent : regle d'origine */ }

const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.xml': 'application/xml', '.txt': 'text/plain', '.ico': 'image/x-icon', '.woff2': 'font/woff2' };

async function serve(dir) {
  // Astro sort dans `dist/`, Next en export statique dans `out/`. Sans ce choix,
  // un site Next donne « 0 page, 0 defaut » : un echec deguise en succes.
  // Astro sort dans `dist/`, Next dans `out/`, et un site ecrit a la main est servi
  // depuis la racine du depot. Sans ce dernier cas, ces sites rendent « 0 page ».
  const root = ['dist', 'out'].map((d) => resolve(dir, d)).find((d) => existsSync(d))
    || (existsSync(join(resolve(dir), 'index.html')) ? resolve(dir) : resolve(dir, 'dist'));
  const server = createServer(async (req, res) => {
    let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    let f = join(root, p);
    try { if ((await stat(f)).isDirectory()) f = join(f, 'index.html'); } catch { f = f + '.html'; }
    try { const body = await readFile(f); res.writeHead(200, { 'content-type': TYPES[extname(f)] || 'application/octet-stream' }); res.end(body); }
    catch { res.writeHead(404); res.end('404'); }
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  return { base: `http://127.0.0.1:${server.address().port}`, server };
}

// Exécuté dans la page.
function inspect(__EDITORIAL__) {
  const out = [];
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  // 1 + 2 — champs du calculateur
  for (const form of document.querySelectorAll('main form')) {
    const ctrls = [...form.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=range]), select:not([size]):not([multiple]), select[size="1"]')].filter(vis);
    const rects = ctrls.map((c) => ({ id: c.id || c.name || c.tagName.toLowerCase(), r: c.getBoundingClientRect() }));
    for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
      const a = rects[i].r, b = rects[j].r;
      const sameRow = a.top < b.bottom && b.top < a.bottom && (a.right <= b.left + 1 || b.right <= a.left + 1);
      if (sameRow && (Math.abs(a.top - b.top) > 2 || Math.abs(a.height - b.height) > 2))
        out.push(`rangée désalignée : #${rects[i].id} (haut ${a.top.toFixed(0)}, h ${a.height.toFixed(0)}) ↔ #${rects[j].id} (haut ${b.top.toFixed(0)}, h ${b.height.toFixed(0)})`);
    }
    const hs = [...new Set(rects.map((x) => Math.round(x.r.height)))];
    if (hs.length && Math.max(...hs) - Math.min(...hs) > 2) out.push(`hauteurs de champs hétérogènes : ${hs.sort().join(' / ')} px`);
  }
  // 3 — largeur du contenu
  // Conteneur de référence : le bloc de l'en-tête qui porte un max-width (celui du logo et du menu).
  const header = document.querySelector('body > header, header');
  const bar = header && ([...header.querySelectorAll('*')].find((e) => getComputedStyle(e).maxWidth !== 'none' && e.getBoundingClientRect().width > 600) || header);
  const main = document.querySelector('main');
  if (bar && main && innerWidth >= 1024) {
    const c = bar.getBoundingClientRect();
    const blocks = [...main.querySelectorAll('p, h1, h2, h3, ul, ol, table')].filter((e) => vis(e) && !e.closest('[data-chrome], form, details, nav, footer, [aria-live]') && e.textContent.trim().length > 40);
    // Une grille de cartes est du contenu, même si chaque carte n'a qu'un titre court :
    // sans elle, une page de liste paraissait « décentrée » (guidevoitureelectrique.fr, /modeles/).
    // Le seuil était à trois cartes, ce qui accusait à tort les pages d'un État
    // n'en comptant que deux : la grille occupe pourtant toute la largeur
    // (costoflivingusa.com, Arkansas et Michigan, 2026-09-24).
    blocks.push(...[...main.querySelectorAll('*')].filter((e) => vis(e) && e.children.length >= 2
      && getComputedStyle(e).display.includes('grid') && !e.closest('[data-chrome], form, nav, footer')));
    if (blocks.length) {
      // Une colonne latérale (<aside> : sommaire, chiffres clés) occupe légitimement la droite.
      const asides = [...main.querySelectorAll('aside')].filter(vis);
      const right = Math.max(...blocks.map((e) => e.getBoundingClientRect().right), ...asides.map((e) => e.getBoundingClientRect().right));
      const left = Math.min(...blocks.map((e) => e.getBoundingClientRect().left));
      const gapL = left - c.left, gapR = c.right - right, width = c.width;
      if (gapR - gapL > width * 0.12) out.push(`contenu décentré : colonne ${Math.round(right - left)} px dans ${Math.round(width)} px, vide à droite ${Math.round(gapR)} px, à gauche ${Math.round(gapL)} px`);
      // Une colonne peut être centrée et rester bien trop étroite : ce contrôle ne
      // voyait que le décentrage, et laissait passer les blocs de texte à 736 px
      // dans un conteneur de 1280, avec 592 px de vide de chaque côté
      // (canadanetpay.com, signalé par l'utilisateur le 2026-09-23). §10.2 veut que
      // le texte occupe la largeur de la page, alignée sur l'en-tête.
      // Un site editorial borne volontairement sa colonne : au-dela de 75
      // caracteres l'oeil rate sa ligne au retour, et toute la presse tient
      // 65-75. La regle ci-dessous viserait alors juste ce qui fait la
      // qualite de la lecture. Un site le declare dans
      // `scripts/colonne-editoriale.txt`, et le controle mesure alors la
      // colonne en caracteres au lieu de la mesurer en part du conteneur.
      // La regle d'origine reste entiere pour les sites de calculateur, ou
      // une colonne etroite dans une page vide se voit et se signale
      // (canadanetpay.com, signale le 2026-09-23).
      else if (__EDITORIAL__) {
        // Le corps de texte, pas la signature : on prend le paragraphe le plus
        // long, seul representatif de ce qu'on lit vraiment. Prendre le
        // premier venu mesurait une ligne de 15 px et annoncait 94 caracteres
        // la ou le corps en fait 77.
        const corps = blocks.filter((b) => b.matches('p'))
          .sort((a, b) => b.textContent.length - a.textContent.length)[0] || blocks[0];
        const fsz = parseFloat(getComputedStyle(corps).fontSize) || 17;
        // 0,5 em par caractere : approximation usuelle pour une serif de labeur.
        // La mesure de lecture est la largeur du paragraphe lui-meme, pas
        // l'emprise de tous les blocs : sur une page de une, une grille de
        // trois colonnes occupe toute la page sans que personne n'ait a lire
        // 125 caracteres d'affilee.
        // Un paragraphe qui coule en colonnes a une ligne aussi longue que sa
        // colonne, pas que son bloc : mesurer le bloc annonçait 125 caracteres
        // la ou chaque colonne en fait 62. La mise en colonnes est justement
        // la reponse de la presse a un bloc large — elle remplit la largeur
        // sans allonger la ligne.
        const colonnes = Math.max(1, parseInt(getComputedStyle(corps.parentElement).columnCount, 10) || 1);
        const largeurLigne = corps.getBoundingClientRect().width / colonnes;
        const chars = largeurLigne / (fsz * 0.48);
        if (chars < 55 || chars > 85) {
          out.push(`mesure de lecture hors norme : ${Math.round(chars)} caracteres par ligne `
            + `(${Math.round(largeurLigne)} px a ${Math.round(fsz)} px`
            + `${colonnes > 1 ? `, ${colonnes} colonnes` : ''}), la presse tient 65-75`);
        }
      }
      else if (!asides.length && right - left < width * 0.75) {
        out.push(`colonne trop étroite : ${Math.round(right - left)} px dans ${Math.round(width)} px, `
          + `${Math.round(gapL)} px de vide de chaque côté`);
      }
    }
  }
  // 10 — aide coincée dans une demi-colonne
  for (const help of document.querySelectorAll('main form [id$="-help"]')) {
    const field = help.parentElement, row = field?.parentElement; if (!row || !vis(help)) continue;
    const fr = field.getBoundingClientRect();
    const nb = [...row.children].find((c) => c !== field && Math.abs(c.getBoundingClientRect().top - fr.top) < 4 && c.getBoundingClientRect().left > fr.left);
    if (!nb || nb.querySelector('[id$="-help"]')) continue;
    const lh = parseFloat(getComputedStyle(help).lineHeight) || 16;
    if (help.getBoundingClientRect().height / lh >= 1.8 && help.getBoundingClientRect().width < row.getBoundingClientRect().width * 0.8) out.push(`aide coincée dans une demi-colonne : « ${help.textContent.trim().slice(0, 40)}… »`);
  }
  // 8 — boutons à bascule
  for (const g of document.querySelectorAll('main [role="group"]')) {
    const btns = [...g.querySelectorAll('button[aria-pressed]')].filter(vis);
    if (btns.length < 2) continue;
    const box = btns[0].parentElement.getBoundingClientRect();
    const hs = btns.map((b) => b.getBoundingClientRect().height), ws = btns.map((b) => b.getBoundingClientRect().width);
    if (Math.min(...hs) < box.height - 12) out.push(`bascule « ${g.textContent.trim().slice(0, 30)} » : option de ${Math.round(Math.min(...hs))} px dans un cadre de ${Math.round(box.height)} px`);
    if (Math.max(...ws) - Math.min(...ws) > 4) out.push(`bascule « ${g.textContent.trim().slice(0, 30)} » : options de largeurs inégales (${ws.map(Math.round).join(' / ')} px)`);
    for (const b of btns) if (b.scrollWidth > b.clientWidth + 1) out.push(`bascule « ${g.textContent.trim().slice(0, 30)} » : « ${b.textContent.trim()} » dépasse de son option (${b.scrollWidth} > ${b.clientWidth} px) — raccourcir l'option`);
  }
  // 5 — rythme vertical
  // Un element en ligne (<astro-island> n'a aucun style propre) qui contient des
  // blocs se reduit a une boite de ligne vide en tete : son rect s'arrete au
  // sommet du contenu, si bien que toute la hauteur du bloc suivant passait pour
  // du blanc. Un calculateur ou une FAQ dans un ilot Astro se voyait ainsi
  // reprocher 900 a 1 200 px d'espacement (brutonaarnettoberekenen.nl, 2026-09-26).
  const bottomOf = (e) => {
    let b = e.getBoundingClientRect().bottom;
    const d = getComputedStyle(e).display;
    if (d === 'inline' || d === 'contents') {
      for (const k of e.children) { const r = k.getBoundingClientRect(); if (r.height > 0) b = Math.max(b, bottomOf(k)); }
    }
    return b;
  };
  const nextVisible = (e) => { for (let n = e.nextElementSibling; n; n = n.nextElementSibling) { if (vis(n) && getComputedStyle(n).display !== 'contents') return n; if (getComputedStyle(n).display === 'contents' && n.firstElementChild) return n.firstElementChild; } return null; };
  for (const calc of document.querySelectorAll('main .rechner')) {
    if (calc.closest('.rechner') !== calc) continue;
    let host = calc.parentElement?.tagName === 'ASTRO-ISLAND' ? calc.parentElement : calc;
    let n = nextVisible(host);
    while (n && n.getBoundingClientRect().height === 0) n = nextVisible(n);
    if (n) {
      const firstText = n.matches('h1,h2,h3,p') ? n : n.querySelector('h1,h2,h3,p,table,ul') || n;
      const gap = firstText.getBoundingClientRect().top - bottomOf(calc);
      if (gap < 32) out.push(`contenu collé au calculateur : ${Math.round(gap)} px sous le cadre`);
    }
  }
  for (const h of main ? main.querySelectorAll('h2') : []) {
    if (!vis(h) || h.closest('form, [aria-live], details, footer, a')) continue;   // a : titre de carte cliquable, espacé par sa carte
    // Titre posé directement dans une boîte encadrée (carte d'actualité, encart) : c'est le titre
    // de la carte, son espacement est celui de la carte, pas le rythme des sections.
    if (h.parentElement !== main && parseFloat(getComputedStyle(h.parentElement).borderTopWidth) > 0) continue;
    // Titre à côté d'une icône, dans une ligne flex : l'élément précédent est à sa gauche, pas
    // au-dessus ; mesurer un « blanc » vertical entre les deux n'a pas de sens (epargnemalin.fr).
    const ps = getComputedStyle(h.parentElement);
    if (ps.display.includes('flex') && !ps.flexDirection.startsWith('column')) continue;
    // Un <astro-island> est en display:contents : vis() le declare invisible alors
    // qu'il dessine tout son contenu. La remontee le sautait donc et mesurait le
    // blanc depuis le titre d'AVANT l'ilot, ce qui comptait la FAQ ou le
    // calculateur entier comme du vide (brutonaarnettoberekenen.nl, 2026-09-26).
    const remonte = (e) => {
      for (let n = e.previousElementSibling; n; n = n.previousElementSibling) {
        if (getComputedStyle(n).display === 'contents') {
          for (let k = n.lastElementChild; k; k = k.previousElementSibling) if (vis(k)) return k;
          continue;
        }
        if (vis(n)) return n;
      }
      return null;
    };
    let prev = remonte(h);
    if (!prev) continue;
    // Un surtitre de rubrique — le petit libelle en capitales qui annonce la
    // section — forme une paire avec le titre qu'il introduit. La presse les
    // colle volontairement : les separer de 24 px casse le couple et donne
    // l'impression de deux elements sans rapport. Mesure du 2026-09-25 sur
    // fdeinsider.com : la regle signalait 13 px au-dessus de chaque titre de
    // carte, alors que l'espacement etait exactement celui voulu.
    if (prev.classList.contains('kicker')) continue;
    const text = h.getBoundingClientRect().top + parseFloat(getComputedStyle(h).paddingTop) + parseFloat(getComputedStyle(h).borderTopWidth);
    const blank = text - bottomOf(prev);
    if (blank < 24 || blank > 80) out.push(`espacement irrégulier : ${Math.round(blank)} px de blanc au-dessus de « ${h.textContent.trim().slice(0, 40)} »`);
  }
  for (const prose of main ? main.querySelectorAll('.prose') : []) {
    // Bord du contenu visible : un tableau dans son conteneur à défilement porte sa marge à l'intérieur.
    const ink = (e) => (e.querySelector(':scope > table') || e).getBoundingClientRect();
    const kids = [...prose.children].filter((e) => vis(e) && !e.matches('h2, h3, h4, [data-chrome]') && e.getBoundingClientRect().height > 0);
    for (const el of kids) {
      let prev = el.previousElementSibling;
      while (prev && (!vis(prev) || prev.getBoundingClientRect().height === 0)) prev = prev.previousElementSibling;
      if (!prev || prev.matches('h2, h3, h4, [data-chrome]')) continue;
      // Un bloc dont le premier texte est un titre (<section><div><h2>…) ouvre une nouvelle
      // section : il relève de la règle des titres (24–80 px), pas de celle des trous.
      if (el.querySelector('h2, h3, h4, p, li, td')?.matches('h2, h3, h4')) continue;
      const blank = ink(el).top - ink(prev).bottom;
      if (blank > 48) out.push(`trou de ${Math.round(blank)} px avant « ${el.textContent.trim().slice(0, 40)} »`);
    }
  }
  return out;
}

// 7 — hydratation : horloge avancée de deux jours, puis lien partagé rechargé.
async function hydration(browser, url) {
  const out = [];
  const run = async (u, later) => {
    const ctx = await browser.newContext(); const p = await ctx.newPage(); const errs = [];
    p.on('pageerror', (e) => errs.push(e.message));
    if (later) await p.clock.setFixedTime(new Date(Date.now() + 2 * 86400000));
    // `waitForTimeout` s'appuie sur l'horloge de la page : après `setFixedTime`,
    // elle est figée et l'attente ne se termine jamais. Le contrôle restait
    // bloqué indéfiniment sur netsalaire.com (2026-09-24), sans message.
    // On attend donc côté script. Même raison pour `networkidle` : une balise
    // tierce chargée par un setTimeout ne se déclenche plus, le réseau ne
    // retombe jamais au repos, et l'attente ne finit pas non plus.
    const pause = (ms) => new Promise((r) => setTimeout(r, ms));
    await p.goto(u, { waitUntil: 'domcontentloaded' }).catch(() => {}); await pause(300);
    let shared = null;
    if (!later) { // produire un lien partagé par une vraie saisie
      const i = p.locator('main form input[inputmode="decimal"]').first();
      if (await i.count()) { await i.click(); await p.keyboard.type('4321'); await i.press('Tab'); await pause(300); shared = p.url(); }
    }
    await ctx.close(); return { errs: errs.filter((e) => /#41[89]|#42[35]|hydrat/i.test(e)), shared };
  };
  const a = await run(url, true);
  if (a.errs.length) out.push(`hydratation : ${a.errs.length} erreur(s) React au chargement deux jours après le build`);
  const b = await run(url, false);
  if (b.shared && b.shared !== url) { const c = await run(b.shared, true); if (c.errs.length) out.push(`hydratation : ${c.errs.length} erreur(s) React sur un lien partagé (${b.shared.replace(/^https?:\/\/[^/]+/, '')})`); }
  return out;
}

// 6 — saisie hors limite : exécuté sur la première page qui porte un calculateur.
async function overMax(page) {
  const out = [];
  const inputs = page.locator('main form input[inputmode="decimal"]:visible');
  const n = await inputs.count();
  for (let k = 0; k < n; k++) {
    const i = inputs.nth(k); const id = await i.getAttribute('id');
    await i.click(); await page.keyboard.type('12');
    const fast = await i.inputValue();
    if (fast !== '12') out.push(`#${id} : clic puis frappe immédiate de « 12 » → « ${fast} »`);
    await i.press('Tab'); await page.waitForTimeout(100);
    await i.click(); await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.type('99999999', { delay: 15 }); await page.waitForTimeout(150);
    const shown = await page.evaluate((id) => { const el = document.getElementById(id); const box = el.closest('div')?.parentElement; return !!box && [...box.querySelectorAll('[role="status"]')].some((m) => m.textContent.trim()); }, id);
    await i.press('Tab'); await page.waitForTimeout(150);
    const v = await i.inputValue();
    if (!shown) out.push(`#${id} : valeur trop grande acceptée ou ignorée sans message`);
    if (!v || /^0*$/.test(v.replace(/\D/g, ''))) out.push(`#${id} : champ vide après une saisie trop grande`);
  }
  return out;
}

const live = /^https?:\/\//.test(arg);
let base, server;
if (live) base = arg.replace(/\/$/, ''); else ({ base, server } = await serve(arg));
// Les <loc> portent le domaine de production : on les réécrit vers la base servie.
const pages = await sitemapUrls(base);
async function sitemapUrls(b) {
  const seen = new Set(); const out = new Set(); const todo = [`${b}/sitemap.xml`, `${b}/sitemap-index.xml`]; // Astro : index ; Next, statique : sitemap.xml
  while (todo.length) {
    const u = todo.pop(); if (seen.has(u)) continue; seen.add(u);
    const r = await fetch(u).catch(() => null); if (!r || !r.ok) continue;
    for (const [, loc] of (await r.text()).matchAll(/<loc>([^<]+)<\/loc>/g)) {
      const l = loc.replace(/^https?:\/\/[^/]+/, b);
      if (l.endsWith('.xml')) todo.push(l); else out.add(l);
    }
  }
  return [...out].slice(0, MAX);
}

const browser = await chromium.launch();
const faults = [];
// 390 px, c'est l'iPhone récent. La moitié du parc Android est à 360, et un
// iPhone SE ou un affichage agrandi descend à 320 : c'est là que les
// débordements apparaissent, et le contrôle ne les voyait pas
// (netsalaire.com, 2026-09-24 — six pages se balayaient latéralement).
const LARGEURS = [[1440, 900, 'desktop'], [390, 844, 'mobile'], [360, 780, 'mobile 360'], [320, 720, 'mobile 320']];
for (const [vw, vh, label] of LARGEURS) {
  const ctx = await browser.newContext({ viewport: { width: vw, height: vh } });
  const page = await ctx.newPage();
  let overChecked = false;
  for (const u of pages) {
    // Pas de `networkidle` : une balise de mesure chargée par un setTimeout
    // suffit à ce que le réseau ne retombe jamais au repos, et chaque page
    // consommait alors ses 30 secondes de délai (netsalaire.com, 2026-09-24).
    await page.goto(u, { waitUntil: 'domcontentloaded' }).catch(() => {});
    await page.waitForTimeout(250);
    const issues = await page.evaluate(inspect, EDITORIAL);
    if (label === 'desktop' && !overChecked && await page.locator('main form input[inputmode="decimal"]').count()) {
      overChecked = true; issues.push(...await hydration(browser, u)); issues.push(...await overMax(page));
    }
    if (label === 'mobile') {
      const over = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      if (over > 1) issues.push(`débordement horizontal de ${over} px`);
    }
    const path = u.replace(base, '') || '/';
    for (const i of issues) if (label === 'desktop' || !/contenu décentré|rangée/.test(i)) faults.push(`[${label}] ${path} — ${i}`);
  }
  await ctx.close();
}
await browser.close();
server?.close();

console.log(`check-layout: ${pages.length} pages × ${LARGEURS.length} largeurs, ${faults.length} défaut(s)`);
for (const f of faults) console.log('  ' + f);
process.exit(faults.length ? 1 : 0);
