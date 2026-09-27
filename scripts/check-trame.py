"""Contrôle de la trame éditoriale d'un site construit (RECETTE-SITE.md).

Usage : python3 check-trame.py <dossier-site> [--verbose] [--json]

Complète `check-seo.py` (snippets, longueurs, sources officielles) et
`check-unique.py` (similarité de la prose). Ici on contrôle ce qu'aucun des deux
ne voyait, c'est-à-dire la trame que le lecteur perçoit :

  §7   FAQ    — une question ne paraît que sur une page ; 6 à 8 sur le pilier
                et sur les guides de 1 200 mots et plus, 3 à 5 sur les pages
                courtes ; réponse de 40 à 90 mots ; le JSON-LD `FAQPage`
                correspond aux questions visibles dans le HTML.
  §8   Auteur — encart auteur sur toutes les pages, `Person` avec `jobTitle` et
                `knowsAbout`, `founder` et `foundingDate` sur l'`Organization`,
                `publishingPrinciples`, `dateModified` sur les guides.
  §8.4 Confiance — date de mise à jour visible en haut ET en bas, disclaimer.
  §10.1 Template — marqueurs « site généré » (dégradé violet, cartes flottantes,
                émoji en puce, grille de features…). Trois sur une page = défaut.
  §18.2 Pied et haut de page — liens légaux obligatoires présents partout.
  HTML  — aucun nom de balise ni d'attribut ne porte d'accent (une passe de
                correction orthographique a déjà écrit `<détails>`, que le
                navigateur ignore silencieusement).

Le script lit `dist/`, jamais les sources : c'est le HTML servi qui compte, et
un `dist/` périmé a déjà masqué deux bugs bloquants (journal du 16/09/2026).
"""
import re, glob, html, sys, os, json, collections

site = sys.argv[1].rstrip('/')

# Astro sort dans `dist/`, Next en export statique dans `out/`. Sans ce choix, les
# cinq sites Next du portefeuille rendaient « 0 page, 0 a corriger » : un echec
# deguise en succes.
# Les dossiers d'archive ne sont pas servis : les compter reviendrait a auditer
# un site fantome, et fausserait l'unicite autant que le compte de pages.
ARCHIVES = ('_archives/', '/archive/', '/old/', '/backup/')
# Le dossier servi n'est pas toujours `dist` : salaryafter.com publie depuis
# `docs/` et calorierule.com depuis `output/`. Ne chercher que dist et out
# faisait contrôler un build obsolète, ou rien du tout (2026-09-26).
# Quand deux candidats coexistent, c'est celui qui porte le plus de pages.
SORTIES = ('dist', 'out', 'build', 'docs', 'output', '_site', 'www')


def _compte_pages(chemin):
    n = 0
    for racine, _, fichiers in os.walk(chemin):
        n += sum(1 for f in fichiers if f.endswith('.html'))
    return n


_candidats = [d for d in SORTIES
              if os.path.isdir(f'{site}/{d}') and os.path.isfile(f'{site}/{d}/index.html')]
if _candidats:
    sortie = max(_candidats, key=lambda d: _compte_pages(f'{site}/{d}'))
else:
    sortie = '' if os.path.isfile(f'{site}/index.html') else 'dist'
verbose = '--verbose' in sys.argv
as_json = '--json' in sys.argv

SERVICE = re.compile(
    r'/[a-z-]*(faq|questions|preguntas|veelgestelde|haeufige|about|a-propos|ueber-uns|over-ons|'
    r'sobre-nosotros|sobre(?=/|$)|methodology|methodik|methodologie|methode|metodologia|method|widget|'
    # Italien : les pages de service d'un site italien n'étaient pas reconnues,
    # si bien que « chi siamo » ou « glossario » se voyaient reprocher
    # l'absence de FAQ (calcolalordonetto.it, 2026-09-24).
    r'chi-siamo|contatti|glossario|glossary|termini|cookie-policy|informativa|'
    r'impressum|mentions|aviso|colofon|legal|privacy|datenschutz|confidentialite|privacidad|'
    # « cgu » : abréviation française de conditions générales d'utilisation, page de service
    # au même titre que /terms/ (cartegrisesimple.fr, 2026-09-20)
    r'cgu|cgv|'
    r'privacidade|cookies|terms|conditions|nutzungsbedingungen|terminos|termos|contact|editorial)', re.I)

