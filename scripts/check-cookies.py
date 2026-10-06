"""Contrôle « sans cookie » — RECETTE-SITE.md §15.6 (décision de l'éditeur du 2026-10-06).

Usage : python3 scripts/check-cookies.py <dossier-site> [--verbose]

Règle : aucun bandeau cookies ; Microsoft Clarity gardé en mode SANS COOKIE ; pages
légales qui disent qu'aucun cookie n'est déposé ; aucun GA4 ni autre traceur.

Le contrôle lit la sortie servie (dist/, out/…), pas le code : c'est ce que reçoit
le visiteur qui compte.
  1. Aucun bandeau : ni #consent-banner, ni [data-consent-manage], ni composant de
     bandeau connu (cookie-banner, cookieconsent, Cookiebot, OneTrust, tarteaucitron…).
  2. Aucun traceur autre que Clarity : ni gtag / googletagmanager / google-analytics,
     ni AdSense, ni pixel Meta, Hotjar, Matomo, Plausible… (pages et scripts servis).
  3. Clarity, s'il est chargé : le signal consentv2 { ad_Storage:'denied',
     analytics_Storage:'denied' } est mis en file AVANT l'adresse clarity.ms/tag/,
     dans la page ; <body data-clarity-mask="true"> masque tout le contenu par le code ;
     l'ancien chargement conditionnel (__clarityLoad, consent-choice) a disparu.
  4. Pages légales présentes : une page de confidentialité et une page de mentions
     légales / CGU par langue servie ; chaque page cookies ou confidentialité dit
     qu'aucun cookie n'est déposé ; elle nomme Clarity si Clarity est chargé ; aucune
     phrase des pages légales ne décrit un bandeau, un choix de consentement, GA4,
     Google Analytics ou AdSense (une phrase négative, « il n'y a pas de bandeau »,
     est admise).
Sortie : 0 si tout est conforme, 1 sinon.
"""
import re
import sys
from pathlib import Path

SORTIES = ('dist', 'out', 'build', 'docs', 'output', '_site', 'www')

BANDEAU = re.compile(
    r'id=["\']consent-banner|data-consent-manage|id=["\']cookie-?banner|class=["\'][^"\']*\bcookie-?banner'
    r'|cookieconsent|cookiebot|onetrust|tarteaucitron|klaro\.js|iubenda|didomi|axeptio|termly',
    re.I)
TRACEURS = re.compile(
    r'googletagmanager\.com|google-analytics\.com|\bgtag\s*\(|(?-i:\bG-[A-Z0-9]{10}\b)'
    r'|pagead2\.googlesyndication|adsbygoogle|doubleclick\.net|connect\.facebook\.net|fbq\s*\('
    r'|static\.hotjar\.com|matomo\.(js|php)|plausible\.io/js|cdn\.segment\.com|mixpanel\.com'
    r'|cloudflareinsights\.com|umami\.is|simpleanalytics',
    re.I)
CLARITY_TAG = re.compile(r'clarity\.ms/tag/')
CONSENTV2_DENIED = re.compile(
    r"clarity\(\s*['\"]consentv2['\"]\s*,\s*\{(?=[^}]*ad_Storage\s*:\s*['\"]denied['\"])"
    r"(?=[^}]*analytics_Storage\s*:\s*['\"]denied['\"])[^}]*\}")
ANCIEN_CLARITY = re.compile(r'__clarityLoad|consent-choice')

# Pages légales, reconnues à leur adresse (toutes langues du portefeuille).
P_PRIVACY = re.compile(r'(privacy|privacidad|privacidade|confidentialit|datenschutz|privacybeleid|riservatezza'
                       r'|prywatnos|integritet|personvern|tietosuoja|aporrito|aporrhto|gdpr)', re.I)
P_COOKIES = re.compile(r'(cookie|evaste|kakor|informasjonskapsl|ciasteczk)', re.I)
P_LEGAL = re.compile(r'(mentions-legales|legal|impressum|aviso-legal|note-legali|terms|cgu|conditions'
                     r'|voorwaarden|colofon|vilkar|villkor|kayttoehdot|agb|termini|termos|regulamin'
                     r'|nota-prawna|condiciones|disclaimer|oroi|nomik|colophon|imprint)', re.I)

