# DeckLite — roguelite deckbuilder

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
| [Bestiaire](https://github.com/goldaj/roguelite-bestiary-deckbuilder) | Créatures, cartes et attrition persistante au fil des combats | Prototype autonome, moteur `core/` et tests ; progression encore à corriger |
| [DeckLite](https://github.com/goldaj/decklite-roguelite-deckbuilder) | Construire son deck pendant une run, choisir des récompenses, événements et boutique méta | Prototype Pygame concentré dans `main.py` |
| [Exploration sur tuiles](https://github.com/goldaj/tilemap-exploration-roguelite) | Se déplacer sur une grille, rencontrer des ennemis, gérer objets et boutique | Modules monde/combat/interface, tuiles et sprites |
| [Chess Roguelite](https://github.com/goldaj/chess-roguelite) | Déplacer des pièces d'échecs et acquérir des améliorations entre les affrontements | Plateau, IA, progression et interface souris |
| [Idle Clicker](https://github.com/goldaj/idle-clicker-tkinter) | Clics, revenus et achats avec coût dynamique | Interface de bureau Tkinter/ttkbootstrap |

Ces dépôts conservent des expériences distinctes, à différents niveaux d'avancement.