# Liens que le pied de page doit porter sur toutes les pages (§8.4 identité
# légale, §12). On accepte n'importe laquelle des variantes linguistiques.
FOOTER_LINKS = {
    'legal':   r'(impressum|mentions-legales|aviso-legal|legal-notice|colofon|legal|'
               r'terms|conditions|voorwaarden|disclaimer|villkor|betingelser)',
    'privacy': r'(datenschutz|privacy|confidentialite|confidentialidade|privacidad|'
               r'privacidade|protection-donnees|gegevensbescherming|persondata|personvern|'
               r'integritetspolicy|privatliv)',
    'about':   r'(about|a-propos|ueber-uns|over-ons|sobre|chi-siamo|om-os|om-oss)',
    'method':  r'(method|methode|methodik|methodologie|metodolog|metod|metode)',
}

# §10.1 — réglages par défaut de Tailwind et des bibliothèques de composants.
TEMPLATE_MARKERS = {
    'dégradé violet/indigo': r'(from|via|to)-(purple|violet|indigo|fuchsia)-\d',
    'carte flottante rounded-2xl+shadow-lg': r'rounded-(2xl|3xl)[^"]*shadow-(lg|xl|2xl)',
    'backdrop-blur': r'backdrop-blur',
    'badge pilule multicolore': r'rounded-full[^"]*bg-(pink|purple|indigo|teal|cyan)-\d',
    'grille de features 3 colonnes': r'grid-cols-3[^"]*gap-\d[^"]*(feature|card)',
}
# Émoji en tête de puce ou de titre : marqueur le plus visible du texte généré.
EMOJI_BULLET = re.compile(
    r'<(li|h[2-4])[^>]*>\s*(<[^>]+>\s*)?[\U0001F300-\U0001FAFF✀-➿⬀-⯿]')

DISCLAIMER = re.compile(
    r'(estimation|indicati[efv]|orientativ|ne constitu|do not constitute|uppskattning|ersätter inte|anslag|erstatter ikke|目安|仅供参考|참고용|ориентировочн|не заменяет|справочный|अनुमान|अनुमानित|অনুমান|تقدير|إرشادية|schätzung|richtwert|schatting|indicação|'
    r'no sustituye|ne remplace|ersetzt kein|vervangt geen|does not replace|'
    r'not (?:legal|financial|professional|tax|medical|veterinary) advice|unverbindlich|'
    # « stellt keine Anlageberatung dar », « stellt keine Steuerberatung dar » : la
    # tournure allemande courante, qui n'emploie ni « ersetzt » ni « unverbindlich ».
    r'stellt kein\w* [^.]{0,40}(?:beratung|empfehlung) dar|'
    r'estimates? only|guide only|for guidance|does not constitute|'
    r'not a substitute for|no substitute for|informational purposes only|'
    r'a titre informatif|à titre informatif|nur zur information)', re.I)

ISO_DATE = re.compile(r'\b20\d{2}-\d{2}-\d{2}\b')
# La date de mise à jour est désormais écrite dans la langue du site
# (« 4 de julho de 2026 »), le format ISO restant dans l'attribut `datetime`.
# Chercher la date dans le texte visible ne prouvait donc plus rien : c'est
# l'élément <time> daté qu'il faut trouver, en haut comme en bas.
TIME_DATE = re.compile(r'<time[^>]+datetime="20\d{2}-\d{2}-\d{2}', re.I)


def _norm(t: str) -> str:
    """Texte comparable : sans espaces, et sans les signes que la passe
    typographique du build reecrit apres coup."""
    t = t.replace('\u2014', ',')
    return re.sub(r'[\s,]+', '', t)


def main_words(doc: str) -> int:
    """Longueur du contenu principal, en mots.

    Japonais, coréen, chinois : ces langues n'emploient pas l'espace comme séparateur,
    un comptage par espaces renvoyait 30 mots pour une page de 3 000 caractères et
    faisait passer toutes les pages CJK pour du contenu mince (gfp, 2026-09-20).
    Équivalence retenue, la même que check-seo : un caractère plein vaut deux lettres.
    """
    m = re.search(r'<main[^>]*>(.*?)</main>', doc, re.S)
    t = strip_tags(m.group(1) if m else doc)
    if re.search(r'<html[^>]*\blang="(ja|ko|zh)', doc, re.I):
        return len(re.sub(r'\s+', '', t)) // 2
    return len(t.split())