NEGATION = re.compile(
    r"\b(no|not|none|never|without|nor|aucun|aucune|pas|ni|sans|jamais|kein|keine|keinen|keinem|nicht|ohne"
    r"|geen|niet|zonder|nessun|nessuna|non|senza|ningún|ninguna|ninguno|sin|nunca|nenhum|nenhuma|não|sem"
    r"|inga|ingen|inte|utan|ikke|uten|ei|eikä|ilman|nie|żadnych|żadnego|żadne|bez|δεν|κανένα|καμία|χωρίς"
    r"|μη|لا|ليس|بدون)\b", re.I)
COOKIE_MOT = re.compile(r'(cookie|evästeit|evästet|eväste|kakor|kaka|informasjonskapsl|ciasteczk|cookies)', re.I)
BANDEAU_MOT = re.compile(r'(bandeau|banni[eè]re|banner|baner|banier|bannière|pop-?up|μπάνερ|banderol|aviso de cookies'
                         r'|cookie[- ]?(settings|einstellungen|instellingen|preferences|inställningar|innstillinger'
                         r'|asetukset|ustawienia)|gérer les cookies|paramètres des cookies|gestione dei cookie'
                         r'|configurar cookies|gestionar cookies)', re.I)
CONSENT_MOT = re.compile(r'(consent|consentement|einwilligung|zustimmung|toestemming|consenso|consentimiento'
                         r'|consentimento|samtycke|samtykke|suostum|zgod[aęy]|συγκατάθεσ|موافقة)', re.I)
GOOGLE_MOT = re.compile(r'(google analytics|\bGA4\b|adsense|google ads|_ga\b|_gid\b)', re.I)

LANGS = ('fr', 'en', 'de', 'nl', 'it', 'es', 'pt', 'pl', 'fi', 'sv', 'nb', 'no', 'da', 'el', 'ar')


def sortie_de(site: Path):
    cands = [site / d for d in SORTIES if (site / d / 'index.html').is_file()]
    if not cands:
        return None
    return max(cands, key=lambda d: sum(1 for _ in d.rglob('*.html')))


