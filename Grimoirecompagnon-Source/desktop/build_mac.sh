#!/bin/sh
# Construit « Grimoire Compagnon.app » puis GrimoireCompagnon-<version>-mac-<arch>.dmg dans dist/ (à lancer sur un Mac).
# Pas de signature Apple : signature « ad hoc » seulement (obligatoire sur les Mac Apple Silicon).
set -eu
cd "$(dirname "$0")"
VERSION=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' src/grimoirecompagnon/__init__.py)
ARCH=$(uname -m)
[ -n "$VERSION" ] || { echo "Version introuvable dans src/grimoirecompagnon/__init__.py"; exit 1; }

python3 -m pip install -q -r requirements.txt pyinstaller pillow
rm -rf build dist
mkdir -p build
# Icône de l'appli : le livre fermé de la page, en 1024 px.
QT_QPA_PLATFORM=offscreen python3 - <<'PY'
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
app = QGuiApplication([])
img = QImage(1024, 1024, QImage.Format.Format_ARGB32)
img.fill(Qt.GlobalColor.transparent)
p = QPainter(img)
QSvgRenderer("web/book_closed.svg").render(p)
p.end()
img.save("build/icon.png")
PY
python3 -m PyInstaller --noconfirm --clean --onedir --windowed --name "Grimoire Compagnon" --icon build/icon.png \
  --osx-bundle-identifier app.bworkshop.grimoire-compagnon \
  --paths src --collect-submodules grimoirecompagnon --add-data "web:web" --add-data "data:data" \
  --collect-all PySide6.QtWebEngineWidgets --collect-all PySide6.QtWebChannel \
  --exclude-module tkinter --exclude-module PyQt6 --exclude-module PyQt5 \
  main.py

APP="dist/Grimoire Compagnon.app"
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
"$APP/Contents/MacOS/Grimoire Compagnon" &
pid=$!
sleep 20
kill -0 "$pid" 2>/dev/null || { echo "Grimoire Compagnon s'est arrêté au démarrage"; exit 1; }
kill "$pid"
wait "$pid" 2>/dev/null || true

# Contrôle : la page de l'appli se construit avec les ressources embarquées.
python3 -c "import sys; sys.path.insert(0, 'src'); from pathlib import Path; from grimoirecompagnon.page import write_qt_page; print(write_qt_page(Path('build/check.html')))"

DMG="dist/GrimoireCompagnon-$VERSION-mac-$ARCH.dmg"
STAGE=$(mktemp -d)
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname "Grimoire Compagnon" -srcfolder "$STAGE" -ov -format UDZO "$DMG"
rm -rf "$STAGE"
shasum -a 256 "$DMG"
echo "Fini : $DMG"