def strip_tags(t: str) -> str:
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S)
    t = html.unescape(re.sub(r'<[a-zA-Z/!][^>]*>', ' ', t))   # « (< 5 ans) » n'est pas une balise
    # Apostrophes et espaces typographiques : le JSON-LD et le HTML n'emploient
    # pas toujours les mêmes, et la comparaison échouait sur ce seul détail.
    t = t.replace('\u2019', "'").replace('\u202f', ' ').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', t).strip()


def kind(path: str) -> str:
    if SERVICE.search(path):
        return 'service'
    if path.strip('/').count('/') == 0:
        return 'pilier'
    return 'secondaire'


def jsonld(doc: str):
    """Tous les objets JSON-LD de la page, arbre entièrement aplati.

    Les nœuds utiles sont rarement à la racine : `Person` vit dans
    `Organization.founder` ou `WebApplication.author`, et on manquerait
    l'essentiel en ne lisant que le premier niveau et `@graph`.
    """
    out = []

    def descendre(node):
        if isinstance(node, list):
            for n in node:
                descendre(n)
        elif isinstance(node, dict):
            out.append(node)
            for v in node.values():
                if isinstance(v, (dict, list)):
                    descendre(v)

    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', doc, re.S):
        try:
            descendre(json.loads(html.unescape(m.group(1))))
        except Exception:
            out.append({'@type': '__INVALIDE__'})
    return out


def typed(nodes, name):
    """Le nœud le plus riche de ce type, pas le premier rencontré.

    Un même type apparaît souvent deux fois : une référence minimale
    (`WebApplication.author` = nom seul) et la fiche complète. Prendre le
    premier dans l'ordre de l'arbre faisait passer la fiche complète pour
    incomplète.
    """
    candidats = [n for n in nodes
                 if name == n.get('@type', '')
                 or (isinstance(n.get('@type'), list) and name in n['@type'])]
    return max(candidats, key=len, default=None)


pages, questions_seen = [], collections.defaultdict(list)

# ---- §13 : la favicon est declaree sur toutes les pages ------------------
# Le robot qui collecte les favicons interroge la racine du domaine et
# /favicon.ico avant de lire quoi que ce soit d'autre. Une page qui ne declare
# rien laisse Search Console afficher une icone generique pendant des semaines,
# et la marque disparait des resultats de recherche.
# Constate le 2026-09-26 : huit sites du portefeuille declaraient bien leur
# favicon sur leurs pages de contenu et rien du tout sur leur racine, qui est
# justement la premiere porte frappee par le robot.
ICONE = re.compile(r'<link[^>]*rel="[^"]*\bicon\b[^"]*"[^>]*href="([^"]+)"', re.I)

def controle_favicon(doc):
    """Les defauts de declaration d'icone d'une page. Liste vide si tout va bien.

    Une declaration commentee n'est pas une declaration : les 98 pages
    d'uaepriceindex.com portaient un `<!-- <link rel="apple-touch-icon" ... > -->`
    laisse en attente d'un PNG, et le controle la comptait comme une icone promise
    puis absente (2026-09-27).
    """
    doc = re.sub(r'<!--.*?-->', ' ', doc, flags=re.S)
    refs = [h for h in ICONE.findall(doc)]
    if not refs:
        return ['aucune favicon declaree']
    manquants = []
    for href in {r.split('?')[0] for r in refs}:
        if href.startswith(('http://', 'https://', 'data:')):
            continue  # hors du site : on ne peut pas le verifier ici
        chemin = f"{site}/{sortie}/{href.lstrip('/')}"
        if not os.path.isfile(chemin):
            manquants.append(href)
    return [f'favicon declaree mais absente du build : {h}' for h in sorted(manquants)]

