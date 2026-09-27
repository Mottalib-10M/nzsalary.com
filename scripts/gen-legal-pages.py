# -*- coding: utf-8 -*-
"""Génère les pages légales des 7 sites : mention légale du pays (mentions légales,
Impressum, aviso legal, disclaimer, terms of use) et politique de confidentialité.

Ces pages existaient, mais sous forme d'ébauches de 120 à 330 mots contenant des
crochets « [à compléter] » et des mentions conditionnelles « [Si activé :] » : elles
n'auraient satisfait ni la LCEN, ni le §5 DDG, ni la LSSI, ni le RGPD, et auraient été
mises en ligne telles quelles. Elles sont réécrites ici en fonction de la juridiction
de chaque site, et l'identité de l'éditeur n'y est plus recopiée à la main : elle vient
du bloc LEGAL de `src/data/site-config.ts` via le composant `LegalIdentity`, si bien
qu'un champ non renseigné ressort en jaune sur la page et fait échouer `npm run check:legal`.

Plan §2.2 (pages de service obligatoires) et §4.3 (« mention légale adaptée au pays »).
"""
import os

ROOT = '/Users/mottalib/Documents/simulateurs-2026'

# terms_id : identifiant de route de la mention légale (le site suisse dit « imprint »)
# name     : expression Astro donnant le nom du site dans la langue
SITES = {
    'ch-lohnrechner':      dict(langs=['de', 'fr'], terms_id='imprint',
                                name={'de': 'SITE_NAME', 'fr': 'SITE_NAME_FR'}),
    'de-arbeitslosengeld': dict(langs=['de'], terms_id='terms', name={'de': 'SITE_NAMES[lang]'}),
    'fr-simulateur-are':   dict(langs=['fr'], terms_id='terms', name={'fr': 'SITE_NAMES[lang]'}),
    'es-calculadora-paro': dict(langs=['es'], terms_id='terms', name={'es': 'SITE_NAMES[lang]'}),
    'nl-ww-berekenen':     dict(langs=['nl'], terms_id='terms', name={'nl': 'SITE_NAMES[lang]'}),
    'ca-ei-calculator':    dict(langs=['en', 'fr'], terms_id='terms',
                                name={'en': 'SITE_NAMES[lang]', 'fr': 'SITE_NAMES[lang]'}),
    'au-final-pay':        dict(langs=['en'], terms_id='terms', name={'en': 'SITE_NAMES[lang]'}),
}

# Chemins réels des pages, relevés dans chaque src/i18n/routes.ts
PATHS = {
    ('ch-lohnrechner', 'de'):      dict(terms='/de/impressum/', privacy='/de/datenschutz/'),
    ('ch-lohnrechner', 'fr'):      dict(terms='/fr/mentions-legales/', privacy='/fr/protection-donnees/'),
    ('de-arbeitslosengeld', 'de'): dict(terms='/de/impressum/', privacy='/de/datenschutz/'),
    ('fr-simulateur-are', 'fr'):   dict(terms='/fr/mentions-legales/', privacy='/fr/confidentialite/'),
    ('es-calculadora-paro', 'es'): dict(terms='/es/aviso-legal/', privacy='/es/privacidad/'),
    ('nl-ww-berekenen', 'nl'):     dict(terms='/nl/disclaimer/', privacy='/nl/privacy/'),
    ('ca-ei-calculator', 'en'):    dict(terms='/en/terms/', privacy='/en/privacy/'),
    ('ca-ei-calculator', 'fr'):    dict(terms='/fr/conditions/', privacy='/fr/confidentialite/'),
    ('au-final-pay', 'en'):        dict(terms='/en/terms/', privacy='/en/privacy/'),
}

# Titre (≤ 60 caractères, nom du site compris) et meta description (140–155 caractères)
META = {}
BODIES = {}

# --------------------------------------------------------------------------- #
# France — simulateur-are.fr
# LCEN art. 6 III-1 pour les mentions légales, RGPD art. 13 pour l'information.
# --------------------------------------------------------------------------- #
META['fr-simulateur-are', 'fr', 'terms'] = (
    'Mentions légales – ${SITE_NAMES[lang]}',
    'Éditeur, directeur de la publication, hébergeur, propriété intellectuelle, limites de responsabilité et droit applicable à ce simulateur d’allocation chômage.')
BODIES['fr-simulateur-are', 'fr', 'terms'] = """    <h1>Mentions légales</h1>
    <p>Informations publiées en application de l’article 6 III-1 de la loi n° 2004-575 du 21 juin 2004 pour la confiance dans l’économie numérique.</p>

    <h2>Éditeur du site</h2>
    <LegalIdentity lang={lang} />
    <p>Directeur de la publication : {AUTHOR_NAME}, responsable à ce titre de l’ensemble des contenus éditoriaux publiés sur {SITE_URL}.</p>

    <h2>Hébergeur</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>Objet du site et absence de conseil</h2>
    <p>Ce site met à disposition un simulateur d’allocation d’aide au retour à l’emploi et des guides explicatifs, à titre gratuit et informatif. Les résultats sont des <strong>estimations</strong> calculées à partir de la réglementation d’assurance chômage publiée par l’Unédic et France Travail. Ils ne constituent ni un conseil juridique, fiscal ou financier personnalisé, ni une décision, ni un engagement de qui que ce soit sur le montant ou la durée de vos droits. Seule la notification de France Travail détermine vos droits réels. La méthode, les paramètres retenus et les situations volontairement non couvertes sont décrits dans notre <a href={route('method', lang)}>méthodologie</a>.</p>

    <h2>Limites de responsabilité</h2>
    <p>Nous mettons à jour les paramètres à chaque revalorisation et vérifions les calculs sur des cas de référence, mais nous ne garantissons pas l’absence d’erreur ni l’exhaustivité. La réglementation évolue, et certaines situations (activité à l’étranger, intermittence, contrats particuliers) obéissent à des règles que le simulateur n’applique pas. L’éditeur ne peut être tenu responsable des conséquences d’une décision prise sur la seule base d’une estimation, ni d’une interruption du service. Toute erreur constatée peut nous être signalée par la page <a href={route('contact', lang)}>contact</a> : la procédure de correction figure dans notre <a href={route('editorial', lang)}>charte éditoriale</a>.</p>

    <h2>Propriété intellectuelle</h2>
    <p>La structure du site, les textes, les graphismes et le code source sont protégés par le code de la propriété intellectuelle et restent la propriété de l’éditeur. Toute reproduction ou réutilisation, totale ou partielle, sans autorisation préalable, est interdite, à l’exception des courtes citations accompagnées d’un lien vers la page d’origine. Les textes réglementaires et les données publiques cités sont reproduits sous <a href="https://www.etalab.gouv.fr/licence-ouverte-open-licence" rel="noopener" target="_blank">Licence ouverte Etalab</a>, dans les conditions qu’elle prévoit.</p>

    <h2>Intégration du simulateur</h2>
    <p>Le simulateur peut être intégré gratuitement dans une iframe sur un autre site, à condition de conserver le lien visible vers la page d’origine et de ne pas laisser croire que l’outil émane d’un organisme public. Écrivez-nous pour obtenir le code d’intégration.</p>

    <h2>Liens externes</h2>
    <p>Les liens vers des sites tiers sont fournis pour faciliter la vérification des sources. Nous n’exerçons aucun contrôle sur leur contenu et déclinons toute responsabilité à leur égard.</p>

    <h2>Données personnelles et cookies</h2>
    <p>Les saisies du simulateur ne quittent jamais votre navigateur. Le traitement des données de connexion, la mesure d’audience et vos droits sont décrits dans la <a href={route('privacy', lang)}>politique de confidentialité</a> et la page <a href={route('cookies', lang)}>cookies</a>.</p>

    <h2>Signalement d’un contenu illicite</h2>
    <p>Tout contenu manifestement illicite peut être signalé à <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>, avec l’adresse exacte de la page et le motif. Nous accusons réception et traitons le signalement sans délai.</p>

    <h2>Droit applicable</h2>
    <p>Les présentes mentions sont soumises au droit français. À défaut de résolution amiable, tout litige relève des juridictions compétentes de {LEGAL.jurisdiction}. Dernière mise à jour : {LAST_UPDATED}.</p>"""

META['fr-simulateur-are', 'fr', 'privacy'] = (
    'Politique de confidentialité – ${SITE_NAMES[lang]}',
    'Quelles données ce site traite, sur quelle base juridique, combien de temps, qui y accède, et comment exercer vos droits RGPD ou saisir la CNIL.')
