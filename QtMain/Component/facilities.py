
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

DEFAULT_DATA_PATH = "QtMain/Component/dependencies/rooms.json"

# ── Palette ────────────────────────────────────────────────────────────────
MINT = "#6ee7b7"        # accents, focus ring, wing labels
TEXT = "#e8f5ee"        # primary text
TEXT_MUTED = "#9fc4b2"  # secondary text (still > 4.5:1 on the dark green)

STYLESHEET = """
/* Glass panels: faint white fill + mint-tinted hairline border */
#SearchPanel, #FacilitiesPanel {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(110, 231, 183, 0.20);
    border-radius: 20px;
}
QLabel { background-color: transparent}
#FacilitiesPanel { background: rgba(255, 255, 255, 0.03); }

/* Search panel */
#PanelTitle  { color: %(text)s; font-size: 22px; font-weight: 700; }
#PanelHint, #ResultCount { color: %(muted)s; font-size: 13px; }
#SearchInput {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(110, 231, 183, 0.25);
    border-radius: 12px;
    padding: 10px 8px;
    color: %(text)s;
    font-size: 14px;
    selection-background-color: rgba(52, 211, 153, 0.45);
}
#SearchInput:focus {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid %(mint)s;
}

/* Floors and wings */
#FloorTitle { color: %(text)s; font-size: 24px; font-weight: 700; }
#FloorRule {
    border: none;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(110, 231, 183, 0.55), stop:1 rgba(110, 231, 183, 0));
}
#WingTitle { color: %(mint)s; font-size: 12px; font-weight: 700; }
#WingCount { color: %(muted)s; font-size: 12px; }

/* Room cards */
#RoomCard {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(110, 231, 183, 0.20);
    border-radius: 16px;
}
#RoomCard:hover {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(110, 231, 183, 0.55);
}
#RoomName        { color: %(text)s;  font-size: 15px; font-weight: 600; }
#RoomDescription { color: %(muted)s; font-size: 13px; }
#EmptyState      { color: %(muted)s; font-size: 15px; padding: 60px 0; }

/* Let the gradient show through the scroll area */
#FacilityScroll, #FacilityScroll > QWidget > QWidget, #FacilityContent {
    background: transparent;
    border: none;
}
QScrollBar:vertical { background: transparent; width: 10px; margin: 6px 2px; }
QScrollBar::handle:vertical {
    background: rgba(110, 231, 183, 0.28); border-radius: 3px; min-height: 36px;
}
QScrollBar::handle:vertical:hover { background: rgba(110, 231, 183, 0.50); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
""" % {"text": TEXT, "muted": TEXT_MUTED, "mint": MINT}


def _icon(kind: str, color: str = MINT, size: int = 18) -> QIcon:
    """Draw a small vector-style icon ('search' or 'close') so no image files are needed."""
    s = size * 2  # draw at 2x so it stays crisp on high-DPI screens
    pixmap = QPixmap(s, s)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(color), 3.2, Qt.SolidLine, Qt.RoundCap))
    if kind == "search":
        p.drawEllipse(QRectF(s * 0.14, s * 0.14, s * 0.50, s * 0.50))
        p.drawLine(QPointF(s * 0.58, s * 0.58), QPointF(s * 0.84, s * 0.84))
    else:
        p.drawLine(QPointF(s * 0.26, s * 0.26), QPointF(s * 0.74, s * 0.74))
        p.drawLine(QPointF(s * 0.74, s * 0.26), QPointF(s * 0.26, s * 0.74))
    p.end()
    return QIcon(pixmap)


def _normalize(data: dict) -> dict:
    """Turn list-style wings into {room: {}} so every wing is {room: details}."""
    return {
        floor: {
            wing: ({r: {} for r in rooms} if isinstance(rooms, list) else rooms)
            for wing, rooms in wings.items()
        }
        for floor, wings in data.items()
    }


