#!/bin/sh
# Construit « Grimoire Boss.app » puis GrimoireBoss-<version>-mac-<arch>.dmg dans dist/ (à lancer sur un Mac).
# Pas de signature Apple : signature « ad hoc » seulement (obligatoire sur les Mac Apple Silicon).
set -eu
cd "$(dirname "$0")"
VERSION=$(sed -n 's/^#define AppVersion "\(.*\)"/\1/p' installer.iss)
ARCH=$(uname -m)
[ -n "$VERSION" ] || { echo "Version introuvable dans installer.iss"; exit 1; }

python3 -m pip install -q -r requirements.txt pyinstaller pillow
rm -rf build dist
python3 -m PyInstaller --noconfirm --clean --onedir --windowed --name "Grimoire Boss" --icon icon.ico \
  --osx-bundle-identifier app.bworkshop.grimoire-boss \
  --add-data "icon.ico:." --exclude-module tkinter --exclude-module PyQt6 --exclude-module PyQt5 \
  grimoire_boss.py

APP="dist/Grimoire Boss.app"
PLIST="$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$PLIST"
/usr/libexec/PlistBuddy -c "Add :CFBundleVersion string $VERSION" "$PLIST" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $VERSION" "$PLIST"
/usr/libexec/PlistBuddy -c "Add :LSMinimumSystemVersion string 11.0" "$PLIST" 2>/dev/null || true
codesign --force --deep --sign - "$APP"
codesign --verify --deep "$APP"
# Contrôle : le moteur web de Qt est bien embarqué (sinon l'appli ne s'ouvre pas).
find "$APP" -name "QtWebEngineCore.framework" -maxdepth 6 | grep -q . || { echo "QtWebEngineCore absent de l'appli"; exit 1; }

# Démarrage : l'application doit toujours tourner après 20 s (bibliothèque manquante, plantage…).
"$APP/Contents/MacOS/Grimoire Boss" &
pid=$!
sleep 20
kill -0 "$pid" 2>/dev/null || { echo "Grimoire Boss s'est arrêté au démarrage"; exit 1; }
kill "$pid"
wait "$pid" 2>/dev/null || true

DMG="dist/GrimoireBoss-$VERSION-mac-$ARCH.dmg"
STAGE=$(mktemp -d)
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname "Grimoire Boss" -srcfolder "$STAGE" -ov -format UDZO "$DMG"
rm -rf "$STAGE"
shasum -a 256 "$DMG"
echo "Fini : $DMG"