BODIES['fr-simulateur-are', 'fr', 'privacy'] = """    <h1>Politique de confidentialité</h1>
    <p>Cette page décrit les traitements de données à caractère personnel liés à l’utilisation de {SITE_URL}, conformément aux articles 12 à 14 du règlement (UE) 2016/679 (RGPD) et à la loi n° 78-17 du 6 janvier 1978 modifiée.</p>

    <h2>1. Responsable du traitement</h2>
    <LegalIdentity lang={lang} />
    <p>Pour toute question relative à vos données : <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. Compte tenu de la nature du site, aucun délégué à la protection des données n’a été désigné : les conditions de l’article 37 du RGPD ne sont pas réunies.</p>

    <h2>2. Ce que le simulateur ne fait pas</h2>
    <p>Le calcul est intégralement exécuté par votre navigateur. Salaires, durée d’affiliation, âge, situation familiale et revenu fiscal de référence <strong>ne sont transmis à aucun serveur</strong>, ne sont enregistrés nulle part et ne sont associés à aucun identifiant. Nous ne créons pas de compte, ne demandons pas d’inscription et ne collectons aucune donnée relative à votre situation professionnelle. Si vous utilisez le lien de partage, vos saisies sont encodées dans l’URL : ne le transmettez qu’aux personnes de votre choix.</p>

    <h2>3. Traitements effectivement réalisés</h2>
    <h3>Journaux de connexion</h3>
    <p>L’hébergeur enregistre, à chaque requête, l’adresse IP, la date et l’heure, la page demandée, le code de réponse, le navigateur et le référent. Finalité : sécurité du service, prévention des abus et diagnostic des pannes. Base juridique : l’intérêt légitime de l’éditeur à maintenir un service disponible et sûr (art. 6-1 f du RGPD). Durée de conservation : 30 jours au maximum, puis suppression.</p>
    <h3>Mesure d’audience</h3>
    <p>Si vous y consentez, l’audience est mesurée avec Google Analytics 4, en mode de consentement Google et avec anonymisation de l’adresse IP, aux seules fins de savoir quelles pages sont consultées et par quel canal. Base juridique : votre consentement (art. 6-1 a du RGPD et art. 82 de la loi Informatique et Libertés). Sans consentement, aucun cookie de mesure n’est déposé. Durée de conservation des données d’audience : 14 mois.</p>
    <h3>Publicité</h3>
    <p>Des emplacements publicitaires peuvent être servis par Google AdSense. Avec votre consentement, Google peut déposer des cookies de personnalisation ; sans consentement, seules des annonces non personnalisées sont diffusées. Le traitement opéré par Google pour son propre compte est décrit dans ses <a href="https://policies.google.com/technologies/ads" rel="noopener" target="_blank">règles publicitaires</a>.</p>
    <h3>Messages que vous nous envoyez</h3>
    <p>Lorsque vous écrivez à l’adresse de contact, votre adresse électronique et le contenu de votre message sont traités pour vous répondre et, le cas échéant, corriger une erreur de calcul. Base juridique : l’intérêt légitime à répondre aux sollicitations. Conservation : trois ans à compter du dernier échange.</p>

    <h2>4. Destinataires et sous-traitants</h2>
    <p>Aucune donnée n’est vendue, louée ni cédée. Y accèdent uniquement l’hébergeur, agissant comme sous-traitant au sens de l’article 28 du RGPD, et, en cas de consentement, Google Ireland Limited pour la mesure d’audience et la publicité. Ces prestataires sont liés par contrat et n’utilisent les données que sur instruction, à l’exception de Google qui agit comme responsable conjoint ou distinct pour certaines finalités publicitaires qu’il documente lui-même.</p>

    <h2>5. Transferts hors Union européenne</h2>
    <p>Les traitements Google peuvent impliquer un transfert vers les États-Unis. Ils sont encadrés par les clauses contractuelles types de la Commission européenne et par la certification de Google LLC au titre du cadre de protection des données UE–États-Unis (EU–U.S. Data Privacy Framework). Vous pouvez éviter tout transfert en refusant la mesure d’audience et la publicité depuis le bandeau cookies.</p>

    <h2>6. Vos droits</h2>
    <p>Vous disposez des droits d’accès, de rectification, d’effacement, de limitation, d’opposition et de portabilité prévus aux articles 15 à 22 du RGPD, ainsi que du droit de définir des directives relatives au sort de vos données après votre décès. Le consentement donné au bandeau cookies peut être retiré à tout moment, aussi facilement qu’il a été donné. Exercez ces droits à l’adresse <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> ; nous répondons dans un délai d’un mois. En pratique, en l’absence de compte utilisateur, nous ne disposons le plus souvent d’aucune donnée permettant de vous identifier : nous vous le dirons alors explicitement.</p>
    <p>Vous pouvez introduire une réclamation auprès de la {LEGAL.supervisoryAuthority} : <a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>.</p>

    <h2>7. Absence de décision automatisée et de profilage</h2>
    <p>Le résultat affiché par le simulateur est un calcul effectué à votre demande, sur vos propres saisies, dans votre navigateur. Il ne produit aucun effet juridique et ne constitue pas une décision automatisée au sens de l’article 22 du RGPD. Nous ne pratiquons aucun profilage.</p>

    <h2>8. Mineurs</h2>
    <p>Le site s’adresse à des personnes majeures ou à des jeunes actifs entrant sur le marché du travail. Il ne s’adresse pas aux enfants et ne collecte sciemment aucune donnée les concernant.</p>

    <h2>9. Sécurité et modifications</h2>
    <p>Le site est servi exclusivement en HTTPS et ne comporte aucune base de données d’utilisateurs. Cette politique peut être modifiée pour tenir compte d’évolutions légales ou techniques ; la date ci-dessous fait foi. Dernière mise à jour : {LAST_UPDATED}.</p>"""

# --------------------------------------------------------------------------- #
# Allemagne — arbeitslosengeld-berechnen.de
# §5 DDG (ex-§5 TMG) et §18 Abs. 2 MStV pour l'Impressum, DSGVO Art. 13 pour la
# Datenschutzerklärung, §36 VSBG pour la mention de règlement des litiges.
# --------------------------------------------------------------------------- #
META['de-arbeitslosengeld', 'de', 'terms'] = (
    'Impressum – ${SITE_NAMES[lang]}',
    'Anbieterkennzeichnung nach §5 DDG und §18 MStV: Betreiber, Kontakt, inhaltlich Verantwortlicher, Haftung für Inhalte und Links, Urheberrecht.')
BODIES['de-arbeitslosengeld', 'de', 'terms'] = """    <h1>Impressum</h1>
    <p>Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG) und § 18 Abs. 2 Medienstaatsvertrag (MStV).</p>

    <h2>Anbieter</h2>
    <LegalIdentity lang={lang} />
    <p>Inhaltlich verantwortlich im Sinne des § 18 Abs. 2 MStV: {AUTHOR_NAME}, unter der vorstehenden Anschrift.</p>

    <h2>Hosting</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>Zweck des Angebots und kein Rechtsrat</h2>
    <p>Dieses Angebot stellt einen kostenlosen Rechner für das Arbeitslosengeld I sowie erläuternde Ratgeber bereit. Die Ergebnisse sind <strong>unverbindliche Schätzungen</strong> auf Grundlage des SGB III, der Leistungsentgeltverordnung und des jeweils gültigen Programmablaufplans zur Lohnsteuer. Sie ersetzen weder den Bescheid der Agentur für Arbeit noch eine Rechts-, Steuer- oder Sozialberatung; sie begründen keinen Anspruch. Maßgeblich ist allein der Bescheid der zuständigen Agentur für Arbeit. Welche Fälle der Rechner abbildet und welche bewusst nicht, steht in der <a href={route('method', lang)}>Methodik</a>.</p>

    <h2>Haftung für Inhalte</h2>
    <p>Als Diensteanbieter sind wir gemäß § 7 Abs. 1 DDG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 DDG sind wir jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Die Parameter werden zu jeder Anpassung überprüft und gegen Referenzfälle getestet; eine Gewähr für Richtigkeit, Vollständigkeit und Aktualität können wir gleichwohl nicht übernehmen. Einen erkannten Fehler melden Sie bitte über die <a href={route('contact', lang)}>Kontaktseite</a>; wie wir damit umgehen, beschreibt unsere <a href={route('editorial', lang)}>Redaktionsrichtlinie</a>.</p>

    <h2>Haftung für Links</h2>
    <p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Zum Zeitpunkt der Verlinkung waren keine Rechtsverstöße erkennbar. Eine permanente inhaltliche Kontrolle ist ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen entfernen wir derartige Links umgehend.</p>

    <h2>Urheberrecht</h2>
    <p>Die durch die Betreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechts bedürfen unserer schriftlichen Zustimmung; kurze Zitate mit Quellenlink sind zulässig. Amtliche Werke, Gesetzestexte und Daten der Bundesagentur für Arbeit sind nach § 5 UrhG gemeinfrei.</p>

    <h2>Einbindung des Rechners</h2>
    <p>Der Rechner darf kostenlos als iframe in andere Websites eingebunden werden, sofern der sichtbare Quellenhinweis auf diese Website erhalten bleibt und nicht der Eindruck eines amtlichen Angebots entsteht. Den Einbindungscode senden wir auf Anfrage zu.</p>

    <h2>Verbraucherstreitbeilegung</h2>
    <p>Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle im Sinne des § 36 VSBG teilzunehmen.</p>

    <h2>Datenschutz</h2>
    <p>Wie personenbezogene Daten verarbeitet werden, steht in der <a href={route('privacy', lang)}>Datenschutzerklärung</a> und im <a href={route('cookies', lang)}>Cookie-Hinweis</a>. Stand: {LAST_UPDATED}.</p>"""

META['de-arbeitslosengeld', 'de', 'privacy'] = (
    'Datenschutzerklärung – ${SITE_NAMES[lang]}',
    'Verarbeitung nach DSGVO: Verantwortlicher, Server-Logfiles, Einwilligung für Statistik und Werbung, Speicherdauer, Ihre Rechte und Beschwerdeweg.')
BODIES['de-arbeitslosengeld', 'de', 'privacy'] = """    <h1>Datenschutzerklärung</h1>
    <p>Diese Erklärung informiert nach Art. 13 und 14 der Datenschutz-Grundverordnung (DSGVO) sowie nach dem Bundesdatenschutzgesetz (BDSG) und dem TDDDG darüber, welche personenbezogenen Daten bei der Nutzung von {SITE_URL} verarbeitet werden.</p>

    <h2>1. Verantwortlicher</h2>
    <LegalIdentity lang={lang} />
    <p>Fragen zum Datenschutz richten Sie bitte an <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. Ein Datenschutzbeauftragter ist nicht zu benennen, weil die Voraussetzungen des Art. 37 DSGVO und des § 38 BDSG hier nicht vorliegen.</p>

    <h2>2. Der Rechner überträgt nichts</h2>
    <p>Sämtliche Berechnungen laufen ausschließlich in Ihrem Browser. Bruttoentgelt, Steuerklasse, Alter, Versicherungszeiten und die Angabe zu einem Kind <strong>verlassen Ihr Gerät nicht</strong>, werden nirgends gespeichert und keiner Kennung zugeordnet. Es gibt keine Registrierung und kein Nutzerkonto. Wenn Sie den Teilen-Link verwenden, sind Ihre Eingaben in der URL kodiert – geben Sie ihn nur an Personen weiter, die sie sehen dürfen.</p>

    <h2>3. Tatsächliche Verarbeitungen</h2>
    <h3>Server-Logfiles</h3>
    <p>Beim Abruf jeder Seite protokolliert der Hoster IP-Adresse, Zeitpunkt, aufgerufene Ressource, Statuscode, übertragene Datenmenge, Browsertyp und Referrer. Zweck: technischer Betrieb, Sicherheit und Missbrauchsabwehr. Rechtsgrundlage ist unser berechtigtes Interesse an einem störungsfreien und sicheren Betrieb (Art. 6 Abs. 1 lit. f DSGVO). Die Logs werden spätestens nach 30 Tagen gelöscht.</p>
    <h3>Reichweitenmessung</h3>
    <p>Nur mit Ihrer Einwilligung setzen wir Google Analytics 4 mit IP-Anonymisierung und Google-Consent-Mode ein, um zu erkennen, welche Seiten gefunden und genutzt werden. Rechtsgrundlage: Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO und § 25 Abs. 1 TDDDG. Ohne Einwilligung wird kein Statistik-Cookie gesetzt. Speicherdauer der Auswertungsdaten: 14 Monate.</p>
    <h3>Werbung</h3>
    <p>Auf einzelnen Seiten kann Werbung über Google AdSense ausgeliefert werden. Mit Ihrer Einwilligung darf Google Cookies zur Personalisierung setzen; ohne Einwilligung werden ausschließlich nicht personalisierte Anzeigen ausgeliefert. Einzelheiten der Verarbeitung durch Google: <a href="https://policies.google.com/technologies/ads" rel="noopener" target="_blank">policies.google.com/technologies/ads</a>.</p>
    <h3>Kontaktaufnahme</h3>
    <p>Schreiben Sie uns, verarbeiten wir Ihre E-Mail-Adresse und den Inhalt Ihrer Nachricht, um zu antworten und gemeldete Rechenfehler zu beheben (Art. 6 Abs. 1 lit. f DSGVO). Die Korrespondenz wird drei Jahre nach dem letzten Kontakt gelöscht.</p>

    <h2>4. Empfänger und Auftragsverarbeitung</h2>
    <p>Daten werden weder verkauft noch vermietet. Zugriff haben allein der Hoster als Auftragsverarbeiter nach Art. 28 DSGVO, mit dem ein Auftragsverarbeitungsvertrag besteht, und – nur bei erteilter Einwilligung – die Google Ireland Limited für Statistik und Werbung.</p>

    <h2>5. Drittlandübermittlung</h2>
    <p>Bei Einsatz der Google-Dienste können Daten in die USA übermittelt werden. Grundlage sind die Standardvertragsklauseln der EU-Kommission sowie die Zertifizierung von Google LLC unter dem EU-US Data Privacy Framework. Wenn Sie die Einwilligung verweigern, findet keine solche Übermittlung statt.</p>

    <h2>6. Ihre Rechte</h2>
    <p>Sie haben das Recht auf Auskunft (Art. 15), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) und Widerspruch gegen Verarbeitungen auf Grundlage berechtigter Interessen (Art. 21 DSGVO). Eine erteilte Einwilligung können Sie jederzeit mit Wirkung für die Zukunft widerrufen – so einfach, wie Sie sie erteilt haben, über die Cookie-Einstellungen im Seitenfuß. Wenden Sie sich an <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>; wir antworten innerhalb eines Monats. Da wir kein Nutzerkonto führen, liegen uns in aller Regel keine Daten vor, die Sie identifizieren – auch das teilen wir Ihnen dann mit.</p>
    <p>Ihnen steht ein Beschwerderecht bei einer Aufsichtsbehörde zu, insbesondere bei {LEGAL.supervisoryAuthority} (<a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>).</p>

    <h2>7. Keine automatisierte Entscheidung, kein Profiling</h2>
    <p>Das Rechenergebnis entsteht auf Ihre Eingabe hin in Ihrem Browser. Es entfaltet keine rechtliche Wirkung und ist keine automatisierte Entscheidung im Sinne des Art. 22 DSGVO. Profiling findet nicht statt.</p>

    <h2>8. Erforderlichkeit und Sicherheit</h2>
    <p>Die Bereitstellung personenbezogener Daten ist weder gesetzlich noch vertraglich vorgeschrieben; Sie können den Rechner ohne jede Angabe nutzen. Die Website wird ausschließlich über HTTPS ausgeliefert und führt keine Nutzerdatenbank. Stand: {LAST_UPDATED}.</p>"""

