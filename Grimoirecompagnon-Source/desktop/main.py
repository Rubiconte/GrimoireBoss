"""Point d'entrée de Grimoire Compagnon (appli overlay)."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# QtWebEngine doit être importé avant la création de la QApplication.
from grimoirecompagnon.app import APP_NAME, Controller  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


def main() -> int:
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Bworkshop.GrimoireCompagnon.1")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    controller = Controller()
    controller.start()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