for f in sorted(x for x in glob.glob(f'{site}/{sortie}/**/index.html', recursive=True)
                if not any(a in x for a in ARCHIVES)):
    doc = open(f, encoding='utf-8').read()
    rel = os.path.relpath(os.path.dirname(f), f'{site}/{sortie}').replace(os.sep, '/')
    path = '/' + ('' if rel == '.' else rel + '/')
    if path == '/' or 'http-equiv="refresh"' in doc:
        continue                                   # racine ou page de redirection
    noindex = 'content="noindex' in doc
    k = kind(path)
    nodes = jsonld(doc)
    flags = []

    # ---- HTML : aucun nom de balise ni d'attribut ne porte d'accent -------
    # Le 2026-09-24, une passe de correction d'accents a transformé 70 balises
    # `<details>` en `<détails>` sur netsalaire.com et salairenet.ch. Le
    # navigateur traite l'inconnue comme un `<span>` : l'accordéon reste ouvert,
    # la FAQ s'affiche dépliée, et rien ne le signale. Aucun nom de balise ni
    # d'attribut HTML ne comporte d'accent : un accent y est donc toujours une
    # faute, et un contrôle d'une ligne suffit à la rendre impossible.
    accents = {m.group(1) for m in re.finditer(r'<\s*/?\s*([A-Za-zÀ-ÿ][-\wÀ-ÿ]*)', doc)
               if re.search(r'[À-ÿ]', m.group(1))}
    accents |= {m.group(1) for m in re.finditer(r'\s([A-Za-zÀ-ÿ][-\wÀ-ÿ]*)=["\']', doc)
                if re.search(r'[À-ÿ]', m.group(1))}
    for nom in sorted(accents):
        flags.append(f'balise ou attribut accentué : « {nom} » n\'existe pas en HTML')

    # ---- §7 FAQ ---------------------------------------------------------
    faq = typed(nodes, 'FAQPage')
    visible_text = strip_tags(re.sub(r'<script[^>]*>.*?</script>', ' ', doc, flags=re.S))
    visible_nospace = _norm(visible_text)
    visible_q = {strip_tags(m.group(1)).rstrip('  ?¿')
                 for m in re.finditer(r'<(?:summary|dt|h[34])[^>]*>(.*?)</(?:summary|dt|h[34])>',
                                      doc, re.S)}
    cjk = re.search(r'<html[^>]*\blang="(ja|ko|zh)', doc, re.I) is not None
    if faq:
        qa = faq.get('mainEntity', [])
        qa = qa if isinstance(qa, list) else [qa]
        for item in qa:
            q = strip_tags(str(item.get('name', '')))
            a = item.get('acceptedAnswer', {})
            a = strip_tags(str(a.get('text', '') if isinstance(a, dict) else a))
            if q:
                if not noindex:
                    # Une question partagée avec des pages en noindex ne
                    # concurrence rien : elles ne sont jamais servies à un
                    # moteur (howmanyof.com, 2026-09-25).
                    questions_seen[q.lower().rstrip(' ?¿!.')].append(path)
            # Japonais, coréen, chinois : compter les mots séparés par une espace n'a pas
            # de sens (le japonais n'en met pas, le coréen agglutine). On mesure alors en
            # caractères, avec la même équivalence que check-seo : un caractère plein vaut
            # environ deux lettres latines, donc 40-90 mots ≈ 120-280 caractères.
            if cjk:
                n = len(a.replace(' ', ''))
                if not 120 <= n <= 280:
                    flags.append(f'réponse FAQ {n} caractères ∉[120,280] : « {q[:40]} »')
            else:
                n = len(a.split())
                if not 40 <= n <= 90:
                    flags.append(f'réponse FAQ {n} mots ∉[40,90] : « {q[:40]} »')
            # §7 : le balisage doit correspondre au visible. La question peut être dans un
            # <summary>, un titre, ou un bouton d'accordéon : on la cherche dans tout le texte.
            if q and not any(q.rstrip(' ?¿') in v or v in q for v in visible_q) \
                    and q.rstrip(' ?¿') not in visible_text:
                flags.append(f'question FAQ absente du HTML visible : « {q[:40]} »')
            # La réponse aussi doit être dans le HTML servi : un accordéon qui ne l'insère
            # qu'au clic déclare à Google un texte que la page ne contient pas
            # (116 pages d'epargnemalin.fr, 2026-09-19).
            # Comparaison sans les espaces : une balise fermée juste avant un point
            # (« <strong>63 ans</strong>. ») laisse « 63 ans . » dans le texte extrait.
            # `typo-nbsp.mjs` remplace le tiret cadratin par une virgule dans le
            # texte visible, mais saute les <script> : le JSON-LD garde donc le
            # tiret et la comparaison echouait sur toute reponse qui en
            # contenait un. Faux positif vu le 2026-09-25 sur la page d'accueil
            # francaise de fdeinsider.com. On normalise les deux cotes de la
            # meme facon avant de comparer.
            if a and _norm(a[:80]) not in visible_nospace:
                flags.append(f'réponse FAQ absente du HTML servi : « {q[:40]} »')
        # Un guide de 1 200 mots et plus est un pilier secondaire : il porte
        # assez de matière pour 6 à 8 questions, et les élaguer à 5 reviendrait
        # à jeter du contenu utile (journal du 17/09/2026).
        # Le pilier doit porter 6 à 8 questions. Un guide de 1 200 mots ou plus
        # a le droit d'aller jusqu'à 8 sans y être contraint : le plafond est
        # relevé, le plancher reste celui d'une page secondaire.
        lo, hi = (6, 8) if k == 'pilier' else (3, 8 if main_words(doc) >= 1200 else 5)
        if k != 'service' and not lo <= len(qa) <= hi:
            flags.append(f'{len(qa)} questions ∉[{lo},{hi}] ({k})')
    elif k != 'service' and not noindex:
        flags.append('pas de FAQPage')

    # ---- §8 E-E-A-T -----------------------------------------------------
    if not noindex:
        # Décision du 2026-09-20 : l'auteur du portefeuille n'est plus une personne
        # physique mais la société éditrice. Un `Person` reste accepté (sites non
        # encore migrés) ; à défaut, une `Organization` complète tient le rôle.
        person = typed(nodes, 'Person')
        org = typed(nodes, 'Organization')
        if person:
            for champ in ('jobTitle', 'knowsAbout'):
                if not person.get(champ):
                    flags.append(f'Person sans {champ}')
        elif not org:
            flags.append('ni Person ni Organization comme auteur')
        if org:
            if not org.get('foundingDate'):
                flags.append('Organization sans foundingDate')
            if not org.get('publishingPrinciples'):
                flags.append('Organization sans publishingPrinciples')
            # `knowsAbout` porte l'expertise quand l'auteur est la société. Les sites
            # déclarent souvent deux Organization (l'éditrice et celle du site) : il
            # suffit que l'une d'elles la porte (brutanet.fr, 2026-09-20).
            if not person and not any(
                    n.get('knowsAbout') for n in nodes
                    if 'Organization' in str(n.get('@type', ''))):
                flags.append('Organization auteur sans knowsAbout')
        # Encart auteur visible, pas seulement dans le JSON-LD.
        if not re.search(r'(rel="author"|itemprop="author"|class="[^"]*author|data-author'
                          r'|src="/team/)', doc):
            flags.append('pas d\'encart auteur visible')
        # §8.2 : dateModified sur les guides et pages secondaires.
        if k == 'secondaire' and not any(n.get('dateModified') for n in nodes):
            flags.append('pas de dateModified')

    # ---- §8.4 confiance : date visible en haut ET en bas -----------------
    if not noindex:
        # « En haut » veut dire à hauteur du titre, pas forcément avant lui : la
        # signature « Par X · Mis à jour le … » se place presque toujours juste
        # sous le <h1>. On garde donc les 2 000 caractères qui suivent sa
        # fermeture (netsalaire.com, 2026-09-24).
        head = doc[:doc.find('</h1>') + 2000] if '</h1>' in doc else doc[:4000]
        foot = doc[doc.rfind('<footer'):] if '<footer' in doc else doc[-4000:]
        if not (TIME_DATE.search(head) or ISO_DATE.search(strip_tags(head))):
            flags.append('pas de date de mise à jour en haut')
        if not (TIME_DATE.search(foot) or ISO_DATE.search(strip_tags(foot))):
            flags.append('pas de date de mise à jour en bas')
        if not DISCLAIMER.search(strip_tags(doc)):
            flags.append('pas de disclaimer')

    # ---- haut et pied de page -------------------------------------------
    embed = path.startswith('/embed/')
    if embed:
        # Une page servie en iframe n'affiche jamais d'icone : l'onglet est
        # celui du site hote. On ne lui demande donc pas de favicon.
        pages.append({'path': path, 'kind': 'iframe', 'noindex': noindex, 'flags': flags})
        continue
    # Une page en noindex (console d'administration, page technique) n'a pas à porter
    # l'en-tête et le pied publics : elle n'est pas indexée, la règle ne la vise pas.
    # La favicon non plus : la regle existe pour le robot qui collecte les icones,
    # et ce robot ne visite pas une page qu'il n'indexe pas (netsalaire.com et
    # bmi-imc.com, dont la seule page signalee etait /admin/, 2026-09-26).
    if noindex:
        pages.append({'path': path, 'kind': k, 'noindex': noindex, 'flags': flags})
        continue

    flags.extend(controle_favicon(doc))
    if '<header' not in doc:
        flags.append('pas de <header>')
    if '<nav' not in doc:
        flags.append('pas de <nav>')
    if '<footer' not in doc:
        flags.append('pas de <footer>')
    else:
        foot = doc[doc.rfind('<footer'):]
        for nom, motif in FOOTER_LINKS.items():
            if not re.search(rf'href="[^"]*{motif}', foot, re.I):
                flags.append(f'pied sans lien {nom}')

    # ---- §10.1 marqueurs de template ------------------------------------
    marqueurs = [nom for nom, motif in TEMPLATE_MARKERS.items()
                 if re.search(motif, doc, re.I)]
    if EMOJI_BULLET.search(doc):
        marqueurs.append('émoji en tête de puce ou de titre')
    if len(marqueurs) >= 3:
        flags.append('template : ' + ', '.join(marqueurs))
    elif marqueurs and verbose:
        flags.append('(template, sous le seuil) ' + ', '.join(marqueurs))

    pages.append({'path': path, 'kind': k, 'noindex': noindex, 'flags': flags})