# --------------------------------------------------------------------------- #
# Suisse — nettolohn-rechner.ch (DE + FR)
# Pas d'obligation d'Impressum au sens allemand, mais l'art. 3 al. 1 let. s LCD
# impose d'indiquer clairement son identité et ses coordonnées ; nLPD pour les données.
# --------------------------------------------------------------------------- #
META['ch-lohnrechner', 'de', 'terms'] = (
    'Impressum – ${SITE_NAME}',
    'Betreiber, Kontakt und UID dieses Lohnrechners, Haftungsausschluss zu Steuerberechnungen, Urheberrecht, Einbindung des Rechners und anwendbares Recht.')
BODIES['ch-lohnrechner', 'de', 'terms'] = """    <h1>Impressum</h1>
    <p>Angaben zum Betreiber dieser Website, veröffentlicht in Übereinstimmung mit Art. 3 Abs. 1 lit. s des Bundesgesetzes gegen den unlauteren Wettbewerb (UWG).</p>

    <h2>Betreiber und verantwortlich für den Inhalt</h2>
    <LegalIdentity lang={lang} />
    <p>Redaktionell verantwortlich: {AUTHOR_NAME}.</p>

    <h2>Hosting</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>Zweck der Website und keine Beratung</h2>
    <p>Diese Website stellt einen kostenlosen Nettolohnrechner für die Schweiz samt Ratgebern bereit. Die Ergebnisse sind <strong>unverbindliche Schätzungen</strong> auf Grundlage der Steuertarife der Eidgenössischen Steuerverwaltung, der kantonalen und kommunalen Steuerfüsse sowie der Sozialversicherungsansätze des jeweiligen Jahres. Sie ersetzen weder die Veranlagung der zuständigen Steuerverwaltung noch eine Steuer-, Rechts- oder Vorsorgeberatung. Massgebend ist einzig die Veranlagungsverfügung. Was der Rechner abbildet und was bewusst nicht, steht in der <a href={route('method', lang)}>Methodik</a>.</p>

    <h2>Haftungsausschluss</h2>
    <p>Wir prüfen Tarife und Steuerfüsse bei jeder Anpassung und testen den Rechner gegen amtliche Referenzfälle. Trotzdem können Fehler, Lücken oder Verzögerungen bei der Aktualisierung nicht ausgeschlossen werden. Eine Haftung für Schäden materieller oder immaterieller Art, die aus dem Zugriff auf diese Website, ihrer Nutzung oder Nichtnutzung entstehen, wird im gesetzlich zulässigen Umfang ausgeschlossen. Fehler melden Sie bitte über die <a href={route('contact', lang)}>Kontaktseite</a>; das Vorgehen beschreibt die <a href={route('editorial', lang)}>Redaktionsrichtlinie</a>.</p>

    <h2>Urheberrecht</h2>
    <p>Texte, Grafiken, Datenaufbereitung und Quellcode dieser Website sind urheberrechtlich geschützt. Jede Verwendung ausserhalb der Schranken des Urheberrechtsgesetzes bedarf unserer Zustimmung; kurze Zitate mit Quellenlink sind zulässig. Steuerdaten stammen von der Eidgenössischen Steuerverwaltung und den Kantonen und unterliegen deren Nutzungsbedingungen.</p>

    <h2>Einbindung des Rechners</h2>
    <p>Die Einbindung als Widget ist unter den Bedingungen der <a href={route('widget', lang)}>Widget-Seite</a> kostenlos gestattet, solange der sichtbare Quellenhinweis erhalten bleibt und nicht der Eindruck eines amtlichen Angebots entsteht.</p>

    <h2>Externe Links</h2>
    <p>Für Inhalte verlinkter Websites sind ausschliesslich deren Betreiber verantwortlich. Zum Zeitpunkt der Verlinkung waren keine Rechtsverstösse erkennbar.</p>

    <h2>Datenschutz und anwendbares Recht</h2>
    <p>Die Bearbeitung von Personendaten ist in der <a href={route('privacy', lang)}>Datenschutzerklärung</a> und im <a href={route('cookies', lang)}>Cookie-Hinweis</a> beschrieben. Es gilt schweizerisches Recht; Gerichtsstand ist {LEGAL.jurisdiction}, soweit nicht zwingende Bestimmungen etwas anderes vorsehen. Stand: {LAST_UPDATED}.</p>"""

META['ch-lohnrechner', 'de', 'privacy'] = (
    'Datenschutzerklärung – ${SITE_NAME}',
    'Bearbeitung von Personendaten nach revidiertem DSG: Logfiles, Einwilligung für Statistik und Werbung, Bekanntgabe ins Ausland, Ihre Rechte, EDÖB.')
BODIES['ch-lohnrechner', 'de', 'privacy'] = """    <h1>Datenschutzerklärung</h1>
    <p>Diese Erklärung informiert nach dem revidierten Bundesgesetz über den Datenschutz (revDSG, in Kraft seit 1. September 2023) und – soweit die Verordnung auf Besucherinnen und Besucher aus der EU anwendbar ist – nach der DSGVO über die Bearbeitung von Personendaten auf {SITE_URL}.</p>

    <h2>1. Verantwortliche Person</h2>
    <LegalIdentity lang={lang} />
    <p>Fragen zum Datenschutz: <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. Eine Vertretung in der EU nach Art. 27 DSGVO ist nicht bestellt, da sich das Angebot an Personen in der Schweiz richtet.</p>

    <h2>2. Der Rechner bearbeitet lokal</h2>
    <p>Lohn, Zivilstand, Kinder, Konfession, Wohngemeinde, Pensionskassenabzüge: alle Eingaben werden ausschliesslich in Ihrem Browser verarbeitet und <strong>weder an uns noch an Dritte übermittelt</strong>. Beim Wechsel des Kantons lädt Ihr Browser lediglich eine statische Datendatei dieser Website. Der Teilen-Link kodiert Ihre Eingaben in der URL; geben Sie ihn nur bewusst weiter.</p>

    <h2>3. Was tatsächlich bearbeitet wird</h2>
    <h3>Server-Logfiles</h3>
    <p>Der Hosting-Anbieter protokolliert IP-Adresse, Zeitpunkt, aufgerufene Seite, Statuscode, Browser und Referrer. Zweck: sicherer Betrieb und Fehlersuche; Grundlage ist unser überwiegendes privates Interesse am störungsfreien Betrieb (Art. 31 Abs. 1 revDSG, Art. 6 Abs. 1 lit. f DSGVO). Löschung nach spätestens 30 Tagen.</p>
    <h3>Reichweitenmessung und Werbung</h3>
    <p>Nur mit Ihrer Einwilligung setzen wir Google Analytics 4 mit IP-Anonymisierung und Consent-Mode ein; ohne Einwilligung wird kein Statistik-Cookie gesetzt. Wird auf einzelnen Seiten Werbung über Google AdSense ausgeliefert, erfolgt eine Personalisierung nur mit Einwilligung, andernfalls werden ausschliesslich nicht personalisierte Anzeigen angezeigt. Die Einwilligung können Sie jederzeit über die Cookie-Einstellungen im Seitenfuss widerrufen.</p>
    <h3>Kontaktaufnahme</h3>
    <p>E-Mail-Adresse und Inhalt Ihrer Nachricht bearbeiten wir, um zu antworten und gemeldete Rechenfehler zu beheben. Die Korrespondenz wird drei Jahre nach dem letzten Kontakt gelöscht.</p>

    <h2>4. Bekanntgabe an Dritte und ins Ausland</h2>
    <p>Personendaten werden weder verkauft noch vermietet. Zugriff haben der Hosting-Anbieter als Auftragsbearbeiter nach Art. 9 revDSG und, nur bei erteilter Einwilligung, Google. Dabei können Daten in die USA bekanntgegeben werden. Die Bekanntgabe stützt sich auf die Standardvertragsklauseln der EU-Kommission, anerkannt durch den EDÖB, sowie auf die Zertifizierung von Google LLC unter dem Swiss–U.S. Data Privacy Framework (Art. 16 f. revDSG).</p>

    <h2>5. Ihre Rechte</h2>
    <p>Sie haben insbesondere das Recht auf Auskunft (Art. 25 revDSG), auf Berichtigung (Art. 32), auf Löschung oder Vernichtung, auf Widerspruch gegen eine Bearbeitung sowie auf Herausgabe oder Übertragung Ihrer Daten (Art. 28 revDSG). Für Personen im Anwendungsbereich der DSGVO gelten zusätzlich deren Art. 15 bis 22. Melden Sie sich unter <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>; wir antworten in der Regel innert 30 Tagen. Da wir kein Nutzerkonto führen, liegen uns meist keine Daten vor, die Sie identifizieren.</p>
    <p>Sie können sich jederzeit an die Aufsichtsbehörde wenden: {LEGAL.supervisoryAuthority} (<a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>).</p>

    <h2>6. Keine automatisierte Einzelentscheidung</h2>
    <p>Das Rechenergebnis entsteht auf Ihre Eingabe hin in Ihrem Browser und hat keine Rechtswirkung; eine automatisierte Einzelentscheidung im Sinne von Art. 21 revDSG liegt nicht vor. Profiling findet nicht statt.</p>

    <h2>7. Sicherheit und Änderungen</h2>
    <p>Die Website wird ausschliesslich über HTTPS ausgeliefert und führt keine Nutzerdatenbank. Wir passen diese Erklärung an, wenn sich Recht oder Technik ändern. Stand: {LAST_UPDATED}.</p>"""

