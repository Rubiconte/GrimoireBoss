# Grimoire Compagnon : appli de bureau

Fenêtre « livre ouvert » toujours au-dessus du jeu, qui affiche la page des compagnons, et petit livre flottant quand elle est refermée.

- `main.py` : point d'entrée.
- `src/grimoirecompagnon/` : l'appli (`app.py`) et la construction de la page (`page.py`).
- `web/index.html` : modèle de la page, avec les marqueurs remplis par `page.py`.
- `data/` : données des compagnons (`companions_fr.json`) et images.

Ce code source a été reconstitué depuis l'exécutable publié en 0.1.0 (GrimoireCompagnon-Setup.exe). Une fois recompilé, il donne exactement le même bytecode Python.

Lancer depuis les sources : `pip install -r requirements.txt` puis `python main.py`.
