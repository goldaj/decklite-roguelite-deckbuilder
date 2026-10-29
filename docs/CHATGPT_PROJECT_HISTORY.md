# Contexte de projet ChatGPT : DeckLite

> Journal pour Codex créé le 2026-10-24. **Partiel**, car les exports complets de toutes les conversations ChatGPT ne sont pas accessibles dans cette session. Les résumés ci-dessous ne sont pas des citations.

## Périmètre et état vérifiables
- Dépôt : `goldaj/decklite-roguelite-deckbuilder`.
- Objet d'après le README : Prototype de roguelite Pygame concentré dans main.py : cartes, événements, récompenses et boutique méta.
- Invariants : Préserver les sauvegardes locales, éviter de fusionner le code ou le contexte avec Moonrail et Bestiaire.
- Entrée de vérification : `python -m pip install -r requirements.txt` puis `python main.py` (Python >=3.10).

## Échanges et références retrouvés

2026-10-18 — Assistant, résumé non verbatim : inventaire des variantes de deckbuilders.

2026-10-18 13:24:13 UTC — Utilisateur (extrait exact) : « N'écrase aucun repo existant. »

2026-10-24 — Utilisateur (verbatim, heure indisponible) : « je te demande de lire mes repo git où tu es le dernier utilisateur, de rajouter un AGENTS.md pertinent s’il n’y en a pas. Mais en plus, tu rajoutera un document repérable par codex [...] où tu mets l’intégralité de nos échanges liés à ce projet. Mes questions, tes réponses [...] et les horodatages si tu les as. » (extrait avec ellipses signalées, donc non intégral).

## À compléter avec les transcriptions sources
**Manquent :** questions/réponses intégrales de chaque session de conception, horaires individuels de certains messages et échanges Codex non publiés. Ne jamais reconstituer un dialogue en prétendant citer des propos exacts.

Lorsque des exports ChatGPT authentiques sont fournis, les archiver par session, avec date ISO/fuseau, rôles et texte intégral en préservant leur ordre. Revoir toute donnée sensible avant de pousser sur GitHub. Après chaque modification, ajouter les échanges exacts nouvellement disponibles, puis actualiser les décisions et l'état vérifié.

## 2026-10-24 : revue multi-dépôts en parallèle de Codex (heure non attestée)

**Utilisateur (verbatim, conversation présente)**

> tu vois tout le boulot qu'on a fait sur la conversation Avancement projets codex ?
> Tu vas refaire la même chose sur TOUT mon repo git. Tu vas commencer par les projets les plus gros, regarder ce que tu peux faire dessus et le faire sur ta branch (même consignes que sur l'autre conversation).
> Tu vas ensuite me faire un rapport très succint des projets que t'as touché et de ce que t'as avancé dessus.
> Amuse toi !

**Assistant (résumé reconstruit, non verbatim)**

Contrôleur hors-ligne de syntaxe et de structure de la sauvegarde par défaut, tests de rejets et CI. Travail isolé sur `chatgpt/review-20261024`, base inchangée.

**Validation et confiance** : confiance élevée dans la modification ciblée ; ne pas supposer des tests locaux exécutés. Vérifier GitHub Actions et comparer avec le travail Codex avant intégration. Ne pas fusionner automatiquement. Aucun secret ou contenu privé de manuscrit ajouté.

## Intervention du 29 octobre 2026 — boss extrême optionnel (résumé non verbatim)

- Demande utilisateur dans le projet : poursuivre de façon autonome les évolutions GitHub utiles et documenter Codex ; intérêt explicite antérieur pour l'équilibrage des jeux.
- Inspection du dépôt DeckLite : branche `master` et ancienne PR #1 séparée. `Run.end_turn` laissait l'ennemi déjà mort agir avant de déclencher la victoire ; le boss étage 10 passait automatiquement au boss 11 sans reconstituer la main.
- Branche `feat/optional-extreme-boss-combat-fix-20261029` : bloquer l'attaque d'un ennemi déjà mort, proposer de terminer la run après boss 10 ou de poursuivre sur un défi extrême avec nouvelle main/énergie et soin de 25 % PV max. Tests de l'authentique moteur `Run/Player/Enemy` avec Pygame simulé, et CI 3.10/3.12.
- Il n'a pas été effectué de test sur interface Pygame graphique, de simulation d'équilibrage multi-seeds, ni d'accès aux sauvegardes personnelles. Seules les exécutions de CI réellement observées font foi.
- Lire `docs/OPTIONAL_EXTREME_BOSS.md` ; comparer aux changements PR #1 et ne pas fusionner sans revue.