def texte(html):
    t = re.sub(r'<(script|style|noscript|svg)[\s\S]*?</\1>', ' ', html, flags=re.I)
    corps = re.search(r'<main[\s\S]*?</main>', t, flags=re.I)
    t = corps.group(0) if corps else re.sub(r'<(nav|header|footer)[\s\S]*?</\1>', ' ', t, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'&nbsp;|&#160;| | ', ' ', t)
    t = re.sub(r'&[a-z#0-9]+;', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def phrases(t):
    return [p.strip() for p in re.split(r'(?<=[.!?;:])\s+', t) if p.strip()]


def lang_de(rel: str, html: str):
    m = re.search(r'<html[^>]*\blang=["\']([a-zA-Z]{2})', html)
    if m:
        return m.group(1).lower()
    seg = rel.split('/')[0]
    return seg if seg in LANGS else '?'


def slug(rel: str):
    parts = [p for p in rel.replace('index.html', '').replace('.html', '').split('/') if p]
    return parts[-1] if parts else ''


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    site = Path(sys.argv[1]).resolve()
    verbose = '--verbose' in sys.argv
    sortie = sortie_de(site)
    if not sortie:
        print(f'check-cookies : pas de build dans {site} — lancer le build avant.')
        sys.exit(1)

    erreurs = []
    html_files = [f for f in sortie.rglob('*.html')
                  if not any(a in f.as_posix() for a in ('/_archives/', '/archive/', '/old/', '/backup/'))]
    clarity_pages = 0
    langues = {}
    legales = {}  # lang -> {'privacy': [...], 'cookies': [...], 'legal': [...]}

    for f in html_files:
        rel = f.relative_to(sortie).as_posix()
        html = f.read_text(errors='ignore')
        if (m := BANDEAU.search(html)):
            erreurs.append(f'{rel} : bandeau ou gestion des cookies ({m.group(0)})')
        if (m := TRACEURS.search(html)):
            erreurs.append(f'{rel} : traceur interdit ({m.group(0)})')
        if (m := ANCIEN_CLARITY.search(html)):
            erreurs.append(f'{rel} : ancien chargement de Clarity soumis au bandeau ({m.group(0)})')
        tag = CLARITY_TAG.search(html)
        if tag:
            clarity_pages += 1
            c = CONSENTV2_DENIED.search(html)
            if not c or c.start() > tag.start():
                erreurs.append(f'{rel} : Clarity chargé sans consentv2 « denied » mis en file avant clarity.ms/tag/')
            # Contenu masqué par le code, pas seulement par le réglage du projet Clarity :
            # les pages légales l'affirment, il faut que ce soit vrai quel que soit le projet.
            if not re.search(r'<body[^>]*data-clarity-mask=["\']true', html, re.I):
                erreurs.append(f'{rel} : Clarity chargé sans data-clarity-mask="true" sur <body>')
        if 'http-equiv="refresh"' in html.lower() or re.search(r'<meta[^>]+refresh', html, re.I):
            continue
        lg = lang_de(rel, html)
        langues[lg] = langues.get(lg, 0) + 1
        s = slug(rel)
        if not s:
            continue
        kind = None
        if P_COOKIES.search(s):
            kind = 'cookies'
        elif P_PRIVACY.search(s):
            kind = 'privacy'
        elif P_LEGAL.search(s):
            kind = 'legal'
        if kind:
            legales.setdefault(lg, {'privacy': [], 'cookies': [], 'legal': []})[kind].append((rel, html))

    # Scripts servis : un traceur peut être injecté par un bundle.
    for f in sortie.rglob('*.js'):
        js = f.read_text(errors='ignore')
        m = re.search(r'googletagmanager\.com|google-analytics\.com|pagead2\.googlesyndication|connect\.facebook\.net'
                      r'|static\.hotjar\.com', js)
        if m:
            erreurs.append(f'{f.relative_to(sortie).as_posix()} : traceur interdit dans un script ({m.group(0)})')

    # Pages légales par langue servie (langues ayant au moins 3 pages).
    for lg, n in sorted(langues.items()):
        if n < 3:
            continue
        lp = legales.get(lg, {'privacy': [], 'cookies': [], 'legal': []})
        if not lp['privacy'] and not lp['cookies']:
            erreurs.append(f'[{lg}] aucune page de confidentialité ni de cookies')
        if not lp['legal']:
            erreurs.append(f'[{lg}] aucune page de mentions légales / CGU')
        for kind in ('cookies', 'privacy'):
            for rel, html in lp[kind]:
                t = texte(html)
                ph = phrases(t)
                if not any(COOKIE_MOT.search(p) and NEGATION.search(p) for p in ph):
                    erreurs.append(f'{rel} : ne dit pas qu\'aucun cookie n\'est déposé')
                if clarity_pages and 'clarity' not in t.lower():
                    erreurs.append(f'{rel} : Clarity est chargé mais la page ne le nomme pas')
        for kind in ('cookies', 'privacy', 'legal'):
            for rel, html in lp[kind]:
                for p in phrases(texte(html)):
                    if NEGATION.search(p):
                        continue
                    for nom, motif in (('bandeau', BANDEAU_MOT), ('consentement', CONSENT_MOT),
                                       ('Google Analytics / AdSense', GOOGLE_MOT)):
                        if motif.search(p) and (nom != 'bandeau' or True):
                            erreurs.append(f'{rel} : mention de {nom} : « {p[:140]} »')

    if erreurs:
        print(f'check-cookies : {len(erreurs)} défaut(s) dans {site.name}')
        for e in erreurs[: (None if verbose else 40)]:
            print('  - ' + e)
        if not verbose and len(erreurs) > 40:
            print(f'  … {len(erreurs) - 40} de plus (--verbose)')
        sys.exit(1)
    print(f'check-cookies : 0 défaut ({len(html_files)} pages, Clarity sur {clarity_pages}, '
          f'langues {", ".join(sorted(k for k, v in langues.items() if v >= 3))})')


if __name__ == '__main__':
    main()