# ---- §10.1 : la page racine est une page, pas un gabarit -----------------
# Elle redirige et porte noindex, mais elle reste la première URL du domaine :
# sans JS elle est tout ce que voit le visiteur, et sur un site multilingue elle
# est le seul chemin vers les autres langues.
racine = f'{site}/{sortie}/index.html'
if os.path.exists(racine):
    doc = open(racine, encoding='utf-8').read()
    flags = []

    m = re.search(r'<title>(.*?)</title>', doc, re.S)
    titre = strip_tags(m.group(1)).strip() if m else ''
    if not titre:
        flags.append('pas de <title>')
    elif titre.lower() in {'redirect', 'redirection', 'index', 'home'}:
        flags.append(f'titre de gabarit : « {titre} » — mettre le nom du site')

    m = re.search(r'rel="canonical"[^>]*href="([^"]*)"', doc)
    canon = m.group(1) if m else ''
    if not canon:
        flags.append('pas de canonical')
    elif not canon.startswith('http'):
        flags.append(f'canonical relatif ({canon}) — doit être absolu')

    # Texte d'un lien : visible, ou aria-label / title / alt d'image (lien-icône accessible).
    liens = [(strip_tags(t).strip() + ' ' + ' '.join(re.findall(r'(?:aria-label|title|alt)="([^"]*)"', attrs + t))).strip()
             for attrs, t in re.findall(r'<a\b([^>]*)>(.*?)</a>', doc, re.S)]
    muets = [t for t in liens if not re.search(r'\w{2}', t)]
    if muets:
        flags.append(f'{len(muets)} lien(s) sans texte lisible '
                     f'({", ".join(repr(t) for t in muets[:3])})')

    locales = sorted(d for d in os.listdir(f'{site}/{sortie}')
                     if re.fullmatch(r'[a-z]{2}', d)
                     and os.path.isdir(f'{site}/{sortie}/{d}'))
    if len(liens) < len(locales):
        flags.append(f'{len(locales)} langue(s) publiée(s) ({", ".join(locales)}) '
                     f'mais {len(liens)} lien(s) : une langue est inatteignable sans JS')

    flags.extend(controle_favicon(doc))

    pages.append({'path': '/', 'kind': 'racine', 'noindex': True, 'flags': flags})

# ---- §7 : une question ne paraît que sur une seule page ------------------
doublons = {q: p for q, p in questions_seen.items() if len(set(p)) > 1}
for q, paths in doublons.items():
    for p in set(paths):
        for page in pages:
            if page['path'] == p:
                page['flags'].append(f'question FAQ partagée avec {len(set(paths))-1} '
                                     f'autre(s) page(s) : « {q[:50]} »')

if as_json:
    print(json.dumps({'site': site, 'pages': pages,
                      'faq_doublons': {q: sorted(set(p)) for q, p in doublons.items()}},
                     ensure_ascii=False, indent=1))
    sys.exit(0)

mauvaises = 0
for page in pages:
    if page['flags']:
        mauvaises += 1
        print(f"!! {page['path']:52s} {page['kind']:11s}")
        for fl in page['flags']:
            print(f"     · {fl}")
    elif verbose:
        print(f"   {page['path']:52s} {page['kind']:11s} ok")

print(f"\n{site} : {len(pages)} pages, {mauvaises} à corriger, "
      f"{len(doublons)} question(s) de FAQ recyclée(s)")
sys.exit(1 if mauvaises else 0)
