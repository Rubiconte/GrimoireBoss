"""Construit la page du Grimoire Compagnon pour l'appli (Qt) ou pour le Web.

La source est web/index.html. Elle marche telle quelle avec un petit serveur local (mode dev),
et contient des marqueurs que l'on remplit ici :
  /*DATA*/null        -> données des compagnons injectées dans la page (pas de fetch)
  /*IMG*/"../data/img/" -> dossier des portraits et icônes de sorts
  /*HOST*/"web"       -> "qt" (fenêtre native) ou "web"
  <!--QWEBCHANNEL-->   -> script QWebChannel en mode appli
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def resource_root() -> Path:
    """Racine des ressources (web/ et data/), en dev comme dans l'exécutable PyInstaller."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def web_dir(root: Path | None = None) -> Path:
    return (root or resource_root()) / "web"


def data_dir(root: Path | None = None) -> Path:
    return (root or resource_root()) / "data"


def load_payload(root: Path | None = None) -> dict:
    data = json.loads((data_dir(root) / "companions_fr.json").read_text(encoding="utf-8"))
    return {"release": data["release"], "companions": data["companions"]}


def render_page(template: str, payload: dict, host: str, img_base: str, web_base: str = "") -> str:
    """Remplit les marqueurs du modèle. web_base préfixe polices et favicon (vide = chemins relatifs)."""
    def sub(html: str, old: str, new: str) -> str:
        if old not in html:
            raise ValueError(f"Marqueur introuvable dans la page : {old!r}")
        return html.replace(old, new)

    html = sub(template, "/*DATA*/null", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    html = sub(html, '/*IMG*/"../data/img/"', json.dumps(img_base))
    html = sub(html, '/*HOST*/"web"', json.dumps(host))
    channel = '<script src="qrc:///qtwebchannel/qwebchannel.js"></script>' if host == "qt" else ""
    html = sub(html, "<!--QWEBCHANNEL-->", channel)
    if web_base:
        html = html.replace('src:url("fonts/', f'src:url("{web_base}fonts/')
        html = html.replace('href="book_closed.svg"', f'href="{web_base}book_closed.svg"')
    return html


def write_qt_page(out_path: Path, root: Path | None = None) -> Path:
    """Page prête à charger en local par l'appli (fichier dans le dossier utilisateur)."""
    template = (web_dir(root) / "index.html").read_text(encoding="utf-8")
    html = render_page(
        template,
        load_payload(root),
        host="qt",
        img_base=(data_dir(root) / "img").resolve().as_uri() + "/",
        web_base=web_dir(root).resolve().as_uri() + "/",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path


def export_web_bundle(out_dir: Path, root: Path | None = None) -> Path:
    """Site statique autonome : index.html + fonts/ + img/ + book_closed.svg.

    À héberger tel quel (bworkshop.app, GitHub Pages...). Ajouter ?embed à l'URL pour
    l'intégrer en iframe plein cadre, sans fenêtre flottante ni widget.
    """
    web, data = web_dir(root), data_dir(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(web / "fonts", out_dir / "fonts", dirs_exist_ok=True)
    shutil.copy2(web / "book_closed.svg", out_dir / "book_closed.svg")
    shutil.copytree(data / "img", out_dir / "img", dirs_exist_ok=True)
    template = (web / "index.html").read_text(encoding="utf-8")
    index = out_dir / "index.html"
    index.write_text(render_page(template, load_payload(root), host="web", img_base="img/"), encoding="utf-8")
    return index
