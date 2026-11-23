# Grimoire Compagnon

La fiche des compagnons de Dofus : stats selon le niveau, sorts et éléments de chaque compagnon.

- Version web : [bworkshop.app/grimoire-compagnon-app](https://bworkshop.app/grimoire-compagnon-app/)
- Fiche : [bworkshop.app/plugins/fiche/?slug=grimoire-compagnon](https://bworkshop.app/plugins/fiche/?slug=grimoire-compagnon)

## Ce qu'il ne fait pas

- Il ne clique jamais et n'envoie aucune touche au jeu.
- Il ne lit pas la mémoire du jeu, n'injecte rien et ne touche pas au réseau du jeu.
- Il ne fait aucune capture d'écran et n'a besoin d'aucune connexion internet : tout est dans la page.

## Le dossier

- `web/index.html` : l'outil entier. Les données des compagnons sont dans la page (constante `DATA`).
- `web/img/` : portraits des compagnons et icônes des sorts, issus du jeu (© Ankama).
- `web/fonts/` : polices Alegreya (licence SIL OFL, voir `fonts/OFL.txt`).

Pour l'utiliser hors ligne, ouvre `web/index.html` dans un navigateur.