META['ch-lohnrechner', 'fr', 'terms'] = (
    'Mentions légales – ${SITE_NAME_FR}',
    'Exploitant, contact et IDE de ce calculateur de salaire net, exclusion de responsabilité, droit d’auteur, intégration du widget et droit applicable.')
BODIES['ch-lohnrechner', 'fr', 'terms'] = """    <h1>Mentions légales</h1>
    <p>Informations relatives à l’exploitant de ce site, publiées conformément à l’art. 3 al. 1 let. s de la loi fédérale contre la concurrence déloyale (LCD).</p>

    <h2>Exploitant et responsable du contenu</h2>
    <LegalIdentity lang={lang} />
    <p>Responsable éditorial : {AUTHOR_NAME}.</p>

    <h2>Hébergeur</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>Objet du site et absence de conseil</h2>
    <p>Ce site propose gratuitement un calculateur de salaire net suisse et des guides explicatifs. Les résultats sont des <strong>estimations indicatives</strong> fondées sur les barèmes de l’Administration fédérale des contributions, les coefficients cantonaux et communaux et les taux de cotisations sociales de l’année considérée. Ils ne remplacent ni la taxation de l’administration fiscale compétente, ni un conseil fiscal, juridique ou de prévoyance. Seule la décision de taxation fait foi. Ce que le calculateur couvre et ce qu’il ne couvre volontairement pas figure dans la <a href={route('method', lang)}>méthodologie</a>.</p>

    <h2>Exclusion de responsabilité</h2>
    <p>Nous contrôlons les barèmes et les coefficients à chaque mise à jour et testons le calculateur sur des cas de référence officiels. Des erreurs, lacunes ou retards de mise à jour ne peuvent cependant pas être exclus. Toute responsabilité pour des dommages matériels ou immatériels résultant de l’accès à ce site, de son utilisation ou de sa non-utilisation est exclue dans les limites permises par la loi. Signalez-nous toute erreur via la page <a href={route('contact', lang)}>contact</a> ; la procédure est décrite dans notre <a href={route('editorial', lang)}>charte éditoriale</a>.</p>

    <h2>Droit d’auteur</h2>
    <p>Les textes, graphiques, mises en forme de données et le code source de ce site sont protégés par le droit d’auteur. Toute utilisation dépassant les limites légales requiert notre accord ; les courtes citations accompagnées d’un lien vers la source sont autorisées. Les données fiscales proviennent de l’Administration fédérale des contributions et des cantons et restent soumises à leurs conditions d’utilisation.</p>

    <h2>Intégration du calculateur</h2>
    <p>L’intégration sous forme de widget est autorisée gratuitement aux conditions indiquées sur la <a href={route('widget', lang)}>page widget</a>, pour autant que la mention visible de la source subsiste et qu’aucune confusion avec une offre officielle ne soit créée.</p>

    <h2>Liens externes</h2>
    <p>Les exploitants des sites liés sont seuls responsables de leur contenu. Aucune infraction n’était décelable au moment de la création du lien.</p>

    <h2>Protection des données et droit applicable</h2>
    <p>Le traitement des données personnelles est décrit dans la <a href={route('privacy', lang)}>déclaration de protection des données</a> et la page <a href={route('cookies', lang)}>cookies</a>. Le droit suisse est applicable ; le for est à {LEGAL.jurisdiction}, sous réserve des dispositions impératives. Dernière mise à jour : {LAST_UPDATED}.</p>"""

META['ch-lohnrechner', 'fr', 'privacy'] = (
    'Protection des données – ${SITE_NAME_FR}',
    'Traitement des données selon la nLPD : journaux, consentement pour la mesure d’audience et la publicité, communication à l’étranger, vos droits, PFPDT.')
BODIES['ch-lohnrechner', 'fr', 'privacy'] = """    <h1>Déclaration de protection des données</h1>
    <p>Cette déclaration informe, conformément à la loi fédérale révisée sur la protection des données (nLPD, en vigueur depuis le 1<sup>er</sup> septembre 2023) et, dans la mesure où il s’applique aux visiteurs de l’Union européenne, au RGPD, sur le traitement des données personnelles sur {SITE_URL}.</p>

    <h2>1. Responsable du traitement</h2>
    <LegalIdentity lang={lang} />
    <p>Questions relatives à la protection des données : <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. Aucun représentant dans l’Union européenne au sens de l’art. 27 RGPD n’a été désigné, l’offre s’adressant aux personnes résidant en Suisse.</p>

    <h2>2. Le calculateur traite localement</h2>
    <p>Salaire, état civil, enfants, confession, commune de domicile, déductions de caisse de pension : toutes les saisies sont traitées exclusivement dans votre navigateur et <strong>ne nous sont jamais transmises, ni à des tiers</strong>. Lors d’un changement de canton, votre navigateur charge uniquement un fichier de données statique de ce site. Le lien de partage encode vos saisies dans l’URL : ne le transmettez qu’en connaissance de cause.</p>

    <h2>3. Ce qui est réellement traité</h2>
    <h3>Journaux du serveur</h3>
    <p>L’hébergeur enregistre l’adresse IP, l’horodatage, la page appelée, le code de réponse, le navigateur et le référent. Finalité : exploitation sécurisée et diagnostic ; le traitement repose sur notre intérêt privé prépondérant à un service disponible (art. 31 al. 1 nLPD, art. 6 par. 1 let. f RGPD). Suppression après 30 jours au plus.</p>
    <h3>Mesure d’audience et publicité</h3>
    <p>Uniquement avec votre consentement, nous utilisons Google Analytics 4 avec anonymisation de l’adresse IP et mode de consentement ; sans consentement, aucun cookie statistique n’est déposé. Si de la publicité Google AdSense est diffusée sur certaines pages, la personnalisation n’intervient qu’avec votre consentement ; à défaut, seules des annonces non personnalisées sont affichées. Vous pouvez révoquer votre consentement à tout moment depuis les réglages cookies du pied de page.</p>
    <h3>Prise de contact</h3>
    <p>Votre adresse électronique et le contenu de votre message sont traités pour vous répondre et corriger les erreurs de calcul signalées. La correspondance est supprimée trois ans après le dernier échange.</p>

    <h2>4. Communication à des tiers et à l’étranger</h2>
    <p>Aucune donnée n’est vendue ni louée. Y ont accès l’hébergeur, en qualité de sous-traitant au sens de l’art. 9 nLPD, et, en cas de consentement, Google. Des données peuvent alors être communiquées aux États-Unis, sur la base des clauses contractuelles types de la Commission européenne reconnues par le PFPDT et de la certification de Google LLC au titre du Swiss–U.S. Data Privacy Framework (art. 16 s. nLPD).</p>

    <h2>5. Vos droits</h2>
    <p>Vous disposez notamment du droit d’accès (art. 25 nLPD), de rectification (art. 32), d’effacement ou de destruction, d’opposition au traitement, ainsi que du droit à la remise ou à la transmission de vos données (art. 28 nLPD). Les personnes relevant du RGPD bénéficient en outre de ses art. 15 à 22. Écrivez à <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> ; nous répondons en règle générale dans les 30 jours. En l’absence de compte utilisateur, nous ne détenons le plus souvent aucune donnée permettant de vous identifier.</p>
    <p>Vous pouvez en tout temps vous adresser à l’autorité de surveillance : {LEGAL.supervisoryAuthority} (<a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>).</p>

    <h2>6. Absence de décision individuelle automatisée</h2>
    <p>Le résultat du calcul est produit dans votre navigateur, à votre demande, et n’a aucun effet juridique : il ne constitue pas une décision individuelle automatisée au sens de l’art. 21 nLPD. Aucun profilage n’est effectué.</p>

    <h2>7. Sécurité et modifications</h2>
    <p>Le site est servi exclusivement en HTTPS et ne tient aucune base de données d’utilisateurs. Nous adaptons cette déclaration en cas d’évolution juridique ou technique. Dernière mise à jour : {LAST_UPDATED}.</p>"""

# --------------------------------------------------------------------------- #
# Espagne — calculadora-paro.es
# Art. 10 LSSI-CE pour l'aviso legal, RGPD + LOPDGDD pour la politique de confidentialité.
# --------------------------------------------------------------------------- #
META['es-calculadora-paro', 'es', 'terms'] = (
    'Aviso legal – ${SITE_NAMES[lang]}',
    'Titular del sitio, objeto, condiciones de uso, exclusión de responsabilidad, propiedad intelectual, enlaces, legislación aplicable y fuero competente.')
