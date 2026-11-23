"""Grimoire Boss pour Windows : la fiche de combat des boss, dans une fenêtre toujours au-dessus de Dofus.

- La fenêtre, sans cadre Windows, affiche la version en ligne de Grimoire Boss (toujours à jour) en mode compact.
  On la déplace par sa barre du haut et on l'agrandit par ses bords.
- Le livre ouvert à gauche de la recherche referme le grimoire : la fenêtre se replie et laisse un petit
  livre flottant, déplaçable et toujours au premier plan. Un clic sur le livre le rouvre.
  Clic droit sur le livre : ouvrir ou quitter.
- Position, taille et stats saisies (fuite, retrait, résistances) sont gardées d'une session à l'autre.
Aucune lecture de la mémoire du jeu, aucune interception réseau, aucune automatisation.
"""
import json
import math
import os
import sys

from PySide6.QtCore import (QByteArray, QEasingCurve, QFile, QIODevice, QObject, QPoint, QPointF, QRectF, Qt,
                            QTimer, QUrl, QVariantAnimation, Slot)
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QRadialGradient, QTransform
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMenu, QVBoxLayout, QWidget

APP_NAME = 'Grimoire Boss'
APP_URL = 'https://bworkshop.app/tacle-retrait-app/?widget=1'
DATA_DIR = os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'), 'GrimoireBoss')
STATE_FILE = os.path.join(DATA_DIR, 'fenetre.json')
DEFAULT = {'width': 480, 'height': 820}
BOOK_WIN = 96     # taille de la fenêtre du petit livre (marge pour l'ombre et le survol)
BOOK_SIZE = 66    # taille du livre dessiné
# Où se trouve le livre ouvert dans la fenêtre : le petit livre apparaît (et la fenêtre se rouvre) à cet endroit
BTN_OFFSET = QPoint(12, 10)


