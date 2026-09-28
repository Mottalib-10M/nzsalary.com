#!/usr/bin/env python3
"""Chaque page de contenu contient au moins un simulateur (RECETTE §9.3).

Une page « de contenu » est toute page indexable qui n'est ni une page de service (à propos,
contact, politique éditoriale, confidentialité, mentions, cookies, widget, glossaire,
méthodologie) ni la racine de redirection. Un simulateur est un champ que le visiteur peut
manipuler dans le <main> : <input> numérique ou texte décimal, ou <select>, rendu dans le HTML
du build (île hydratée). Un lien vers un calculateur ne compte pas.

Usage : check-simulateurs.py <site>   → code de sortie 1 s'il manque au moins un simulateur.
"""
import glob, re, sys

SERVICE = re.compile(r'/(about|a-propos|om-oss|over-ons|om-oss|uber-uns|ueber-uns|chi-siamo|sobre|sobre-nos|quienes-somos|acerca|contact|contacto|contatti|kontakt|editorial[^/]*|politique-editoriale|redaksjonell[^/]*|redaktionel[^/]*|redactiebeleid|redaktion[^/]*|politica-editorial|privacy|privacidad|privacidade|personvern|privatliv[^/]*|datenschutz|confidentialite|terms|vilkar|vilkaar|mentions-legales|disclaimer|impressum|aviso-legal|termos|cookies|informasjonskapsler|widget|embed|glossary|glossaire|glosario|glossario|glossar|woordenlijst|ordliste|ordbog|ordlista|methodology|methodologie|metodologia|metodologia|metode|metod|methodik)/')
INPUT = re.compile(r'<input\b(?![^>]*type="(?:hidden|search|checkbox|radio|submit|button)")[^>]*>|<select\b', re.I)

site = sys.argv[1].rstrip('/')
out = 'dist' if glob.glob(f'{site}/dist/**/index.html', recursive=True) else 'out'
pages = missing = 0
bad = []
for p in sorted(glob.glob(f'{site}/{out}/**/index.html', recursive=True)):
    t = open(p, encoding='utf-8', errors='replace').read()
    if re.search(r'<meta[^>]+name="robots"[^>]+noindex', t) or 'http-equiv="refresh"' in t: continue
    url = p[len(site) + len(out) + 1:-len('index.html')] or '/'
    if SERVICE.search(url): continue
    m = re.search(r'<main\b.*?</main>', t, re.S)
    pages += 1
    if not INPUT.search(m.group(0) if m else t):
        missing += 1; bad.append(url)
for u in bad: print(f'!! {u}')
print(f'{site} : {pages} page(s) de contenu, {missing} sans simulateur')
if pages == 0: sys.exit('0 page examinée : le contrôle a échoué (RECETTE §0).')
sys.exit(1 if missing else 0)
