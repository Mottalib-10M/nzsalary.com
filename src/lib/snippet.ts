/**
 * Calibrage des extraits au build (RECETTE §15 point 15, journal 2026-09-20) : la page choisit,
 * parmi des fins de phrase, la première qui fait tomber le titre dans 50–60 caractères et la
 * description dans 150–160. Si aucune ne convient, le build échoue : un extrait hors fenêtre ne
 * peut plus sortir en production.
 */
const DESC_TAILS = ['', ' Free.', ' Free, no sign-up.', ' Free and private.', ' Free, private, no sign-up.', ' Updated for 2026.', ' Free, updated for 2026.', ' Free, private and updated for 2026.', ' Calculated in your browser, free.', ' Free, no sign-up, calculated in your browser.'];
const TITLE_TAILS = ['', ' NZ', ' (NZ)', ' | New Zealand'];
function fit(core: string, tails: string[], lo: number, hi: number, what: string): string {
  for (const t of tails) { const s = core + t; if (s.length >= lo && s.length <= hi) return s; }
  throw new Error(`${what} hors fenêtre ${lo}–${hi} (${core.length}) : « ${core} »`);
}
export const fitDescription = (d: string) => fit(d.trim(), DESC_TAILS, 150, 160, 'Description');
export const fitTitle = (t: string) => fit(t.trim(), TITLE_TAILS, 50, 60, 'Titre');
