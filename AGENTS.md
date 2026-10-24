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
