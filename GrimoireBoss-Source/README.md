# Grimoire Boss

La fiche de combat des boss de Dofus : tacle, fuite, retrait PA/PM, résistances et mémos de chaque boss.

- Version web : [bworkshop.app/tacle-retrait-app](https://bworkshop.app/tacle-retrait-app/)
- Fiche : [bworkshop.app/plugins/fiche/?slug=grimoire-boss](https://bworkshop.app/plugins/fiche/?slug=grimoire-boss)

## Ce qu'il ne fait pas

- Il ne clique jamais et n'envoie aucune touche au jeu.
- Il ne lit pas la mémoire du jeu, n'injecte rien et ne touche pas au réseau du jeu.
- Il ne fait aucune capture d'écran.
- Seule connexion internet : la page web de Grimoire Boss et l'API publique de DofusDB (sorts et images).

## Les dossiers

- `web/` : l'outil lui-même (une page HTML). `monsters.json` et `memos.json` contiennent les boss et leurs mémos.
- `desktop/` : la version Windows. C'est une fenêtre toujours au premier plan qui affiche la version web en mode compact (`grimoire_boss.py`, PySide6). Elle garde seulement sa position, sa taille et tes stats dans `%APPDATA%\GrimoireBoss`.

## Construire le .exe

Dans `desktop/`, lance `build.bat` (il faut Python 3.12 et Inno Setup 6). L'installateur sort dans `desktop\dist\GrimoireBoss-Setup.exe`.
