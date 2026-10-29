# Combat DeckLite : correction des morts et choix de boss extrême (2026-10-29)

## Anomalies du vrai code d'origine

1. `Run.end_turn()` appelait toujours `Player.end_turn(enemy)` **avant** de vérifier `enemy.hp <= 0`. Une carte létale pouvait donc laisser l'ennemi mort infliger encore sa prochaine attaque lorsque le joueur cliquait sur « Fin », jusqu'à faire perdre une run gagnée.
2. À la mort du boss d'étage 10, le jeu passait directement au boss 11, sans nouvelle main, sans régénérer l'énergie et sans possibilité de terminer la partie. La transition de puissance brutale ne laissait pas de récompense satisfaisante au boss normal.

## Fonctionnalités implémentées

- **Aucun coup de grâce après la mort :** lorsque l'ennemi est déjà à 0 PV, le joueur termine sa main et l'ennemi n'agit pas. Les attaques contre un ennemi encore vivant et les dégâts reçus restent inchangés.
- **Victoire normale à l'étage 10 :** après le boss, un écran propose « Encaisser la victoire » ou « Défi extrême ». Le premier choix termine la run en victoire et donne l'essence correspondant au boss normal.
- **Défi extrême sur décision :** le joueur conserve son deck et ses améliorations de run, regagne **25 % de ses PV max** (sans dépasser les PV max), reçoit un tirage complet et ses points d'énergie pour affronter l'étage 11. Le défi reste très dangereux : il n'existe **pas de sauvegarde en combat** ni de garantie de victoire.
- Les étages ordinaires et les événements aux étages 4, 7 et 9 restent intacts.
- La sortie « abandonner avec victoire » dépend du choix explicite après boss normal : elle ne change pas automatiquement le combat.

### Équilibrage préliminaire, non statistique

Dans les règles actuelles, une victoire arrêtée à l'étage 10 donne `12 * (10-1) + 120 = 228` essence avant autres éventuels effets. Affronter le boss extrême représente un potentiel supérieur mais plus risqué. Le soin de 25 % est une hypothèse de design initiale, **non issue d'une étude chiffrée de taux de victoire**.

La valeur fonctionnelle est d'abord le libre choix entre victoire validée et défi supplémentaire, ainsi que la disparition d'une attaque incohérente. Ne pas prétendre que l'équilibrage global est résolu.

## Vérifier sans affichage ni sauvegarde

```bash
python -m unittest discover -s tests -v
python -m py_compile main.py
```

`tests/test_boss_transition.py` charge les **vraies classes du jeu** avec une substitution limitée du module graphique `pygame`. Cela permet de tester les règles de `Run`, `Player` et `Enemy` sans assets, fenêtre, ni lectures/écritures de `save.json`. Tests : ennemi mort sans riposte, ennemi vivant infligeant toujours des dégâts, transition étage 10, victoire encaissée, transition extrême avec régénération, défaite/victoire possibles et événement ordinaire.

La CI GitHub `.github/workflows/boss-regression.yml` effectue ces tests sous Python 3.10 et 3.12 ; vérifier son **résultat réel**. Les tests ne contrôlent pas les clics et positionnement des deux boutons sur l'écran réel. Faire ce test sous Pygame après revue.

## Reprise Codex

- Dépôt `goldaj/decklite-roguelite-deckbuilder`, branche `feat/optional-extreme-boss-combat-fix-20261029`, base `master`.
- PR de revue antérieure #1 sur `chatgpt/review-20261024` laissée inchangée, vérifier la compatibilité des travaux avant toute fusion. Ne pas merger automatiquement.
- Lire `README.md`, `AGENTS.md`, `docs/CHATGPT_PROJECT_HISTORY.md` et le présent document.
- Contrôler que l'écran de choix s'affiche et que le clic « victoire » crédite l'essence **une seule fois** dans un test local avec une copie de sauvegarde.
- Vérifier sous Windows les polices/boutons et la taille de la fenêtre ; aucune interface graphique réelle n'a été lancée ici.
- Poursuivre avec une **simulation déterministe des combats** sur plusieurs archétypes de deck, 100+ seeds, comparaison survie étage 10 vs taux de victoire extrême ; ajuster les PV/attaques et soin seulement après observation.
- Ne jamais écraser `save.json` ou les sauvegardes privées d'un joueur. Aucun secret ou donnée locale n'a été consulté pour ce chantier.
