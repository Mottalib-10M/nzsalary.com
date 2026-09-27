# -*- coding: utf-8 -*-
"""Les champs du formulaire et la fonction de calcul parlent-ils de la meme chose ?

Le simulateur d'indemnite de licenciement rendait toujours zero parce que son
formulaire posait deux champs d'anciennete -- annees et mois -- quand sa fonction
n'en lisait qu'un, qu'elle prenait pour le total. Rien dans le code ne le
signalait : les deux cotes compilent, le site se construit, et le resultat est
faux en silence.

Ce controle compare, pour chaque simulateur :
  - les `name` des champs declares dans le formulaire, contre les `inputs.X` que
    la fonction lit reellement. Un champ declare et jamais lu est inerte ; une
    lecture sans champ correspondant vaut toujours zero ;
  - les `key` des resultats affiches, contre les cles que la fonction renvoie.
    Un resultat affiche mais jamais produit laisse une ligne vide.
"""
import io, re, sys

CLIENT = 'src/app/simulateurs/[slug]/SimulatorClient.tsx'
CALCULS = 'src/lib/calculations.ts'

client = io.open(CLIENT, encoding='utf8').read()
calculs = io.open(CALCULS, encoding='utf8').read()

# Decoupe des configurations de simulateur : "slug": { ... calculate: fn },
config = re.compile(r'"([a-z0-9-]+)":\s*\{\s*\n\s*fields:(.*?)calculate:\s*(\w+),', re.S)
fonction = re.compile(r'export function (\w+)\(\s*inputs[^)]*\)[^{]*\{(.*?)\n\}', re.S)
corps = {m.group(1): m.group(2) for m in fonction.finditer(calculs)}

soucis = []
for m in config.finditer(client):
    slug, bloc, nom_fn = m.group(1), m.group(2), m.group(3)
    if nom_fn not in corps:
        soucis.append(f'{slug} : fonction {nom_fn} introuvable')
        continue
    src = corps[nom_fn]
    champs = set(re.findall(r'name:\s*"(\w+)"', bloc))
    lus = set(re.findall(r'inputs\.(\w+)', src)) | set(re.findall(r'inputs\["(\w+)"\]', src))
    resultats = set(re.findall(r'\{\s*key:\s*"(\w+)"', bloc))
    # Cles renvoyees : le dernier objet `return { ... }` de la fonction.
    rendus = set()
    for ret in re.findall(r'return\s*\{(.*?)\n\s*\};', src, re.S):
        rendus |= set(re.findall(r'^\s*(\w+):', ret, re.M))

    inertes = champs - lus
    fantomes = lus - champs
    vides = resultats - rendus
    if inertes:
        soucis.append(f'{slug} : champ(s) saisi(s) mais jamais lu(s) par le calcul → {sorted(inertes)}')
    if fantomes:
        soucis.append(f'{slug} : le calcul lit des entrées absentes du formulaire (valent 0) → {sorted(fantomes)}')
    if vides:
        soucis.append(f'{slug} : résultat(s) affiché(s) mais jamais produit(s) → {sorted(vides)}')

print(f'{len(list(config.finditer(client)))} simulateur(s) examiné(s), {len(soucis)} incohérence(s)')
for s in soucis:
    print('  ' + s)
sys.exit(1 if soucis else 0)
