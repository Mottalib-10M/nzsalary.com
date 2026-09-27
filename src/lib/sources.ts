/** Sources officielles, tirées du fichier de paramètres (RECETTE §7, §8.3). */
import P from '../data/params-2026.json';
const s = P.sources as Record<string, { url: string; label: { en: string } }>;
export const SRC = Object.fromEntries(Object.entries(s).map(([k, v]) => [k, { name: v.label.en, url: v.url }])) as Record<keyof typeof P.sources, { name: string; url: string }>;