BODIES['es-calculadora-paro', 'es', 'terms'] = """    <h1>Aviso legal</h1>
    <p>Información exigida por el artículo 10 de la Ley 34/2002, de 11 de julio, de servicios de la sociedad de la información y de comercio electrónico (LSSI-CE).</p>

    <h2>Titular del sitio</h2>
    <LegalIdentity lang={lang} />
    <p>Responsable de los contenidos: {AUTHOR_NAME}.</p>

    <h2>Alojamiento</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>Objeto y ausencia de asesoramiento</h2>
    <p>Este sitio ofrece de forma gratuita una calculadora de la prestación por desempleo y guías explicativas. Los resultados son <strong>estimaciones orientativas</strong> basadas en la normativa publicada por el SEPE, en las bases de cotización de la Seguridad Social y en los tipos de retención de la Agencia Tributaria. No constituyen asesoramiento jurídico, fiscal ni laboral, ni generan derecho alguno: solo la resolución del SEPE determina la cuantía y la duración de su prestación. Lo que la herramienta cubre y lo que deliberadamente no cubre se detalla en la <a href={route('method', lang)}>metodología</a>.</p>

    <h2>Condiciones de uso</h2>
    <p>El acceso es libre y gratuito y no requiere registro. El usuario se compromete a utilizar el sitio conforme a la ley y a no realizar actuaciones que puedan dañarlo, sobrecargarlo o impedir su normal funcionamiento, incluida la extracción masiva y automatizada de contenidos. La calculadora puede integrarse gratuitamente mediante iframe en otra web siempre que se mantenga visible el enlace a la página de origen y no se induzca a pensar que se trata de un servicio oficial.</p>

    <h2>Exclusión de responsabilidad</h2>
    <p>Revisamos los parámetros en cada actualización normativa y comprobamos la calculadora frente a casos de referencia, pero no garantizamos la ausencia de errores ni la exhaustividad. La normativa cambia y determinadas situaciones (trabajo en el extranjero, fijos discontinuos, compatibilidades específicas) siguen reglas que la herramienta no aplica. El titular no responde de las decisiones adoptadas exclusivamente sobre la base de una estimación ni de las interrupciones del servicio. Si detecta un error, comuníquenoslo desde la página de <a href={route('contact', lang)}>contacto</a>: el procedimiento de corrección figura en nuestra <a href={route('editorial', lang)}>política editorial</a>.</p>

    <h2>Propiedad intelectual e industrial</h2>
    <p>Los textos, el diseño, la estructura de navegación, las bases de datos elaboradas y el código fuente son titularidad del editor y están protegidos por el Real Decreto Legislativo 1/1996. Queda prohibida su reproducción, distribución o transformación sin autorización, salvo cita breve con enlace a la fuente. Las disposiciones normativas y los datos públicos citados pertenecen a sus organismos emisores.</p>

    <h2>Enlaces</h2>
    <p>Los enlaces a sitios de terceros se ofrecen para facilitar la verificación de las fuentes. No controlamos sus contenidos y no asumimos responsabilidad alguna sobre ellos.</p>

    <h2>Protección de datos y cookies</h2>
    <p>Los datos que introduce en la calculadora no salen de su navegador. El tratamiento de datos personales se describe en la <a href={route('privacy', lang)}>política de privacidad</a> y en la página de <a href={route('cookies', lang)}>cookies</a>.</p>

    <h2>Legislación aplicable</h2>
    <p>Este aviso legal se rige por la legislación española. Para cualquier controversia, las partes se someten a los juzgados y tribunales de {LEGAL.jurisdiction}, salvo que la normativa de consumo imponga otro fuero. Última actualización: {LAST_UPDATED}.</p>"""

META['es-calculadora-paro', 'es', 'privacy'] = (
    'Política de privacidad – ${SITE_NAMES[lang]}',
    'Qué datos trata este sitio, con qué base jurídica y plazo, quién accede a ellos y cómo ejercer sus derechos o reclamar ante la AEPD.')
BODIES['es-calculadora-paro', 'es', 'privacy'] = """    <h1>Política de privacidad</h1>
    <p>Esta política informa, conforme a los artículos 13 y 14 del Reglamento (UE) 2016/679 (RGPD) y a la Ley Orgánica 3/2018 (LOPDGDD), sobre los tratamientos de datos personales asociados al uso de {SITE_URL}.</p>

    <h2>1. Responsable del tratamiento</h2>
    <LegalIdentity lang={lang} />
    <p>Contacto en materia de protección de datos: <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. No se ha designado delegado de protección de datos por no concurrir los supuestos del artículo 37 del RGPD ni del artículo 34 de la LOPDGDD.</p>

    <h2>2. Lo que la calculadora no hace</h2>
    <p>El cálculo se ejecuta íntegramente en su navegador. Las bases de cotización, los días cotizados, la edad, los hijos a cargo y la retención voluntaria <strong>no se transmiten a ningún servidor</strong>, no se almacenan y no se asocian a ningún identificador. No hay registro ni cuenta de usuario. Si utiliza el enlace para compartir, sus datos quedan codificados en la URL: compártalo solo con quien desee.</p>

    <h2>3. Tratamientos que sí se realizan</h2>
    <h3>Registros del servidor</h3>
    <p>El proveedor de alojamiento registra la dirección IP, la fecha y hora, la página solicitada, el código de respuesta, el navegador y el referente. Finalidad: seguridad, prevención de abusos y diagnóstico de incidencias. Base jurídica: interés legítimo del responsable en mantener un servicio disponible y seguro (art. 6.1.f del RGPD). Plazo de conservación: 30 días como máximo.</p>
    <h3>Medición de audiencia</h3>
    <p>Si presta su consentimiento, medimos la audiencia con Google Analytics 4, con anonimización de IP y modo de consentimiento, para saber qué páginas se encuentran y se utilizan. Base jurídica: su consentimiento (art. 6.1.a del RGPD y art. 22.2 de la LSSI). Sin consentimiento no se instala ninguna cookie de medición. Conservación de los datos de audiencia: 14 meses.</p>
    <h3>Publicidad</h3>
    <p>Algunas páginas pueden mostrar publicidad de Google AdSense. Con su consentimiento, Google puede instalar cookies de personalización; sin él, solo se muestran anuncios no personalizados. El tratamiento que Google realiza por cuenta propia se describe en sus <a href="https://policies.google.com/technologies/ads" rel="noopener" target="_blank">políticas de publicidad</a>.</p>
    <h3>Mensajes que nos envía</h3>
    <p>Si nos escribe, tratamos su dirección de correo y el contenido del mensaje para responderle y, en su caso, corregir un error de cálculo (interés legítimo). Conservación: tres años desde el último contacto.</p>

    <h2>4. Destinatarios y encargados</h2>
    <p>No vendemos ni cedemos datos. Solo acceden a ellos el proveedor de alojamiento, como encargado del tratamiento con contrato conforme al artículo 28 del RGPD, y, únicamente si consiente, Google Ireland Limited para la medición de audiencia y la publicidad.</p>

    <h2>5. Transferencias internacionales</h2>
    <p>Los servicios de Google pueden implicar una transferencia a Estados Unidos, amparada en las cláusulas contractuales tipo de la Comisión Europea y en la certificación de Google LLC en el marco EU–U.S. Data Privacy Framework. Si rechaza la medición y la publicidad, no se produce transferencia alguna.</p>

    <h2>6. Sus derechos</h2>
    <p>Puede ejercer los derechos de acceso, rectificación, supresión, limitación, oposición y portabilidad (arts. 15 a 22 del RGPD), así como retirar en cualquier momento el consentimiento prestado, con la misma facilidad con que lo otorgó, desde la configuración de cookies del pie de página. Escriba a <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>; responderemos en el plazo de un mes. Al no existir cuenta de usuario, lo habitual es que no dispongamos de dato alguno que permita identificarle, y así se lo indicaremos.</p>
    <p>Si considera que sus derechos no han sido atendidos, puede presentar una reclamación ante la {LEGAL.supervisoryAuthority}: <a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>.</p>

    <h2>7. Sin decisiones automatizadas ni elaboración de perfiles</h2>
    <p>El resultado que muestra la calculadora es un cálculo realizado a petición suya, sobre sus propios datos y en su navegador. No produce efectos jurídicos ni constituye una decisión automatizada del artículo 22 del RGPD. No elaboramos perfiles.</p>

    <h2>8. Menores y seguridad</h2>
    <p>El sitio no se dirige a menores de catorce años ni recaba conscientemente sus datos. Se sirve exclusivamente por HTTPS y no mantiene ninguna base de datos de usuarios. Esta política puede actualizarse por motivos legales o técnicos. Última actualización: {LAST_UPDATED}.</p>"""

# --------------------------------------------------------------------------- #
# Pays-Bas — ww-berekenen.nl
# Disclaimer et colofon (identité du fournisseur, art. 3:15d BW), AVG pour la privacy.
# --------------------------------------------------------------------------- #
META['nl-ww-berekenen', 'nl', 'terms'] = (
    'Disclaimer en colofon – ${SITE_NAMES[lang]}',
    'Wie deze site uitgeeft, waarvoor de rekenhulp wel en niet dient, aansprakelijkheid, auteursrecht, insluiten van de tool en toepasselijk recht.')
BODIES['nl-ww-berekenen', 'nl', 'terms'] = """    <h1>Disclaimer en colofon</h1>
    <p>Gegevens van de dienstverlener zoals bedoeld in artikel 3:15d van het Burgerlijk Wetboek, en de voorwaarden waaronder u deze site gebruikt.</p>

    <h2>Uitgever</h2>
    <LegalIdentity lang={lang} />
    <p>Verantwoordelijk voor de inhoud: {AUTHOR_NAME}.</p>

    <h2>Hosting</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>Waarvoor deze site dient – en waarvoor niet</h2>
    <p>Deze site biedt kosteloos een rekenhulp voor de WW-uitkering en de transitievergoeding, met bijbehorende uitleg. De uitkomsten zijn <strong>indicatieve schattingen</strong> op basis van de Werkloosheidswet, de dagloonregels van het UWV en de loonheffingstabellen van de Belastingdienst. Ze zijn geen juridisch, fiscaal of financieel advies en geven geen recht op een uitkering: alleen de beslissing van het UWV is bepalend. Wat de rekenhulp wel en bewust niet meeneemt, staat in de <a href={route('method', lang)}>methode en bronnen</a>.</p>

    <h2>Aansprakelijkheid</h2>
    <p>We controleren de parameters bij elke wijziging en toetsen de rekenhulp aan referentiegevallen, maar we garanderen niet dat alles foutloos en volledig is. Regelgeving verandert, en sommige situaties (werken in het buitenland, oproepcontracten, samenloop met andere uitkeringen) volgen regels die de rekenhulp niet toepast. We zijn niet aansprakelijk voor beslissingen die uitsluitend op een schatting zijn gebaseerd, noch voor tijdelijke onbereikbaarheid. Ziet u een fout, meld die dan via de <a href={route('contact', lang)}>contactpagina</a>; hoe we die afhandelen staat in ons <a href={route('editorial', lang)}>redactiestatuut</a>.</p>

    <h2>Auteursrecht</h2>
    <p>Teksten, vormgeving, databewerkingen en broncode van deze site zijn auteursrechtelijk beschermd. Overname of hergebruik zonder toestemming is niet toegestaan; een kort citaat met bronvermelding en link mag. Wetteksten en overheidsgegevens zijn ingevolge artikel 11 van de Auteurswet vrij van auteursrecht.</p>

    <h2>Rekenhulp insluiten</h2>
    <p>U mag de rekenhulp kosteloos in een iframe op uw eigen site plaatsen, mits de zichtbare bronvermelding naar deze site blijft staan en niet de indruk ontstaat dat het om een dienst van de overheid gaat. Vraag ons om de insluitcode.</p>

    <h2>Links naar andere sites</h2>
    <p>Voor de inhoud van websites van derden zijn uitsluitend hun beheerders verantwoordelijk. Op het moment van linken waren er geen aanwijzingen voor onrechtmatige inhoud.</p>

    <h2>Persoonsgegevens en cookies</h2>
    <p>Wat u in de rekenhulp invult, verlaat uw browser niet. Hoe we met persoonsgegevens omgaan, leest u in de <a href={route('privacy', lang)}>privacyverklaring</a> en op de pagina <a href={route('cookies', lang)}>cookies</a>.</p>

    <h2>Toepasselijk recht</h2>
    <p>Op het gebruik van deze site is Nederlands recht van toepassing. Geschillen worden voorgelegd aan de bevoegde rechter in {LEGAL.jurisdiction}, tenzij dwingend recht anders bepaalt. Laatst bijgewerkt: {LAST_UPDATED}.</p>"""

