# Audit GitHub indépendant et passation (2026-10-30) — goldaj/decklite-roguelite-deckbuilder

Contrôle des références, PR, racine, README. Les tests et une partie jouable n'ont pas été exécutés.

## Branches
`master` : `758542064be56ecfb9be05de5dc5a9b9956cbb11`.
- `chatgpt/review-20261024`: **behind** (0 commits exclusifs / 10 derrière). Historique inclus dans master ; branche redondante à vérifier puis retirer.
- `feat/optional-extreme-boss-combat-fix-20261029`: **behind** (0 commits exclusifs / 1 derrière). Historique inclus dans master ; branche redondante à vérifier puis retirer.

## PR
- [#2](https://github.com/goldaj/decklite-roguelite-deckbuilder/pull/2) : closed, fusionnée ; feat: prevent dead enemy retaliation and make floor-11 boss optional
- [#1](https://github.com/goldaj/decklite-roguelite-deckbuilder/pull/1) : closed, fusionnée ; [ChatGPT] Validation hors-ligne du prototype et des sauvegardes

## Périmètre
Racine : `.github`, `.gitignore`, `AGENTS.md`, `README.md`, `assets`, `docs`, `main.py`, `requirements.txt`, `run.bat`, `run.sh`, `save.default.json`, `tests`, `tools`.

README : # DeckLite — roguelite deckbuilder

Prototype Pygame de construction de deck pendant une run : cartes, ennemis, choix de récompenses, événements, repos et boutique méta. Le code conserve une version sans minuterie.

## Installation et lancement

Dans un environnement virtuel Python 3.10 ou plus récent :

```bash
python -m pip install -r requirements.txt
python main.py
```

L'interface se pilote à la souris. `main.py` rassemble les cartes, les entités de combat, les écrans et la logique de run. `save.default.json` fournit une sauvegarde initiale ; la progression personnelle dans `save.json` reste locale et est ignorée par Git.

Il s'agit d'un prototype en développement ; sa structure monolithique fait partie des axes de refactorisation possibles.

## Situer ce prototype parmi les autres jeux

| Projet | Expérience explorée | Organisation du code |
| --- | --- | --- |
| [Moonrail](https://github.com/goldaj/moonrail-narrative-deckbuilder) | Deckbuilding narratif, collection et progression persistante | Projet distinct, avec sa direction de produit et ses personnages |
| [Bestiaire](https://github.com/goldaj/roguelite-bestiary-deckbuilder) | Créatures, cartes et attrition persistante au fil des combats | Prototype autonome, moteur `co

## Remise en cause / test de valeur
1. Vérifier qu'un ennemi mort n'effectue aucune contre-attaque après la correction du combat.
2. Vérifier que le boss du niveau 11 est réellement facultatif et que les embranchements ne bloquent pas la progression.
3. Mesurer l'équilibrage : taux de victoire, gain de ressources, difficulté des premiers étages et pics artificiels.
4. Tester sauvegarde/rechargement et invariants de combat via CI et session manuelle ; ne pas supposer ces tests verts.
5. Les deux branches secondaires ont 0 commit exclusif : vérifier les anciens workflows/PR avant suppression, ne pas créer de PR supplémentaire.
