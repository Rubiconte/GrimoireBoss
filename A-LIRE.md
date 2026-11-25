# Grimoire Boss et Grimoire Compagnon sur GitHub Pages

But : que les versions web tournent sur `rubiconte.github.io` (comme Grimoire), et plus sur bworkshop.app.

## 1. Envoyer les fichiers (5 minutes)

1. Ouvre https://github.com/rubiconte/GrimoireBoss/upload/main
2. Glisse **le contenu** de ce dossier (pas le dossier lui-même) :
   - `.nojekyll`
   - `GrimoireBoss-Source`
   - `Grimoirecompagnon-Source`
3. Les fichiers vont se ranger dans les dossiers qui existent déjà :
   - Grimoire Boss : polices incluses dans `web/fonts/`, `index.html` pointe dessus
   - Compagnon : polices `.woff2` plus légères
4. Clique sur **Commit changes**.

(Ce fichier `A-LIRE.md` n'est pas utile sur GitHub, tu peux ne pas le glisser.)

## 2. Activer GitHub Pages (1 minute)

1. Va dans **Settings** du dépôt GrimoireBoss → **Pages** (menu de gauche).
2. Dans **Build and deployment** :
   - Source : **Deploy from a branch**
   - Branch : **main**, dossier **/ (root)**
3. Clique sur **Save**, puis attends 1 à 2 minutes.

## 3. Vérifier

Ces deux adresses doivent afficher les outils :

- https://rubiconte.github.io/GrimoireBoss/GrimoireBoss-Source/web/
- https://rubiconte.github.io/GrimoireBoss/Grimoirecompagnon-Source/web/

Préviens Bworkshop quand c'est bon : les fiches du site seront basculées sur ces adresses,
et les anciennes adresses bworkshop.app redirigeront automatiquement.

## Ensuite, pour les mises à jour

Il suffit de mettre à jour les fichiers du dossier `web/` sur GitHub. Le site les affiche directement,
sans validation à attendre.