META['nl-ww-berekenen', 'nl', 'privacy'] = (
    'Privacyverklaring – ${SITE_NAMES[lang]}',
    'Welke gegevens deze site verwerkt, op welke grondslag en hoe lang, wie ze inziet, en hoe u uw AVG-rechten uitoefent of klaagt bij de AP.')
BODIES['nl-ww-berekenen', 'nl', 'privacy'] = """    <h1>Privacyverklaring</h1>
    <p>Deze verklaring beschrijft, op grond van de artikelen 13 en 14 van de Algemene verordening gegevensbescherming (AVG), welke persoonsgegevens bij het gebruik van {SITE_URL} worden verwerkt.</p>

    <h2>1. Verwerkingsverantwoordelijke</h2>
    <LegalIdentity lang={lang} />
    <p>Vragen over privacy: <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. Een functionaris voor gegevensbescherming is niet aangesteld; de gevallen van artikel 37 AVG doen zich hier niet voor.</p>

    <h2>2. Wat de rekenhulp niet doet</h2>
    <p>De berekening gebeurt volledig in uw browser. SV-loon, gewerkte uren, einddatum van het dienstverband, arbeidsverleden en loonheffingskorting <strong>worden niet naar een server gestuurd</strong>, nergens opgeslagen en aan geen enkele identificatie gekoppeld. Er is geen account en geen registratie. Gebruikt u de deellink, dan staan uw invoergegevens in de URL: deel die alleen met wie u wilt.</p>

    <h2>3. Wat wel wordt verwerkt</h2>
    <h3>Serverlogbestanden</h3>
    <p>De hostingpartij legt per verzoek het IP-adres, het tijdstip, de opgevraagde pagina, de responscode, de browser en de verwijzende pagina vast. Doel: veilige werking, misbruikpreventie en storingsanalyse. Grondslag: ons gerechtvaardigd belang bij een beschikbare en veilige dienst (artikel 6, lid 1, onder f, AVG). Bewaartermijn: maximaal 30 dagen.</p>
    <h3>Bezoekstatistieken</h3>
    <p>Alleen met uw toestemming meten we het bezoek met Google Analytics 4, met IP-anonimisering en consent mode, om te zien welke pagina’s worden gevonden en gebruikt. Grondslag: uw toestemming (artikel 6, lid 1, onder a, AVG en artikel 11.7a Telecommunicatiewet). Zonder toestemming wordt geen statistiekcookie geplaatst. Bewaartermijn van de statistiekgegevens: 14 maanden.</p>
    <h3>Advertenties</h3>
    <p>Op sommige pagina’s kan advertentieruimte van Google AdSense worden getoond. Met uw toestemming mag Google cookies voor personalisatie plaatsen; zonder toestemming worden uitsluitend niet-gepersonaliseerde advertenties getoond. Zie de <a href="https://policies.google.com/technologies/ads" rel="noopener" target="_blank">advertentievoorwaarden van Google</a>.</p>
    <h3>Berichten die u ons stuurt</h3>
    <p>Schrijft u ons, dan verwerken we uw e-mailadres en de inhoud van uw bericht om te antwoorden en gemelde rekenfouten te herstellen (gerechtvaardigd belang). Bewaartermijn: drie jaar na het laatste contact.</p>

    <h2>4. Ontvangers en verwerkers</h2>
    <p>We verkopen of verhuren geen gegevens. Toegang hebben alleen de hostingpartij, als verwerker met een verwerkersovereenkomst op grond van artikel 28 AVG, en – uitsluitend bij toestemming – Google Ireland Limited voor statistieken en advertenties.</p>

    <h2>5. Doorgifte buiten de EER</h2>
    <p>Bij gebruik van de Google-diensten kunnen gegevens naar de Verenigde Staten worden doorgegeven, op basis van de modelcontractbepalingen van de Europese Commissie en de certificering van Google LLC onder het EU–U.S. Data Privacy Framework. Weigert u de statistieken en advertenties, dan vindt geen doorgifte plaats.</p>

    <h2>6. Uw rechten</h2>
    <p>U heeft recht op inzage, rectificatie, verwijdering, beperking, bezwaar en overdraagbaarheid (artikelen 15 tot en met 22 AVG). Gegeven toestemming kunt u op elk moment intrekken, net zo eenvoudig als u die heeft gegeven, via de cookie-instellingen onderaan de pagina. Stuur een bericht naar <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>; we reageren binnen een maand. Omdat er geen account bestaat, hebben we meestal geen gegevens waarmee we u kunnen identificeren – dat laten we u dan weten.</p>
    <p>U kunt ook een klacht indienen bij {LEGAL.supervisoryAuthority}: <a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>.</p>

    <h2>7. Geen geautomatiseerde besluitvorming</h2>
    <p>De uitkomst van de rekenhulp ontstaat op uw verzoek, met uw eigen invoer, in uw browser. Ze heeft geen rechtsgevolg en is geen geautomatiseerd besluit in de zin van artikel 22 AVG. We stellen geen profielen op.</p>

    <h2>8. Beveiliging en wijzigingen</h2>
    <p>De site wordt uitsluitend via HTTPS aangeboden en houdt geen gebruikersdatabase bij. We passen deze verklaring aan als wet- of regelgeving of de techniek daartoe aanleiding geeft. Laatst bijgewerkt: {LAST_UPDATED}.</p>"""

# --------------------------------------------------------------------------- #
# Canada — ei-calculator.ca (EN + FR)
# LPRPDE/PIPEDA, plus mention de la Loi 25 pour le Québec.
# --------------------------------------------------------------------------- #
META['ca-ei-calculator', 'en', 'terms'] = (
    'Terms of use – ${SITE_NAMES[lang]}',
    'Who publishes this EI calculator, what the estimates are and are not, limits of liability, copyright, embedding the tool and the governing law.')
BODIES['ca-ei-calculator', 'en', 'terms'] = """    <h1>Terms of use</h1>
    <p>By using this website you accept the terms below. They apply to every page and to the calculator itself.</p>

    <h2>Publisher</h2>
    <LegalIdentity lang={lang} />
    <p>Responsible for content: {AUTHOR_NAME}.</p>

    <h2>Hosting</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>What this site is — and what it is not</h2>
    <p>This site offers a free Employment Insurance calculator and explanatory guides. Results are <strong>estimates</strong> based on the Employment Insurance Act, the weekly benefit rates and maximum insurable earnings published by Service Canada, and the regional unemployment rates published by Statistics Canada. They are not legal, tax or financial advice, they create no entitlement, and they do not bind Service Canada, which alone decides your claim. This site is independent and is not affiliated with, endorsed by, or operated on behalf of the Government of Canada. What the tool covers and deliberately does not cover is set out in our <a href={route('method', lang)}>methodology</a>.</p>

    <h2>Accuracy and liability</h2>
    <p>We update the parameters at every change and test the calculator against reference cases, but we do not warrant that it is error-free or complete. Rules change, and some situations — work outside Canada, fishing benefits, self-employed special benefits, overlapping claims — follow rules the calculator does not apply. To the fullest extent permitted by law, we are not liable for any loss arising from a decision made solely on an estimate, or from any interruption of the service. The site is provided "as is", without warranty of any kind. If you spot an error, tell us through the <a href={route('contact', lang)}>contact page</a>; our correction process is described in the <a href={route('editorial', lang)}>editorial policy</a>.</p>

    <h2>Copyright</h2>
    <p>The text, design, compiled data and source code of this site are protected by the Copyright Act and remain the property of the publisher. Reproduction or reuse without permission is prohibited, except for short quotations with a link to the source page. Statutes and Government of Canada data are reproduced under the terms set by their originating departments.</p>

    <h2>Embedding the calculator</h2>
    <p>You may embed the calculator free of charge in an iframe on your own site, provided the visible credit link back to this site remains and nothing suggests the tool is an official government service. Ask us for the embed code.</p>

    <h2>Links to other sites</h2>
    <p>Links to third-party sites are provided so you can verify our sources. We do not control their content and accept no responsibility for it.</p>

    <h2>Personal information and cookies</h2>
    <p>What you type into the calculator never leaves your browser. How we handle personal information is set out in our <a href={route('privacy', lang)}>privacy policy</a> and on the <a href={route('cookies', lang)}>cookies</a> page.</p>

    <h2>Governing law</h2>
    <p>These terms are governed by the laws of {LEGAL.jurisdiction} and the federal laws of Canada applicable there. We may amend them; the date below shows the current version. Last updated: {LAST_UPDATED}.</p>"""

META['ca-ei-calculator', 'en', 'privacy'] = (
    'Privacy policy – ${SITE_NAMES[lang]}',
    'What this site collects under PIPEDA, why, how long it is kept, where it is stored, how to opt out of analytics and how to reach the Privacy Commissioner.')
BODIES['ca-ei-calculator', 'en', 'privacy'] = """    <h1>Privacy policy</h1>
    <p>This policy explains what personal information is handled when you use {SITE_URL}, under the Personal Information Protection and Electronic Documents Act (PIPEDA). If you are a Quebec resident, the rights described below also reflect Quebec’s Act respecting the protection of personal information in the private sector, as amended by Law 25.</p>

    <h2>1. Who is accountable</h2>
    <LegalIdentity lang={lang} />
    <p>Privacy enquiries: <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. {AUTHOR_NAME} is the individual accountable for personal information under our control, as required by PIPEDA’s first principle.</p>

    <h2>2. The calculator sends nothing</h2>
    <p>Every calculation runs in your browser. Insurable earnings, insurable hours, your economic region or postal code, the number of best weeks and the Family Supplement question <strong>are never transmitted to a server</strong>, never stored, and never linked to an identifier. There is no account and no sign-up. If you use the share link, your entries are encoded in the URL — send it only to people you choose.</p>

    <h2>3. What is actually collected</h2>
    <h3>Server logs</h3>
    <p>Our hosting provider records, for each request, the IP address, timestamp, page requested, response code, browser and referring page. Purpose: keeping the service available and secure, and diagnosing faults. This is information a reasonable person would consider appropriate in the circumstances, and it is kept for no more than 30 days.</p>
    <h3>Analytics</h3>
    <p>We use Google Analytics 4 with IP anonymisation and Google consent mode to see which pages are found and used. Consent is implied when you continue to use the site after the notice shown on your first visit, and you may withdraw it at any time through the cookie settings in the footer — analytics then stops on your device. Analytics data is retained for 14 months.</p>
    <h3>Advertising</h3>
    <p>Some pages may carry Google AdSense advertising. Where you have not opted out, Google may set cookies to personalise ads; once you opt out, only non-personalised ads are served. Google’s own processing is described in its <a href="https://policies.google.com/technologies/ads" rel="noopener" target="_blank">advertising policies</a>.</p>
    <h3>Messages you send us</h3>
    <p>If you write to us, we process your email address and the content of your message to reply and, where relevant, to fix a calculation error. We keep that correspondence for three years after the last exchange.</p>

    <h2>4. Who sees it</h2>
    <p>We never sell, rent or trade personal information. Access is limited to our hosting provider, acting on our instructions under contract, and to Google where analytics or advertising is active.</p>

    <h2>5. Storage outside Canada</h2>
    <p>Our hosting provider and Google may store or process this information outside Canada, including in the United States. While it is there, it is subject to the laws of that country and may be accessible to its courts and law enforcement under a lawful order. We use providers that contractually commit to a comparable level of protection, as PIPEDA requires of transfers for processing.</p>

    <h2>6. Your rights</h2>
    <p>You may ask what personal information we hold about you, ask for it to be corrected, and challenge our compliance with this policy. Write to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>; we respond within 30 days, at no cost for a routine request. Because there is no user account, we usually hold nothing that identifies you, and we will say so plainly.</p>
    <p>If our answer does not satisfy you, you may complain to the {LEGAL.supervisoryAuthority}: <a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>.</p>

    <h2>7. No automated decisions, no profiling</h2>
    <p>The figure the calculator shows is a computation you asked for, made in your browser from your own entries. It has no legal effect and is not an automated decision about you. We build no profiles.</p>

    <h2>8. Safeguards and changes</h2>
    <p>The site is served over HTTPS only and keeps no user database. We may update this policy; the date below identifies the current version. Last updated: {LAST_UPDATED}.</p>"""