def resource(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


# ---------- Le livre fermé (même dessin que l'icône), en trois calques pour l'animation ----------
_DEFS = """<defs>
<linearGradient id="lt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8e3424"/><stop offset=".55" stop-color="#6a2216"/><stop offset="1" stop-color="#47150d"/></linearGradient>
<linearGradient id="sp" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3a0f09"/><stop offset="1" stop-color="#5a1b11"/></linearGradient>
<linearGradient id="gd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe7a1"/><stop offset=".45" stop-color="#f0c35a"/><stop offset="1" stop-color="#b9801e"/></linearGradient>
<linearGradient id="pg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e9d6a8"/><stop offset="1" stop-color="#c9ad74"/></linearGradient>
<radialGradient id="gm" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#ffe0a0"/><stop offset=".35" stop-color="#ff8a3c"/><stop offset="1" stop-color="#b8320e"/></radialGradient>
<radialGradient id="gw" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffb02e" stop-opacity=".75"/><stop offset="1" stop-color="#ffb02e" stop-opacity="0"/></radialGradient>
</defs>"""


def _svg(body):
    return ('<svg viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">' + _DEFS + body + '</svg>').encode()


BOOK_BASE = _svg("""
<ellipse cx="128" cy="226" rx="88" ry="13" fill="#000" opacity=".35"/>
<rect x="58" y="42" width="160" height="172" rx="14" fill="#3b220f"/>
<rect x="62" y="46" width="152" height="164" rx="12" fill="url(#pg)"/>
<path d="M206 56v144M200 54v148M194 52v152" stroke="#a88a55" stroke-width="2" opacity=".6"/>""")

BOOK_COVER = _svg("""
<rect x="34" y="32" width="166" height="176" rx="16" fill="#2a0c08"/>
<rect x="37" y="35" width="160" height="170" rx="14" fill="url(#lt)"/>
<rect x="37" y="35" width="24" height="170" rx="12" fill="url(#sp)"/>
<rect x="72" y="52" width="112" height="136" rx="10" fill="none" stroke="#a5473a" stroke-opacity=".55" stroke-width="3"/>
<g transform="translate(128 122)">
<path d="M-30 -14C-52 -18-60-38-50-58C-46-40-36-32-22-30Z" fill="url(#gd)" stroke="#6b3e0c" stroke-width="3" stroke-linejoin="round"/>
<path d="M30 -14C52 -18 60-38 50-58C46-40 36-32 22-30Z" fill="url(#gd)" stroke="#6b3e0c" stroke-width="3" stroke-linejoin="round"/>
<path d="M0-40C-24-40-36-24-36-4C-36 10-28 18-20 22L-20 36L20 36L20 22C28 18 36 10 36-4C36-24 24-40 0-40Z" fill="url(#gd)" stroke="#6b3e0c" stroke-width="3" stroke-linejoin="round"/>
<path d="M-23-8C-23-16-9-16-8-6C-8 2-22 3-23-8Z" fill="#3a1208"/>
<path d="M23-8C23-16 9-16 8-6C8 2 22 3 23-8Z" fill="#3a1208"/>
<path d="M0 6L-6 16L6 16Z" fill="#3a1208"/>
<path d="M-12 24v12M0 24v12M12 24v12" stroke="#6b3e0c" stroke-width="3" stroke-linecap="round"/>
<circle cx="0" cy="-26" r="6.5" fill="url(#gm)" stroke="#6b3e0c" stroke-width="2"/>
</g>
<g fill="url(#gd)" stroke="#6b3e0c" stroke-width="2.5" stroke-linejoin="round">
<path d="M30 70V40Q30 28 42 28H72V42H48Q44 42 44 46V70Z"/>
<path d="M204 70V40Q204 28 192 28H162V42H186Q190 42 190 46V70Z"/>
<path d="M30 170V200Q30 212 42 212H72V198H48Q44 198 44 194V170Z"/>
<path d="M204 170V200Q204 212 192 212H162V198H186Q190 198 190 194V170Z"/>
</g>""")

BOOK_GLOW = _svg('<circle cx="128" cy="96" r="17" fill="url(#gw)"/>')

# Le livre ouvert du bouton « refermer le grimoire », mêmes couleurs que le livre fermé
OPEN_BOOK_SVG = """<svg viewBox="0 0 64 48" aria-hidden="true"><defs>
<linearGradient id="gbLea" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9a3a28"/><stop offset=".5" stop-color="#6a2216"/><stop offset="1" stop-color="#3f120b"/></linearGradient>
<linearGradient id="gbPg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f1e1b8"/><stop offset="1" stop-color="#cfb27a"/></linearGradient>
<linearGradient id="gbGd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe7a1"/><stop offset=".45" stop-color="#f0c35a"/><stop offset="1" stop-color="#b9801e"/></linearGradient>
<radialGradient id="gbGm" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#ffe0a0"/><stop offset=".35" stop-color="#ff8a3c"/><stop offset="1" stop-color="#b8320e"/></radialGradient>
<radialGradient id="gbGw" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffb02e" stop-opacity=".7"/><stop offset="1" stop-color="#ffb02e" stop-opacity="0"/></radialGradient>
</defs>
<ellipse cx="32" cy="44" rx="27" ry="3" fill="#000" opacity=".35"/>
<path d="M3 13Q32 7 61 13V41Q32 35 3 41Z" fill="url(#gbLea)" stroke="#2a0c08" stroke-width="1.2"/>
<path d="M7 11Q20 6 31 11V38Q20 33 7 37Z" fill="url(#gbPg)"/>
<path d="M33 11Q44 6 57 11V37Q44 33 33 38Z" fill="url(#gbPg)"/>
<path d="M11 16q9-3 16 0M11 21q9-3 16 0M11 26q9-3 16 0M37 16q9-3 16 0M37 21q9-3 16 0M37 26q9-3 16 0" stroke="#a5473a" stroke-width=".9" fill="none" opacity=".6"/>
<path d="M32 11V39" stroke="url(#gbGd)" stroke-width="1.6"/>
<circle cx="32" cy="9" r="7.5" fill="url(#gbGw)"/>
<circle cx="32" cy="9" r="3.2" fill="url(#gbGm)" stroke="#6b3e0c" stroke-width="1"/>
<path d="M3 37v4l5-1M61 37v4l-5-1" fill="none" stroke="url(#gbGd)" stroke-width="2.4" stroke-linecap="round"/>
</svg>"""

# ---------- Ce qui est ajouté dans la page de l'outil quand elle tourne dans l'appli ----------
INJECT_CSS = """
html.gbqt,html.gbqt body{background:transparent!important;overflow:hidden!important;height:100%}
html.gbqt .wrap{position:fixed!important;inset:0!important;margin:0!important;max-width:none!important;
  overflow-y:auto;overflow-x:hidden;border-radius:14px!important;border:1px solid rgba(217,180,107,.28)!important;
  box-shadow:inset 0 1px 0 rgba(255,240,210,.07)!important;background:linear-gradient(180deg,#1d1913 0,#181510 220px)!important;
  transform-origin:0 0;scrollbar-width:thin;scrollbar-color:rgba(217,180,107,.35) transparent}
html.gbqt .wrap::-webkit-scrollbar{width:8px}
html.gbqt .wrap::-webkit-scrollbar-thumb{background:rgba(217,180,107,.3);border-radius:8px;border:2px solid transparent;background-clip:padding-box}
html.gbqt .topbar{position:sticky;top:0;z-index:40;background:linear-gradient(180deg,#1d1913,#1b1712);
  grid-template-columns:auto minmax(0,1fr)!important;cursor:move;margin:0 -18px;padding-left:12px!important;padding-right:12px!important}
html.gbqt body.widget-mode .topbar{margin:0 -12px}
html.gbqt .topbar-brand,html.gbqt .topbar-count,html.gbqt #btn-widget-mode{display:none!important}
html.gbqt .topbar input,html.gbqt .topbar button,html.gbqt .topbar .dropdown{cursor:auto}
html.gbqt .topbar button{cursor:pointer}
#gb-book-btn{width:40px;height:32px;display:grid;place-items:center;padding:0;border:0;background:none;border-radius:8px;
  cursor:pointer;transition:transform .15s,filter .15s}
#gb-book-btn:hover{transform:translateY(-1px) scale(1.06);filter:drop-shadow(0 0 6px rgba(255,176,46,.45))}
#gb-book-btn:focus-visible{outline:2px solid rgba(217,180,107,.7);outline-offset:1px}
#gb-book-btn svg{width:36px;height:27px;display:block}
html.gbqt .wrap.gb-in{animation:gbWin .22s cubic-bezier(.2,.8,.2,1)}
html.gbqt .wrap.gb-out{animation:gbWin .16s cubic-bezier(.6,0,.8,.4) reverse forwards}
@keyframes gbWin{from{opacity:0;transform:scale(.18)}to{opacity:1;transform:none}}
.gb-grip{position:fixed;z-index:100}
.gb-grip.r{top:14px;bottom:14px;right:0;width:5px;cursor:ew-resize}
.gb-grip.l{top:14px;bottom:14px;left:0;width:5px;cursor:ew-resize}
.gb-grip.b{left:14px;right:14px;bottom:0;height:5px;cursor:ns-resize}
.gb-grip.br{right:0;bottom:0;width:16px;height:16px;cursor:nwse-resize}
.gb-grip.bl{left:0;bottom:0;width:16px;height:16px;cursor:nesw-resize}
"""

INJECT_JS = r"""(function(){
if(window.__gbqt)return;window.__gbqt=true;
var root=document.documentElement;root.classList.add('gbqt');
var css=document.createElement('style');css.textContent=__CSS__;document.head.appendChild(css);
var bridge=null;
new QWebChannel(qt.webChannelTransport,function(ch){bridge=ch.objects.bridge;});
function setup(){
  var bar=document.querySelector('.topbar'),wrap=document.querySelector('.wrap');
  if(!bar||!wrap||document.getElementById('gb-book-btn'))return;
  var b=document.createElement('button');
  b.id='gb-book-btn';b.type='button';b.title='Refermer le grimoire';b.setAttribute('aria-label','Refermer le grimoire');
  b.innerHTML=__OPEN_BOOK__;
  bar.insertBefore(b,bar.firstChild);
  var busy=false;
  b.addEventListener('click',function(e){
    e.stopPropagation();if(busy)return;busy=true;
    var dd=document.getElementById('dropdown');if(dd)dd.hidden=true;
    wrap.classList.remove('gb-in');wrap.classList.add('gb-out');
    setTimeout(function(){bridge&&bridge.collapse();},150);
    setTimeout(function(){wrap.classList.remove('gb-out');busy=false;},420);
  });
  bar.addEventListener('pointerdown',function(e){
    if(e.button!==0||e.target.closest('button,input,select,a,.dropdown'))return;
    e.preventDefault();bridge&&bridge.startMove();
  });
  ['r','l','b','br','bl'].forEach(function(k){
    var g=document.createElement('div');g.className='gb-grip '+k;
    g.addEventListener('pointerdown',function(e){if(e.button!==0)return;e.preventDefault();bridge&&bridge.startResize(k);});
    document.body.appendChild(g);
  });
  // appelé par l'appli quand la fenêtre réapparaît
  window.gbPlayOpen=function(){wrap.classList.remove('gb-in','gb-out');void wrap.offsetWidth;wrap.classList.add('gb-in');
    setTimeout(function(){wrap.classList.remove('gb-in');},260);};
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();
})();""".replace('__CSS__', json.dumps(INJECT_CSS)).replace('__OPEN_BOOK__', json.dumps(OPEN_BOOK_SVG))

OFFLINE_PAGE = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:transparent;color:#efe7d7;font:15px/1.45 'Segoe UI',sans-serif;overflow:hidden}
main{position:fixed;inset:0;border-radius:14px;border:1px solid rgba(217,180,107,.28);background:#181510;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;padding:24px;text-align:center;box-sizing:border-box}
h1{margin:0;font:700 20px Georgia,serif;letter-spacing:.04em;color:#f0d394}
p{margin:0;color:#a39882;max-width:320px}
button{height:34px;padding:0 16px;border-radius:8px;border:1px solid rgba(217,180,107,.35);background:rgba(217,180,107,.13);color:#f0d394;font:600 14px 'Segoe UI',sans-serif;cursor:pointer}
button:hover{background:rgba(217,180,107,.22)}
</style></head><body><main>
<h1>Grimoire Boss</h1>
<p>Pas de connexion à Internet. Grimoire Boss a besoin d'Internet pour charger les boss et leurs sorts.</p>
<button onclick="location.href='__URL__'">Réessayer</button>
</main></body></html>""".replace('__URL__', APP_URL)


# ---------- Mémoire de la fenêtre ----------
def load_state():
    try:
        with open(STATE_FILE, encoding='utf-8') as f:
            raw = json.load(f)
    except Exception:
        raw = {}
    state = dict(DEFAULT)
    for k in ('x', 'y', 'width', 'height', 'book_x', 'book_y'):
        if isinstance(raw.get(k), int):
            state[k] = raw[k]
    state['collapsed'] = bool(raw.get('collapsed'))
    state['width'] = max(360, min(state['width'], 2400))
    state['height'] = max(420, min(state['height'], 2400))
    # Écran débranché depuis la dernière fois : on oublie les positions hors écran
    for kx, ky in (('x', 'y'), ('book_x', 'book_y')):
        if kx in state and QGuiApplication.screenAt(QPoint(state[kx] + 30, state[ky] + 20)) is None:
            state.pop(kx, None)
            state.pop(ky, None)
    return state


def save_state(state):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        keep = {k: int(v) for k, v in state.items() if k != 'collapsed' and isinstance(v, (int, float))}
        keep['collapsed'] = bool(state.get('collapsed'))
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(keep, f)
    except Exception:
        pass


def keep_on_screen(x, y, w, h):
    screen = QGuiApplication.screenAt(QPoint(x + w // 2, y + h // 2)) or QGuiApplication.primaryScreen()
    a = screen.availableGeometry()
    return max(a.left(), min(x, a.right() - w + 1)), max(a.top(), min(y, a.bottom() - h + 1))


# ---------- Le petit livre flottant ----------
class BookWidget(QWidget):
    def __init__(self, app):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.NoDropShadowWindowHint)
        self.app = app
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(BOOK_WIN, BOOK_WIN)
        self.setWindowTitle(APP_NAME + ' (livre)')
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip('Clic : ouvrir Grimoire Boss · Clic droit : menu')
        self.base, self.cover, self.glow = QSvgRenderer(QByteArray(BOOK_BASE)), QSvgRenderer(QByteArray(BOOK_COVER)), QSvgRenderer(QByteArray(BOOK_GLOW))
        self.hover = 0.0     # 0 → 1 au survol
        self.opening = 0.0   # 0 → 1 : la couverture se rabat
        self.pop = 1.0       # 0 → 1 : apparition
        self.phase = 0.0     # pulsation de la gemme
        self.dragging = False
        self.press = None
        self.busy = False

        self.hover_anim = QVariantAnimation(self, duration=150, easingCurve=QEasingCurve.OutCubic)
        self.hover_anim.valueChanged.connect(lambda v: self._set('hover', v))
        self.pop_anim = QVariantAnimation(self, startValue=0.0, endValue=1.0, duration=240, easingCurve=QEasingCurve.OutBack)
        self.pop_anim.valueChanged.connect(lambda v: self._set('pop', v))
        self.open_anim = QVariantAnimation(self, startValue=0.0, endValue=1.0, duration=210, easingCurve=QEasingCurve.InCubic)
        self.open_anim.valueChanged.connect(lambda v: self._set('opening', v))
        self.open_anim.finished.connect(self._opened)
        self.gem = QTimer(self, interval=50)
        self.gem.timeout.connect(self._tick)

    def _set(self, name, value):
        setattr(self, name, float(value))
        self.update()

    def _tick(self):
        self.phase = (self.phase + 0.05 / 2.4) % 1.0
        self.update()

    def appear(self, pos):
        x, y = keep_on_screen(pos.x(), pos.y(), BOOK_WIN, BOOK_WIN)
        self.move(x, y)
        self.opening, self.pop, self.busy = 0.0, 0.0, False
        self.show()
        self.raise_()
        self.pop_anim.start()
        self.gem.start()

    def disappear(self):
        self.gem.stop()
        self.hide()

    # dessin
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        c = BOOK_WIN / 2
        scale = (0.4 + 0.6 * self.pop) * (1 + 0.05 * self.hover + (0.03 if self.dragging else 0))
        p.setOpacity(min(1.0, max(0.0, self.pop * 1.6)))
        if self.hover > 0:  # halo doré au survol
            g = QRadialGradient(QPointF(c, c), BOOK_SIZE * 0.62)
            g.setColorAt(0, QColor(255, 176, 46, int(70 * self.hover)))
            g.setColorAt(1, QColor(255, 176, 46, 0))
            p.setPen(Qt.NoPen)
            p.setBrush(g)
            p.drawEllipse(QPointF(c, c), BOOK_SIZE * 0.62, BOOK_SIZE * 0.62)
        p.translate(c, c - 2 * self.hover)
        p.scale(scale, scale)
        p.translate(-BOOK_SIZE / 2, -BOOK_SIZE / 2)
        box = QRectF(0, 0, BOOK_SIZE, BOOK_SIZE)
        self.base.render(p, box)
        # couverture : pivote autour de son bord gauche (x=34/256), comme une page qu'on tourne
        k = BOOK_SIZE / 256
        t = self.opening
        p.save()
        hinge = QPointF(34 * k, 120 * k)
        tr = QTransform()
        tr.translate(hinge.x(), hinge.y())
        tr.shear(0, -math.tan(math.radians(6)) * t)
        tr.scale(1 - 0.95 * t, 1)
        tr.translate(-hinge.x(), -hinge.y())
        p.setTransform(tr, True)
        self.cover.render(p, box)
        p.setOpacity(p.opacity() * (0.45 + 0.55 * (0.5 + 0.5 * math.cos(self.phase * 2 * math.pi))))
        self.glow.render(p, box)
        p.restore()

    # souris : clic = ouvrir, glisser = déplacer, clic droit = menu
    def enterEvent(self, _):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self.hover)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()

    def leaveEvent(self, _):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self.hover)
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.press = (e.globalPosition().toPoint(), self.pos())

    def mouseMoveEvent(self, e):
        if not self.press:
            return
        start, origin = self.press
        delta = e.globalPosition().toPoint() - start
        if not self.dragging and abs(delta.x()) + abs(delta.y()) < 5:
            return
        if not self.dragging:
            self.dragging = True
            self.setCursor(Qt.ClosedHandCursor)
        self.move(origin + delta)
        self.update()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton or not self.press:
            return
        was_dragging = self.dragging
        self.press, self.dragging = None, False
        self.setCursor(Qt.PointingHandCursor)
        self.update()
        if was_dragging:
            # lâché à moitié hors de l'écran : on le ramène dedans
            margin = (BOOK_WIN - BOOK_SIZE) // 2
            x, y = keep_on_screen(self.x() + margin, self.y() + margin, BOOK_SIZE, BOOK_SIZE)
            self.move(x - margin, y - margin)
            self.app.book_moved(self.pos())
        else:
            self.open_book()

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        menu.setStyleSheet(
            'QMenu{background:#1d1913;color:#efe7d7;border:1px solid rgba(217,180,107,.35);border-radius:8px;padding:5px}'
            'QMenu::item{padding:6px 18px;border-radius:5px;font:10pt "Segoe UI"}'
            'QMenu::item:selected{background:rgba(217,180,107,.18);color:#f0d394}')
        menu.addAction('Ouvrir Grimoire Boss', self.open_book)
        menu.addSeparator()
        menu.addAction('Quitter', self.app.quit)
        menu.exec(e.globalPos())

    def open_book(self):
        if self.busy:
            return
        self.busy = True
        self.open_anim.start()

    def _opened(self):
        self.app.expand(self.pos())


# ---------- La fenêtre principale ----------
class Bridge(QObject):
    """Fonctions appelées par la page (bouton livre, barre du haut, bords)."""

    def __init__(self, app):
        super().__init__()
        self.app = app

    @Slot()
    def collapse(self):
        self.app.collapse()

    @Slot()
    def startMove(self):
        self.app.main.windowHandle().startSystemMove()

    @Slot(str)
    def startResize(self, edge):
        edges = {'r': Qt.RightEdge, 'l': Qt.LeftEdge, 'b': Qt.BottomEdge,
                 'br': Qt.RightEdge | Qt.BottomEdge, 'bl': Qt.LeftEdge | Qt.BottomEdge}.get(edge)
        if edges is not None:
            self.app.main.windowHandle().startSystemResize(edges)


class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.app = app
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(360, 420)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.profile = QWebEngineProfile('GrimoireBoss', self)  # stockage persistant : les stats saisies restent
        self.profile.setPersistentStoragePath(os.path.join(DATA_DIR, 'web'))
        self.profile.setCachePath(os.path.join(DATA_DIR, 'cache'))
        script = QWebEngineScript()
        script.setName('grimoire-boss')
        script.setSourceCode(qwebchannel_js() + '\n' + INJECT_JS)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(False)
        self.profile.scripts().insert(script)

        self.view = QWebEngineView(self)
        self.page = QWebEnginePage(self.profile, self.view)
        self.page.setBackgroundColor(Qt.transparent)
        self.view.setPage(self.page)
        self.channel = QWebChannel(self.page)
        self.bridge = Bridge(app)
        self.channel.registerObject('bridge', self.bridge)
        self.page.setWebChannel(self.channel)
        self.page.loadFinished.connect(self._loaded)
        layout.addWidget(self.view)
        self.view.load(QUrl(APP_URL))

    def _loaded(self, ok):
        if not ok and self.page.url().toString().startswith('https://'):
            self.page.setHtml(OFFLINE_PAGE, QUrl('about:blank'))

    def play_open(self):
        self.page.runJavaScript('window.gbPlayOpen && gbPlayOpen()')

    def moveEvent(self, e):
        self.app.main_geometry_changed()
        super().moveEvent(e)

    def resizeEvent(self, e):
        self.app.main_geometry_changed()
        super().resizeEvent(e)

    def closeEvent(self, e):
        self.app.quit()
        e.accept()


def qwebchannel_js():
    f = QFile(':/qtwebchannel/qwebchannel.js')
    if f.open(QIODevice.ReadOnly):
        return bytes(f.readAll()).decode('utf-8')
    return ''


class GrimoireApp:
    def __init__(self, qapp):
        self.qapp = qapp
        self.state = load_state()
        self.main = MainWindow(self)
        self.book = BookWidget(self)
        self.save_timer = QTimer(singleShot=True, interval=600)
        self.save_timer.timeout.connect(lambda: save_state(self.state))
        s = self.state
        self.main.resize(s['width'], s['height'])
        if 'x' in s:
            self.main.move(s['x'], s['y'])
        else:  # premier lancement : à droite de l'écran, là où il gêne le moins le jeu
            a = QGuiApplication.primaryScreen().availableGeometry()
            self.main.move(a.right() - s['width'] - 40, a.top() + max(20, (a.height() - s['height']) // 2))
        self.ready = True
        if s['collapsed']:
            self.book.appear(self.book_pos())
        else:
            self.main.show()

    def book_pos(self):
        s = self.state
        if 'book_x' in s:
            return QPoint(s['book_x'], s['book_y'])
        center = BTN_OFFSET + QPoint(20, 16)  # milieu du livre ouvert dans la fenêtre
        return self.main.pos() + center - QPoint(BOOK_WIN // 2, BOOK_WIN // 2)

    def main_geometry_changed(self):
        if not getattr(self, 'ready', False) or not self.main.isVisible():
            return
        g = self.main.geometry()
        self.state.update(x=g.x(), y=g.y(), width=g.width(), height=g.height())
        self.save_timer.start()

    def book_moved(self, pos):
        self.state['book_x'], self.state['book_y'] = pos.x(), pos.y()
        self.save_timer.start()

    def collapse(self):
        # le livre apparaît là où était le bouton : la fenêtre « se range » dans le livre
        self.state.pop('book_x', None)
        self.state.pop('book_y', None)
        pos = self.book_pos()
        self.main.hide()
        self.book.appear(pos)
        self.state['collapsed'] = True
        self.book_moved(self.book.pos())

    def expand(self, book_pos):
        # la fenêtre se rouvre depuis le livre, à l'endroit où on l'a posé
        center = BTN_OFFSET + QPoint(20, 16)
        target = book_pos + QPoint(BOOK_WIN // 2, BOOK_WIN // 2) - center
        x, y = keep_on_screen(target.x(), target.y(), self.main.width(), self.main.height())
        self.main.move(x, y)
        self.main.show()
        self.main.raise_()
        self.main.activateWindow()
        self.main.play_open()
        self.book.disappear()
        self.state['collapsed'] = False
        self.main_geometry_changed()

    def quit(self):
        save_state(self.state)
        self.qapp.quit()


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    qapp = QApplication(sys.argv)
    qapp.setApplicationName('GrimoireBoss')
    qapp.setQuitOnLastWindowClosed(False)
    icon = resource('icon.ico')
    if os.path.exists(icon):
        qapp.setWindowIcon(QIcon(icon))
    app = GrimoireApp(qapp)  # noqa: F841 (garde les fenêtres en vie)
    return qapp.exec()


if __name__ == '__main__':
    sys.exit(main())
