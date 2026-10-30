# Audit de branches et passation — 30 octobre 2026

**Audit de références, pas validation du logiciel.** Branches et PR ouvertes interrogées sur GitHub. Ne pas supprimer par simple intuition.

- Dépôt : `goldaj/decklite-roguelite-deckbuilder`, branche principale : `master`.
- PR ouvertes : aucune.

## Branches recensées (3)
- `chatgpt/review-20261024`
- `feat/optional-extreme-boss-combat-fix-20261029`
- `master` (branche par défaut)

## Contre-analyse / actions de reprise
- Contrôler chaque SHA et chaque comparaison `base...head`, puis analyser les différences de fichiers pour les branches divergentes.
- Examiner PR fermées, branches de release, CI, build, assets et dépendances interbranches.
- Vérifier les tests et ne pas casser la production. Une PR déjà fusionnée ne justifie pas automatiquement la suppression d'un tag ou d'une branche utile.
- Les branches non comparées individuellement restent **à qualifier**, pas « à supprimer ».

**Statut :** inventaire GitHub effectué, audit exhaustif des diffs et exécution des tests encore nécessaires.