META['ca-ei-calculator', 'fr', 'terms'] = (
    'Conditions d’utilisation – ${SITE_NAMES[lang]}',
    'Qui publie ce calculateur d’assurance-emploi, ce que valent les estimations, limites de responsabilité, droit d’auteur, intégration et droit applicable.')
BODIES['ca-ei-calculator', 'fr', 'terms'] = """    <h1>Conditions d’utilisation</h1>
    <p>L’utilisation de ce site vaut acceptation des conditions ci-dessous. Elles s’appliquent à toutes les pages et au calculateur.</p>

    <h2>Éditeur</h2>
    <LegalIdentity lang={lang} />
    <p>Responsable du contenu : {AUTHOR_NAME}.</p>

    <h2>Hébergement</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>Ce que ce site est, et ce qu’il n’est pas</h2>
    <p>Ce site offre gratuitement un calculateur d’assurance-emploi et des guides explicatifs. Les résultats sont des <strong>estimations</strong> fondées sur la Loi sur l’assurance-emploi, les taux de prestations et le maximum de la rémunération assurable publiés par Service Canada, ainsi que sur les taux de chômage régionaux de Statistique Canada. Ils ne constituent pas un avis juridique, fiscal ou financier, ne créent aucun droit et ne lient pas Service Canada, seul compétent pour statuer sur votre demande. Ce site est indépendant : il n’est ni affilié au gouvernement du Canada, ni approuvé par lui, ni exploité pour son compte. Ce que l’outil couvre et ce qu’il ne couvre volontairement pas figure dans notre <a href={route('method', lang)}>méthodologie</a>.</p>

    <h2>Exactitude et responsabilité</h2>
    <p>Nous mettons les paramètres à jour à chaque changement et testons le calculateur sur des cas de référence, sans pour autant garantir l’absence d’erreur ni l’exhaustivité. Les règles évoluent et certaines situations — travail hors du Canada, prestations de pêcheur, prestations spéciales des travailleurs autonomes, demandes qui se chevauchent — obéissent à des règles que le calculateur n’applique pas. Dans la mesure permise par la loi, nous déclinons toute responsabilité pour les préjudices résultant d’une décision prise sur la seule base d’une estimation ou d’une interruption du service. Le site est fourni « tel quel », sans garantie d’aucune sorte. Signalez-nous toute erreur par la page <a href={route('contact', lang)}>contact</a> ; notre procédure de correction est décrite dans la <a href={route('editorial', lang)}>charte éditoriale</a>.</p>

    <h2>Droit d’auteur</h2>
    <p>Les textes, la conception, les données compilées et le code source de ce site sont protégés par la Loi sur le droit d’auteur et demeurent la propriété de l’éditeur. Toute reproduction ou réutilisation sans autorisation est interdite, sauf courte citation accompagnée d’un lien vers la page d’origine. Les lois et les données du gouvernement du Canada sont reproduites aux conditions fixées par les ministères qui les publient.</p>

    <h2>Intégration du calculateur</h2>
    <p>Vous pouvez intégrer gratuitement le calculateur dans une iframe sur votre site, à condition de conserver le lien de crédit visible vers ce site et de ne rien laisser croire qui suggère un service gouvernemental officiel. Demandez-nous le code d’intégration.</p>

    <h2>Liens externes</h2>
    <p>Les liens vers des sites tiers vous permettent de vérifier nos sources. Nous n’exerçons aucun contrôle sur leur contenu et n’en assumons aucune responsabilité.</p>

    <h2>Renseignements personnels et témoins</h2>
    <p>Ce que vous saisissez dans le calculateur ne quitte jamais votre navigateur. Le traitement des renseignements personnels est décrit dans notre <a href={route('privacy', lang)}>politique de confidentialité</a> et sur la page <a href={route('cookies', lang)}>cookies</a>.</p>

    <h2>Droit applicable</h2>
    <p>Les présentes conditions sont régies par les lois en vigueur à {LEGAL.jurisdiction} et par les lois fédérales du Canada qui s’y appliquent. Nous pouvons les modifier ; la date ci-dessous identifie la version en vigueur. Dernière mise à jour : {LAST_UPDATED}.</p>"""

META['ca-ei-calculator', 'fr', 'privacy'] = (
    'Politique de confidentialité – ${SITE_NAMES[lang]}',
    'Ce que ce site recueille sous la LPRPDE, pourquoi, pendant combien de temps, où c’est stocké, comment refuser la mesure d’audience et saisir le Commissariat.')
BODIES['ca-ei-calculator', 'fr', 'privacy'] = """    <h1>Politique de confidentialité</h1>
    <p>Cette politique explique quels renseignements personnels sont traités lorsque vous utilisez {SITE_URL}, au sens de la Loi sur la protection des renseignements personnels et les documents électroniques (LPRPDE). Si vous résidez au Québec, les droits décrits ci-dessous tiennent également compte de la Loi sur la protection des renseignements personnels dans le secteur privé, modifiée par la Loi 25.</p>

    <h2>1. Personne responsable</h2>
    <LegalIdentity lang={lang} />
    <p>Questions relatives à la vie privée : <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. {AUTHOR_NAME} est la personne responsable des renseignements personnels sous notre contrôle, conformément au premier principe de la LPRPDE.</p>

    <h2>2. Le calculateur ne transmet rien</h2>
    <p>Tous les calculs s’exécutent dans votre navigateur. Rémunération assurable, heures assurables, région économique ou code postal, nombre de semaines les mieux rémunérées et supplément familial <strong>ne sont jamais transmis à un serveur</strong>, jamais conservés et jamais reliés à un identifiant. Il n’y a ni compte, ni inscription. Si vous utilisez le lien de partage, vos saisies sont encodées dans l’URL : ne le transmettez qu’aux personnes de votre choix.</p>

    <h2>3. Ce qui est réellement recueilli</h2>
    <h3>Journaux du serveur</h3>
    <p>Notre hébergeur enregistre, à chaque requête, l’adresse IP, l’horodatage, la page demandée, le code de réponse, le navigateur et le référent. Finalité : maintenir un service disponible et sécurisé et diagnostiquer les pannes. Ces fins sont celles qu’une personne raisonnable estimerait acceptables dans les circonstances ; les journaux sont conservés 30 jours au plus.</p>
    <h3>Mesure d’audience</h3>
    <p>Nous utilisons Google Analytics 4 avec anonymisation de l’adresse IP et mode de consentement, afin de savoir quelles pages sont trouvées et utilisées. Le consentement est implicite lorsque vous poursuivez votre visite après l’avis affiché la première fois ; vous pouvez le retirer à tout moment depuis les réglages cookies du pied de page, ce qui arrête la mesure sur votre appareil. Les données d’audience sont conservées 14 mois.</p>
    <h3>Publicité</h3>
    <p>Certaines pages peuvent afficher de la publicité Google AdSense. Tant que vous ne vous y êtes pas opposé, Google peut déposer des témoins de personnalisation ; après opposition, seules des annonces non personnalisées sont diffusées. Les traitements propres à Google sont décrits dans ses <a href="https://policies.google.com/technologies/ads" rel="noopener" target="_blank">règles publicitaires</a>.</p>
    <h3>Messages que vous nous envoyez</h3>
    <p>Lorsque vous nous écrivez, votre adresse électronique et le contenu de votre message servent à vous répondre et, le cas échéant, à corriger une erreur de calcul. Cette correspondance est conservée trois ans après le dernier échange.</p>

    <h2>4. Qui y a accès</h2>
    <p>Nous ne vendons, ne louons ni n’échangeons aucun renseignement personnel. Seuls y accèdent notre hébergeur, qui agit sur nos instructions en vertu d’un contrat, et Google lorsque la mesure d’audience ou la publicité est active.</p>

    <h2>5. Stockage à l’extérieur du Canada</h2>
    <p>Notre hébergeur et Google peuvent stocker ou traiter ces renseignements à l’extérieur du Canada, notamment aux États-Unis. Ils sont alors soumis au droit de ce pays et peuvent être accessibles à ses tribunaux et à ses autorités dans le cadre d’une ordonnance légale. Nous recourons à des fournisseurs qui s’engagent contractuellement à un niveau de protection comparable, comme l’exige la LPRPDE pour les communications aux fins de traitement.</p>

    <h2>6. Vos droits</h2>
    <p>Vous pouvez demander quels renseignements personnels nous détenons à votre sujet, en exiger la rectification et contester notre conformité à la présente politique. Écrivez à <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> ; nous répondons dans les 30 jours, sans frais pour une demande courante. En l’absence de compte utilisateur, nous ne détenons généralement rien qui permette de vous identifier, et nous vous le dirons clairement.</p>
    <p>Si notre réponse ne vous satisfait pas, vous pouvez porter plainte auprès du {LEGAL.supervisoryAuthority} : <a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>.</p>

    <h2>7. Aucune décision automatisée, aucun profilage</h2>
    <p>Le montant affiché est un calcul que vous avez demandé, effectué dans votre navigateur à partir de vos propres saisies. Il n’a aucun effet juridique et ne constitue pas une décision automatisée vous concernant. Nous n’établissons aucun profil.</p>

    <h2>8. Mesures de sécurité et modifications</h2>
    <p>Le site est servi uniquement en HTTPS et ne tient aucune base de données d’utilisateurs. Cette politique peut être modifiée ; la date ci-dessous identifie la version en vigueur. Dernière mise à jour : {LAST_UPDATED}.</p>"""

