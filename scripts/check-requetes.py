#!/usr/bin/env python3
"""Couverture des requêtes réelles (RECETTE §23.2).

Interroge les suggestions Google du pays et de la langue pour chaque requête-graine,
puis cherche, pour chaque suggestion, la page du site dont le titre, le H1 ou l'URL
en reprend le mieux les mots. Une suggestion sans page qui couvre au moins 60 % de ses
mots est un trou possible, à lire à la main (marque, navigation, intention hors sujet).

Usage : check-requetes.py <site> --hl nb --gl no "lønn etter skatt" "skattekalkulator" …
"""
import argparse, glob, html, json, re, sys, time, unicodedata, urllib.parse, urllib.request

def norm(t):
    t = unicodedata.normalize('NFKD', t.lower())
    ws = [w for w in re.findall(r'[a-z0-9æøåäöü]+', ''.join(c for c in t if not unicodedata.combining(c))) if len(w) > 2 or w.isdigit()]
    # Une année vaut une autre année (la page 2026 répond à « … 2025 ») ; singulier et pluriel se confondent par la racine.
    return ['<annee>' if re.fullmatch(r'20\d\d', w) else w[:6] for w in ws]

ap = argparse.ArgumentParser(); ap.add_argument('site'); ap.add_argument('--hl', required=True); ap.add_argument('--gl', required=True); ap.add_argument('seeds', nargs='+')
a = ap.parse_args()
out = 'dist' if glob.glob(f'{a.site}/dist/**/index.html', recursive=True) else 'out'
pages = []
for p in glob.glob(f'{a.site}/{out}/**/index.html', recursive=True):
    t = open(p, encoding='utf-8').read()
    if 'noindex' in t[:4000] or '/embed/' in p: continue
    ti = re.search(r'<title>(.*?)</title>', t, re.S); h1 = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    url = p[len(a.site) + len(out) + 1:-10] or '/'
    txt = ' '.join([html.unescape(ti.group(1)) if ti else '', html.unescape(re.sub('<[^>]+>', '', h1.group(1))) if h1 else '', url.replace('-', ' ')])
    pages.append((url, set(norm(txt))))
if not pages: sys.exit('0 page trouvée : le contrôle a échoué (RECETTE §0).')
holes = total = 0
for seed in a.seeds:
    u = 'https://suggestqueries.google.com/complete/search?' + urllib.parse.urlencode({'client': 'firefox', 'hl': a.hl, 'gl': a.gl, 'q': seed})
    try: sugg = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read().decode('utf-8', 'replace'))[1][:8]
    except Exception as e: print(f'?? {seed}: {e}'); continue
    for q in sugg:
        words = set(norm(q)); total += 1
        if not words: continue
        best = max(pages, key=lambda pg: (len(words & pg[1]), -len(pg[1])))  # à égalité, la page la plus ciblée
        cov = len(words & best[1]) / len(words)
        flag = 'ok' if cov >= 0.6 else '!!'
        holes += flag == '!!'
        print(f'{flag} {q:55} → {best[0]} ({cov:.0%})')
    time.sleep(0.4)
print(f'{a.site} : {total} suggestion(s), {holes} sans page qui les couvre (à lire à la main)')
