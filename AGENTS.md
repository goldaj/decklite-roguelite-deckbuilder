# AGENTS.md — DeckLite

## Avant toute intervention
- Lire `README.md`, puis **`docs/CHATGPT_PROJECT_HISTORY.md`** pour les décisions de conception et les limites documentaires. Consulter ensuite les documents spécialisés cités par le README.
- Mission : Prototype de roguelite Pygame concentré dans main.py : cartes, événements, récompenses et boutique méta.
- Invariants : Préserver les sauvegardes locales, éviter de fusionner le code ou le contexte avec Moonrail et Bestiaire.

## Exécution
- `python -m pip install -r requirements.txt` puis `python main.py` (Python >=3.10).
- Préserver le travail préexistant, les versions anciennes et les fichiers non concernés. Valider uniquement ce qui peut être vérifié dans l'environnement disponible.

## Continuité du contexte
- Après toute modification de projet, consulter et enrichir `docs/CHATGPT_PROJECT_HISTORY.md` avec les échanges fournis, les décisions et le résultat de la validation.
- Distinguer `Utilisateur (verbatim)`, `Assistant (verbatim)` et `Résumé reconstruit (non verbatim)`. Donner date et heure uniquement si attestées, sinon noter qu'elles manquent.
- Ne pas inventer d'échanges ou de tests. Si une transcription n'est pas accessible, demander son export plutôt que supposer son contenu.
- Le dépôt peut être public : expurger secrets, données personnelles et contenus ne relevant pas du projet. Ne pas écraser les éléments historiques.

## Option de boss extrême et règle « ennemi mort » (2026-10-29)

- Branche isolée `feat/optional-extreme-boss-combat-fix-20261029` (base `master`), PR à comparer avec #1 avant intégration.
- La mort de l'ennemi avant la fin du tour interdit sa dernière attaque. Ne pas inverser l'ordre sans tests.
- Fin de boss étage 10 = victoire encaissable **ou** défi extrême optionnel ; sur entrée du boss 11, le deck est remélangé et la main/énergie redémarrent, soin initial de 25 % des PV maximum.
- Lire `docs/OPTIONAL_EXTREME_BOSS.md`. Tests réels du moteur sans affichage : `python -m unittest discover -s tests -v` et CI GitHub. Vérifier aussi manuellement l'écran à deux boutons, la récompense unique et la continuité après le boss.
- Conserver la save locale `save.json`. Ne pas annoncer équilibrage global/compilation du GUI comme validés sur la base des tests hors écran.
