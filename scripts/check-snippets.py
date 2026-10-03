#!/usr/bin/env python3
"""Controle BLOQUANT des snippets (RECETTE-SITE.md §11), lance a la fin de `npm run build`.

    python3 scripts/check-snippets.py dist

Pour chaque page indexable de la sortie compilee (ni noindex, ni redirection, ni 404) :
  - <title> de 50 a 60 caracteres, <meta description> de 150 a 160 (ja/ko/zh : 24-40 et 70-120),
    mesures sur le texte servi, entites decodees ;
  - le titre s'ouvre sur le terme-cle : jamais sur le pays ou son adjectif, un mot d'outil,
    un mot de rubrique ni une question (listes dans snippets_regles.py ; prefixes legitimes
    declares et justifies dans scripts/titres-exceptions.txt) ;
  - aucun titre ni aucune description servis a l'identique par deux pages ;
  - pas de tiret cadratin, pas d'espace avant : ; ! ? hors du francais, pas de marqueur de gabarit.

Pourquoi bloquant : `npm run check` existait mais le deploiement ne lance que `npm run build`.
Un titre hors regle partait en ligne sans que rien ne l'arrete (2026-10-03).
Sortie 1 au moindre ecart : le build echoue, donc le deploiement aussi.
"""
import glob, html, os, re, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets_regles import COUNTRY, GENERIC_START

sortie = sys.argv[1] if len(sys.argv) > 1 else 'dist'
racine = os.path.abspath(os.path.join(sortie, '..'))

def exceptions():
    chemin = os.path.join(racine, 'scripts', 'titres-exceptions.txt')
    if not os.path.isfile(chemin):
        return ()
    prefixes, justifie = [], False
    for ligne in open(chemin, encoding='utf-8'):
        ligne = ligne.strip()
        if not ligne:
            justifie = False
            continue
        if ligne.startswith('#'):
            justifie = True
            continue
        if not justifie:
            sys.exit(f"{chemin} : « {ligne} » sans commentaire de justification.")
        prefixes.append(ligne.lower())
    return tuple(prefixes)

EXC = exceptions()
PAYS = tuple(c.lower() for c in COUNTRY)
GABARIT = re.compile(r'\{\{|\}\}|__[A-Z_]+__|%%|\$\{|undefined|\bnull\b|\bNaN\b')

def meta_description(doc):
    for tag in re.findall(r'<meta\b[^>]*>', doc, re.I):
        if re.search(r'name\s*=\s*["\']description["\']', tag, re.I):
            m = re.search(r'content\s*=\s*"([^"]*)"', tag, re.I) or re.search(r"content\s*=\s*'([^']*)'", tag, re.I)
            return html.unescape(m.group(1)) if m else ''
    return None

ecarts, titres, descs, n = [], defaultdict(list), defaultdict(list), 0
for f in sorted(glob.glob(os.path.join(sortie, '**', '*.html'), recursive=True)):
    rel = '/' + os.path.relpath(f, sortie).replace(os.sep, '/').replace('index.html', '')
    if rel.endswith(('404.html', '/404/')) or '/embed/' in rel:
        continue
    doc = open(f, encoding='utf-8', errors='ignore').read()
    tete = doc[:doc.find('</head>')] if '</head>' in doc else doc[:200000]
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', tete, re.I) or \
       re.search(r'http-equiv=["\']refresh["\']', tete, re.I):
        continue
    m = re.search(r'<title[^>]*>(.*?)</title>', tete, re.S | re.I)
    t = html.unescape(m.group(1)).strip() if m else ''
    d = meta_description(tete)
    d = (d or '').strip()
    lang = (re.search(r'<html[^>]*\blang=["\']([a-zA-Z-]+)', doc) or [None, ''])[1][:2].lower()
    cjk = lang in ('ja', 'ko', 'zh')
    tmin, tmax, dmin, dmax = (24, 40, 70, 120) if cjk else (50, 60, 150, 160)
    n += 1
    pb = []
    if not t:
        pb.append('titre absent')
    elif not tmin <= len(t) <= tmax:
        pb.append(f'titre {len(t)} car. (attendu {tmin}-{tmax})')
    if not d:
        pb.append('description absente')
    elif not dmin <= len(d) <= dmax:
        pb.append(f'description {len(d)} car. (attendu {dmin}-{dmax})')
    tl = t.lower()
    if tl.startswith(PAYS) and not tl.startswith(EXC):
        pb.append('titre ouvert par le pays : terme-cle d\'abord, pays ensuite')
    elif GENERIC_START.match(tl) and not tl.startswith(EXC):
        pb.append(f'titre ouvert par « {t.split()[0]} » : terme-cle d\'abord')
    if '—' in t + d:
        pb.append('tiret cadratin')
    if lang and lang != 'fr' and re.search(r'[   ][:;!?](\s|$)', t + ' ' + d):
        pb.append('espace avant la ponctuation hors du francais')
    if GABARIT.search(t + ' ' + d):
        pb.append('marqueur de gabarit')
    if t:
        titres[t].append(rel)
    if d:
        descs[d].append(rel)
    if pb:
        ecarts.append((rel, t, len(t), len(d), pb))

for texte, pages in list(titres.items()) + list(descs.items()):
    if len(pages) > 1:
        quoi = 'titre' if texte in titres else 'description'
        ecarts.append((', '.join(pages[:4]) + (' …' if len(pages) > 4 else ''), texte, len(texte), 0, [f'{quoi} identique sur {len(pages)} pages']))

if ecarts:
    print(f'check-snippets : {len(ecarts)} ecart(s) sur {n} pages indexables (RECETTE §11)')
    for rel, t, lt, ld, pb in ecarts[:80]:
        print(f'  {rel}\n     « {t} » [{lt}/{ld}] -> {" ; ".join(pb)}')
    if len(ecarts) > 80:
        print(f'  … et {len(ecarts) - 80} autres')
    sys.exit(1)
print(f'check-snippets : {n} pages indexables, titres 50-60, descriptions 150-160, ordre des mots et unicite conformes')