# --------------------------------------------------------------------------- #
# Australie — finalpaycalculator.com.au
# Privacy Act 1988 et Australian Privacy Principles ; mention de l'ACL.
# --------------------------------------------------------------------------- #
META['au-final-pay', 'en', 'terms'] = (
    'Terms of use – ${SITE_NAMES[lang]}',
    'Who publishes this final pay calculator, what the estimates are and are not, liability, copyright, embedding the tool and the governing law.')
BODIES['au-final-pay', 'en', 'terms'] = """    <h1>Terms of use</h1>
    <p>By using this website you accept the terms below. They apply to every page and to the calculators themselves.</p>

    <h2>Publisher</h2>
    <LegalIdentity lang={lang} />
    <p>Responsible for content: {AUTHOR_NAME}.</p>

    <h2>Hosting</h2>
    <LegalIdentity mode="hosting" lang={lang} />

    <h2>What this site is — and what it is not</h2>
    <p>This site provides free calculators for final pay, redundancy and long service leave, together with explanatory guides. Results are <strong>estimates</strong> based on the Fair Work Act 2009 and the National Employment Standards, the long service leave Act of each state and territory, and the Australian Taxation Office rates for employment termination payments. They are not legal, tax or financial advice, and they do not take the place of an award, an enterprise agreement or a contract of employment, which may give you more. This site is independent and is not affiliated with the Fair Work Ombudsman, the Fair Work Commission or the ATO. What the tools cover and deliberately do not cover is set out in our <a href={route('method', lang)}>methodology</a>.</p>

    <h2>Accuracy and liability</h2>
    <p>We update the parameters at every change and test the calculators against reference cases, but we do not warrant that they are error-free or complete. Entitlements vary with the applicable award or agreement, and some situations — casual conversion, transfer of business, small business redundancy, terminations for serious misconduct — follow rules the calculators do not apply. To the fullest extent permitted by law, we exclude liability for any loss arising from reliance on an estimate or from any interruption of the service, and the site is provided "as is". Nothing in these terms excludes, restricts or modifies any guarantee, right or remedy you have under the Australian Consumer Law that cannot lawfully be excluded. If you spot an error, tell us through the <a href={route('contact', lang)}>contact page</a>; our correction process is in the <a href={route('editorial', lang)}>editorial policy</a>.</p>

    <h2>Copyright</h2>
    <p>The text, design, compiled data and source code of this site are protected under the Copyright Act 1968 and remain the property of the publisher. Reproduction or reuse without permission is prohibited, except for short quotations with a link to the source page. Legislation and government data are reproduced on the terms set by the bodies that publish them.</p>

    <h2>Embedding the calculators</h2>
    <p>You may embed a calculator free of charge in an iframe on your own site, provided the visible credit link back to this site remains and nothing suggests the tool is an official government service. Ask us for the embed code.</p>

    <h2>Links to other sites</h2>
    <p>Links to third-party sites are provided so you can verify our sources. We do not control their content and accept no responsibility for it.</p>

    <h2>Personal information and cookies</h2>
    <p>What you type into a calculator never leaves your browser. How we handle personal information is set out in our <a href={route('privacy', lang)}>privacy policy</a> and on the <a href={route('cookies', lang)}>cookies</a> page.</p>

    <h2>Governing law</h2>
    <p>These terms are governed by the laws of {LEGAL.jurisdiction}, and you submit to the non-exclusive jurisdiction of its courts. We may amend them; the date below shows the current version. Last updated: {LAST_UPDATED}.</p>"""

META['au-final-pay', 'en', 'privacy'] = (
    'Privacy policy – ${SITE_NAMES[lang]}',
    'How this site handles personal information under the Privacy Act 1988 and the APPs: what is collected, overseas disclosure, access, correction and complaints.')
BODIES['au-final-pay', 'en', 'privacy'] = """    <h1>Privacy policy</h1>
    <p>This policy sets out, as Australian Privacy Principle 1 requires, how personal information is handled when you use {SITE_URL}. We follow the Privacy Act 1988 and the Australian Privacy Principles, and we do so whether or not the small business exemption applies to us.</p>

    <h2>1. Who is responsible</h2>
    <LegalIdentity lang={lang} />
    <p>Privacy enquiries: <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>, marked for the attention of {AUTHOR_NAME}.</p>

    <h2>2. The calculators send nothing</h2>
    <p>Every calculation runs in your browser. Your pay rate, years of continuous service, state or territory, accrued leave balances and termination details <strong>are never transmitted to a server</strong>, never stored and never linked to an identifier. There is no account and no sign-up. If you use the share link, your entries are encoded in the URL — send it only to people you choose. We never ask for a tax file number, and you should not send one to us.</p>

    <h2>3. What is actually collected</h2>
    <h3>Server logs</h3>
    <p>Our hosting provider records, for each request, the IP address, timestamp, page requested, response code, browser and referring page. We collect this only for the security and reliability of the service, as APP 3 requires: it is reasonably necessary for operating the site. Logs are kept for no more than 30 days and then destroyed, in line with APP 11.2.</p>
    <h3>Analytics</h3>
    <p>We use Google Analytics 4 with IP anonymisation and Google consent mode to see which pages are found and used. The notice shown on your first visit tells you before the collection happens, as APP 5 requires. You can turn analytics off at any time through the cookie settings in the footer. Analytics data is retained for 14 months.</p>
    <h3>Advertising</h3>
    <p>Some pages may carry Google AdSense advertising. Unless you opt out, Google may set cookies to personalise ads; once you opt out, only non-personalised ads are served. Google’s own handling is described in its <a href="https://policies.google.com/technologies/ads" rel="noopener" target="_blank">advertising policies</a>. We do not use personal information for direct marketing.</p>
    <h3>Messages you send us</h3>
    <p>If you write to us, we use your email address and the content of your message to reply and, where relevant, to fix a calculation error. We keep that correspondence for three years after the last exchange, then delete it.</p>

    <h2>4. Who we disclose it to</h2>
    <p>We do not sell, rent or trade personal information, and we do not disclose it for any purpose other than the one it was collected for, unless the law requires it. Access is limited to our hosting provider, acting under contract on our instructions, and to Google where analytics or advertising is active.</p>

    <h2>5. Overseas disclosure</h2>
    <p>Our hosting provider and Google may store or process this information outside Australia, including in the United States, Ireland and other countries where they operate data centres. As APP 8 requires, we take reasonable steps to ensure those recipients handle the information consistently with the Australian Privacy Principles, through the contractual terms they commit to.</p>

    <h2>6. Access, correction and anonymity</h2>
    <p>You may ask for access to any personal information we hold about you and ask us to correct it, under APP 12 and APP 13. Write to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>; we respond within 30 days and do not charge for a routine request. You can use every calculator on this site anonymously — we have no account system, so in practice we usually hold nothing that identifies you, and we will tell you so.</p>

    <h2>7. Complaints</h2>
    <p>If you believe we have breached the Australian Privacy Principles, write to us first at the address above. We acknowledge complaints within five business days and answer within 30 days. If you are not satisfied with our response, you may complain to the {LEGAL.supervisoryAuthority}: <a href={LEGAL.supervisoryAuthorityUrl} rel="noopener" target="_blank">{LEGAL.supervisoryAuthorityUrl}</a>.</p>

    <h2>8. No automated decisions and no profiling</h2>
    <p>The figure a calculator shows is a computation you asked for, made in your browser from your own entries. It has no legal effect, it is not a decision about you, and we build no profiles.</p>

    <h2>9. Security and changes</h2>
    <p>The site is served over HTTPS only and keeps no user database, which is the most effective safeguard available to us: information we never collect cannot be misused. We may update this policy; the date below identifies the current version. Last updated: {LAST_UPDATED}.</p>"""

# --------------------------------------------------------------------------- #
# Libellés du fil d'Ariane
# --------------------------------------------------------------------------- #
BREADCRUMB = {
    ('ch-lohnrechner', 'de'):      dict(terms='Impressum', privacy='Datenschutz'),
    ('ch-lohnrechner', 'fr'):      dict(terms='Mentions légales', privacy='Protection des données'),
    ('de-arbeitslosengeld', 'de'): dict(terms='Impressum', privacy='Datenschutz'),
    ('fr-simulateur-are', 'fr'):   dict(terms='Mentions légales', privacy='Confidentialité'),
    ('es-calculadora-paro', 'es'): dict(terms='Aviso legal', privacy='Privacidad'),
    ('nl-ww-berekenen', 'nl'):     dict(terms='Disclaimer', privacy='Privacy'),
    ('ca-ei-calculator', 'en'):    dict(terms='Terms of use', privacy='Privacy'),
    ('ca-ei-calculator', 'fr'):    dict(terms='Conditions d’utilisation', privacy='Confidentialité'),
    ('au-final-pay', 'en'):        dict(terms='Terms of use', privacy='Privacy'),
}

CONFIG_NAMES = ['AUTHOR_NAME', 'CONTACT_EMAIL', 'LAST_UPDATED', 'LEGAL', 'SITE_NAMES',
                'SITE_NAME_FR', 'SITE_NAME', 'SITE_URL']


def render(site, lang, kind):
    title_tpl, desc = META[site, lang, kind]
    body = BODIES[site, lang, kind]
    hay = title_tpl + body
    # SITE_NAME est un préfixe de SITE_NAME_FR : on ne l'importe que s'il apparaît seul
    names = []
    for n in CONFIG_NAMES:
        if n == 'SITE_NAME':
            if 'SITE_NAME}' in hay or 'SITE_NAME ' in hay:
                names.append(n)
        elif n in hay:
            names.append(n)
    imports = [
        "import PageLayout from '../../layouts/PageLayout.astro';",
        "import LegalIdentity from '../../components/LegalIdentity.astro';",
        f"import {{ {', '.join(sorted(names))} }} from '../../data/site-config';",
        "import { route } from '../../i18n/routes';",
    ]
    bc = BREADCRUMB[site, lang][kind]
    return ("---\n" + "\n".join(imports) + f"\nconst lang = '{lang}';\n"
            f"const title = `{title_tpl}`;\n"
            f"const description = '{desc.replace(chr(92), chr(92)*2).replace(chr(39), chr(92)+chr(39))}';\n---\n"
            "<PageLayout title={title} description={description} lang={lang} noindex={true} "
            f"breadcrumbs={{[{{ label: '{bc}' }}]}} showAuthor={{false}}>\n"
            '  <div class="prose prose-slate max-w-none">\n' + body + "\n  </div>\n</PageLayout>\n")


written = 0
for site, cfg in SITES.items():
    for lang in cfg['langs']:
        for kind in ('terms', 'privacy'):
            url = PATHS[site, lang][kind]
            dest = os.path.join(ROOT, site, 'src/pages', url.strip('/') + '.astro')
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, 'w', encoding='utf-8').write(render(site, lang, kind))
            written += 1
            print(f'  {site}{url}')
print(f'{written} pages légales écrites')