class CircleImage(QWidget):
    """Like a porthole on a ship, this widget shows only a round window onto the
    picture. It crops the image to fill the circle, and when no photo exists it
    paints initials on a green gradient, so cards never look empty."""

    def __init__(self, name: str, image_path: Path | None, size: int = 60, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._label = self._initials(name)
        self._source = (
            QPixmap(str(image_path)) if image_path and image_path.is_file() else QPixmap()
        )
        self._cache: tuple[float, QPixmap] | None = None

    @staticmethod
    def _initials(name: str) -> str:
        words = name.split()
        if name.startswith("Classroom") and len(words) > 1:
            return words[-1]  # "Classroom SH 841" -> "841"
        if words[0].isupper() and words[0].isalpha() and len(words[0]) <= 5:
            return words[0]  # acronyms read better whole: "CSDL", "COED", "HR"
        return "".join(w[0] for w in words[:2]).upper()

    def _scaled(self, side: float, dpr: float) -> QPixmap:
        if self._cache is None or self._cache[0] != dpr:
            px = int(side * dpr)
            scaled = self._source.scaled(
                px, px, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            scaled.setDevicePixelRatio(dpr)
            self._cache = (dpr, scaled)
        return self._cache[1]

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)

        clip = QPainterPath()
        clip.addEllipse(rect)
        p.setClipPath(clip)

        if self._source.isNull():
            fill = QLinearGradient(rect.topLeft(), rect.bottomRight())
            fill.setColorAt(0.0, QColor("#1f7a5a"))
            fill.setColorAt(1.0, QColor("#0b3d2c"))
            p.fillRect(rect, QBrush(fill))
            font = QFont(self.font())
            font.setPixelSize({1: 18, 2: 17, 3: 15}.get(len(self._label), 13))
            font.setWeight(QFont.DemiBold)
            p.setFont(font)
            p.setPen(QColor(TEXT))
            p.drawText(rect, Qt.AlignCenter, self._label)
        else:
            dpr = self.devicePixelRatioF()
            pm = self._scaled(rect.width(), dpr)
            w, h = pm.width() / dpr, pm.height() / dpr
            p.drawPixmap(QPointF(rect.center().x() - w / 2, rect.center().y() - h / 2), pm)

        p.setClipping(False)
        p.setPen(QPen(QColor(110, 231, 183, 150), 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(rect)


class RoomCard(QFrame):
    """A room card is a hotel door plaque: a round photo, the room's name, and a
    short line saying what happens inside. It keeps a lowercase search string
    handy, so checking whether it matches is a single quick comparison."""

    MIN_WIDTH = 300  # preferred width per column; only used to decide the column count

    def __init__(self, floor: str, wing: str, name: str, details: dict, image_root: Path, parent=None):
        super().__init__(parent)
        self.setObjectName("RoomCard")

        description = details.get("description", "")
        self.search_text = f"{floor} {wing} {name} {description}".lower()

        image = details.get("image")
        image_path = None
        if image:
            image_path = Path(image)
            if not image_path.is_absolute():
                image_path = image_root / image_path

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 14, 16, 14)
        row.setSpacing(14)
        row.addWidget(CircleImage(name, image_path), 0, Qt.AlignTop)

        text = QVBoxLayout()
        text.setSpacing(4)
        title = QLabel(name)
        title.setObjectName("RoomName")
        title.setWordWrap(True)
        text.addWidget(title)
        if description:
            body = QLabel(description)
            body.setObjectName("RoomDescription")
            body.setWordWrap(True)
            text.addWidget(body)
        text.addStretch(1)
        row.addLayout(text, 1)

    def matches(self, tokens: list[str]) -> bool:
        return all(t in self.search_text for t in tokens)


class WingSection(QWidget):
    """A wing is one shelf of the drawer, holding room cards side by side. It
    re-deals its cards into as many columns as the width allows, like seating
    guests at a table that grows or shrinks, and hides cards that miss the search."""

    GAP = 12

    def __init__(self, floor: str, wing: str, rooms: dict, image_root: Path, parent=None):
        super().__init__(parent)
        self.cards = [
            RoomCard(floor, wing, name, details, image_root, self)
            for name, details in rooms.items()
        ]
        self._visible: list[RoomCard] = []
        self._columns = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        header = QHBoxLayout()
        self._title = QLabel(wing.upper())
        self._title.setObjectName("WingTitle")
        spaced = self._title.font()
        spaced.setLetterSpacing(QFont.AbsoluteSpacing, 1.4)  # QSS can't do letter-spacing
        self._title.setFont(spaced)
        self._count = QLabel()
        self._count.setObjectName("WingCount")
        header.addWidget(self._title)
        header.addStretch(1)
        header.addWidget(self._count)
        root.addLayout(header)

        self._grid = QGridLayout()
        self._grid.setSpacing(self.GAP)
        root.addLayout(self._grid)

        self.apply_filter([])

    def apply_filter(self, tokens: list[str]) -> int:
        self._visible = []
        for card in self.cards:
            show = card.matches(tokens)
            card.setVisible(show)
            if show:
                self._visible.append(card)
        n = len(self._visible)
        self._count.setText(f"{n} {'place' if n == 1 else 'places'}")
        self.setVisible(n > 0)
        self._reflow(force=True)
        return n

    def _reflow(self, force: bool = False) -> None:
        cols = max(1, (self.width() + self.GAP) // (RoomCard.MIN_WIDTH + self.GAP))
        if not force and cols == self._columns:
            return
        self._columns = cols
        while self._grid.count():
            self._grid.takeAt(0)  # detach from the grid; the widgets stay alive
        for c in range(self._grid.columnCount()):
            self._grid.setColumnStretch(c, 0)
        for i, card in enumerate(self._visible):
            self._grid.addWidget(card, i // cols, i % cols)
        for c in range(cols):
            self._grid.setColumnStretch(c, 1)
        self._grid.invalidate()  # make parents re-ask "how tall at this width?"
        self.updateGeometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reflow()


class FloorSection(QWidget):
    """Each floor is a labelled drawer in a filing cabinet. The header names the
    drawer, and inside it sit the wing folders. When a search empties every
    folder, the whole drawer hides itself, so you never open one and find nothing."""

    def __init__(self, floor: str, wings: dict, image_root: Path, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(16)
        title = QLabel(floor)
        title.setObjectName("FloorTitle")
        rule = QFrame()
        rule.setObjectName("FloorRule")
        rule.setFixedHeight(1)
        header.addWidget(title)
        header.addWidget(rule, 1, Qt.AlignVCenter)
        root.addLayout(header)

        self.wings = [
            WingSection(floor, wing, rooms, image_root, self) for wing, rooms in wings.items()
        ]
        for section in self.wings:
            root.addWidget(section)

    def apply_filter(self, tokens: list[str]) -> int:
        total = sum([w.apply_filter(tokens) for w in self.wings])
        self.setVisible(total > 0)
        return total


class SearchPanel(QWidget):
    """Like the front-desk clerk who points you toward a room, this panel only
    collects your question. It holds the title, the search box and the result
    count, then announces each keystroke through a signal, so it never needs to
    know how the rooms are displayed."""

    queryChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SearchPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(270)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(10)

        title = QLabel("Campus Directory")
        title.setObjectName("PanelTitle")
        title.setWordWrap(True)
        hint = QLabel("Find a classroom, office or facility.")
        hint.setObjectName("PanelHint")
        hint.setWordWrap(True)

        self.input = QLineEdit()
        self.input.setObjectName("SearchInput")
        self.input.setPlaceholderText("Search rooms or offices…")
        self.input.setAccessibleName("Search facilities")
        self.input.addAction(_icon("search"), QLineEdit.LeadingPosition)
        self._clear_action = self.input.addAction(_icon("close"), QLineEdit.TrailingPosition)
        self._clear_action.setToolTip("Clear search")
        self._clear_action.setVisible(False)
        self._clear_action.triggered.connect(self.input.clear)
        self.input.textChanged.connect(self._on_text_changed)

        self.count = QLabel()
        self.count.setObjectName("ResultCount")

        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addSpacing(10)
        layout.addWidget(self.input)
        layout.addWidget(self.count)
        layout.addStretch(1)

    def _on_text_changed(self, text: str) -> None:
        self._clear_action.setVisible(bool(text))
        self.queryChanged.emit(text)

    def set_result_count(self, shown: int, total: int) -> None:
        self.count.setText(
            f"{total} places" if shown == total else f"{shown} of {total} places"
        )


class FacilitiesPanel(QWidget):
    """Picture a building's floor-by-floor signboard in the elevator. This panel
    stacks one section per floor inside a scroll area, so a long list stays
    reachable, and it shows a friendly empty message when a search matches
    nothing at all."""

    def __init__(self, data: dict, image_root: Path, parent=None):
        super().__init__(parent)
        self.setObjectName("FacilitiesPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)

        self._scroll = QScrollArea()
        self._scroll.setObjectName("FacilityScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.viewport().setAutoFillBackground(False)

        content = QWidget()
        content.setObjectName("FacilityContent")
        column = QVBoxLayout(content)
        column.setContentsMargins(22, 22, 22, 22)
        column.setSpacing(34)

        self.floors = [
            FloorSection(floor, wings, image_root, content) for floor, wings in data.items()
        ]
        for section in self.floors:
            column.addWidget(section)

        self._empty = QLabel()
        self._empty.setObjectName("EmptyState")
        self._empty.setAlignment(Qt.AlignCenter)
        self._empty.setWordWrap(True)
        self._empty.hide()
        column.addWidget(self._empty)
        column.addStretch(1)

        self._scroll.setWidget(content)
        outer.addWidget(self._scroll)

    def apply_filter(self, tokens: list[str], raw_query: str) -> int:
        total = sum([f.apply_filter(tokens) for f in self.floors])
        self._empty.setVisible(total == 0)
        if total == 0:
            self._empty.setText(
                f"No places match “{raw_query}”.\nTry a room number, office name or floor."
            )
        self._scroll.verticalScrollBar().setValue(0)
        return total


class Facilities(QWidget):
    """Think of a mall's lobby directory board: a slim search kiosk beside a big
    map of every shop. This widget splits itself the same way, 1:9. It wires the
    search box to the room cards, so typing narrows the list live, and it paints
    the dark-green backdrop."""

    def __init__(self, data: dict | str | Path | None = None,
                 image_root: str | Path | None = None, parent=None):
        super().__init__(parent)

        source_dir = Path.cwd()
        if data is None:
            data = DEFAULT_DATA_PATH
        if isinstance(data, (str, Path)):
            path = Path(data)
            source_dir = path.parent
            data = json.loads(path.read_text(encoding="utf-8"))
        data = _normalize(data)
        image_root = Path(image_root) if image_root else source_dir

        self._total = sum(len(rooms) for wings in data.values() for rooms in wings.values())
        self.setStyleSheet(STYLESHEET)
        self.setMinimumSize(680, 420)

        layout = QVBoxLayout(self)  # swap for QVBoxLayout to stack the panels instead
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)
        self.search_panel = SearchPanel(self)
        self.facilities_panel = FacilitiesPanel(data, image_root, self)
        layout.addWidget(self.search_panel, 1)
        layout.addWidget(self.facilities_panel, 9)

        self.search_panel.queryChanged.connect(self._on_query)
        self._on_query("")

    def sizeHint(self) -> QSize:
        return QSize(1180, 760)

    def _on_query(self, query: str) -> None:
        # Every word must appear somewhere in "floor wing room description".
        shown = self.facilities_panel.apply_filter(query.lower().split(), query.strip())
        self.search_panel.set_result_count(shown, self._total)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        base = QLinearGradient(0, 0, w, h)
        base.setColorAt(0.0, QColor("#04110c"))
        base.setColorAt(0.55, QColor("#08241a"))
        base.setColorAt(1.0, QColor("#0d3b2b"))
        p.fillRect(self.rect(), QBrush(base))

        # Soft emerald glows give the glass panels something to "frost".
        for cx, cy, scale, (r, g, b, a) in (
            (0.85, 0.05, 0.55, (52, 211, 153, 70)),
            (0.05, 0.95, 0.50, (16, 185, 129, 55)),
        ):
            glow = QRadialGradient(QPointF(w * cx, h * cy), max(w, h) * scale)
            glow.setColorAt(0.0, QColor(r, g, b, a))
            glow.setColorAt(1.0, QColor(r, g, b, 0))
            p.fillRect(self.rect(), QBrush(glow))