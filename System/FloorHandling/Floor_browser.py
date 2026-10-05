"""Data-driven floor/room browser.

Instead of hand-building a QWidget per room, this reads rooms.json
and generates: one QListWidget row per floor (the sidebar), one page per floor
in a QStackedWidget (the room grid), and one RoomCard per room. Add a room to
rooms.json and it appears here automatically -- nothing in this file changes.

Layout is two clearly separate zones, like a building directory in a lobby:
a gray "directory board" on the left (floors) and the rooms on the right,
with a thin divider between them so the split is obvious.

Run directly (`python floor_browser.py`) for a standalone preview.
"""
from PySide6.QtCore import Qt, Signal, QSize, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QStackedWidget, QListWidget, QListWidgetItem,
)
import ast

from System.FloorHandling.flow_layout import FlowLayout

SCHOOL_FLOORS = None
with open("System/FloorHandling/rooms.json", 'r') as e:
    SCHOOL_FLOORS = ast.literal_eval(e.read())


# ---------------------------------------------------------------------------
# Design tokens -- one place to tweak colours/fonts instead of hunting hex codes
# ---------------------------------------------------------------------------
GREEN_DARK = "#23411A"
GREEN_ACCENT = "#5E9B2F"
INK = "#1E2A3A"
MUTED = "#6B6B6B"
SIDEBAR_BG = "#EEF0F2"      # the light gray that marks the floor column
LINE = "#C9CCD1"            # gray used for every separator/border
FONT_STACK = "'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif"


# ---------------------------------------------------------------------------
# Icons -- tiny inline SVGs (Lucide-style line icons), no image files needed
# ---------------------------------------------------------------------------
_ICON_LAYERS = (
    '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
    '<polyline points="2 17 12 22 22 17"/>'
    '<polyline points="2 12 12 17 22 12"/>'
)
_ICON_BUILDING = (
    '<rect x="4" y="2" width="16" height="20" rx="2"/>'
    '<path d="M9 22v-4h6v4"/>'
    '<path d="M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>'
)


def _render_svg(body: str, color: str, size: int = 36) -> QPixmap:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{body}</svg>'
    )
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(svg.encode("utf-8"))).render(painter)
    painter.end()
    return pixmap


def make_icon(body: str, normal: str, selected: str | None = None) -> QIcon:
    """Build a QIcon that swaps colour when its list row is selected
    (dark green normally, white on the green highlight)."""
    icon = QIcon()
    icon.addPixmap(_render_svg(body, normal), QIcon.Mode.Normal)
    if selected:
        icon.addPixmap(_render_svg(body, selected), QIcon.Mode.Selected)
    return icon


def icon_label(body: str, color: str, size: int = 18) -> QLabel:
    lbl = QLabel()
    lbl.setPixmap(_render_svg(body, color, size * 2).scaled(
        size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    lbl.setFixedSize(size, size)
    return lbl


class RoomCard(QFrame):
    """One clickable card for a single room. Emits its own info dict on click,
    so the handler doesn't need per-card state or lambda-closure tricks."""
    clicked = Signal(dict)

    def __init__(self, floor: str, building: str, room: str, parent=None):
        super().__init__(parent)
        self._info = {"floor": floor, "building": building, "room": room}
        self.setObjectName("roomCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        name = QLabel(room)
        name.setObjectName("roomCardName")
        name.setWordWrap(True)

        sub = QLabel(building)
        sub.setObjectName("roomCardBuilding")

        layout.addWidget(name)
        layout.addWidget(sub)

        self.setStyleSheet(f"""
            QFrame#roomCard {{
                background: white;
                border: 1px solid {LINE};
                border-radius: 10px;
            }}
            QFrame#roomCard:hover {{ border: 1px solid {GREEN_ACCENT}; }}
            QLabel#roomCardName {{
                font-family: {FONT_STACK};
                font-size: 14px; font-weight: 700; color: {INK};
                background: transparent; border: none;
            }}
            QLabel#roomCardBuilding {{
                font-family: {FONT_STACK};
                font-size: 12px; font-weight: 500; color: {MUTED};
                background: transparent; border: none;
            }}
        """)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit(self._info)
        super().mouseReleaseEvent(event)


class FloorPage(QScrollArea):
    """One QStackedWidget page: every building on this floor, each building's
    rooms wrapped in a FlowLayout so the grid reflows instead of scrolling sideways."""
    room_clicked = Signal(dict)

    def __init__(self, floor: str, buildings: dict, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("QScrollArea { background: white; border: none; }")

        content = QWidget()
        content.setStyleSheet("background: white;")
        outer = QVBoxLayout(content)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(20)

        for building, rooms in buildings.items():
            # Section header: building icon + name, like a sign above a wing.
            header = QWidget()
            header_row = QHBoxLayout(header)
            header_row.setContentsMargins(0, 0, 0, 0)
            header_row.setSpacing(8)

            section = QLabel(building)
            section.setStyleSheet(
                f"font-family: {FONT_STACK}; font-size: 16px; font-weight: 700; "
                f"color: {GREEN_DARK}; background: transparent;"
            )
            header_row.addWidget(icon_label(_ICON_BUILDING, GREEN_DARK))
            header_row.addWidget(section)
            header_row.addStretch(1)
            outer.addWidget(header)

            grid_host = QWidget()
            flow = FlowLayout(grid_host, margin=0, h_spacing=10, v_spacing=10)
            for room in rooms:
                card = RoomCard(floor, building, room)
                card.clicked.connect(self.room_clicked.emit)
                flow.addWidget(card)
            outer.addWidget(grid_host)

        outer.addStretch(1)
        self.setWidget(content)


class FloorBrowser(QWidget):
    """Gray floor column | divider | room grid.

    This is the piece you drop into CommonContainer.RightColumn() (or wherever
    you want the room grid to live) instead of hand-adding every room widget.
    """
    room_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- Left: the floor column (its own gray panel) -------------------
        self.sidebar = QFrame()
        self.sidebar.setObjectName("floorSidebar")
        self.sidebar.setFixedWidth(170)
        self.sidebar.setStyleSheet(f"""
            QFrame#floorSidebar {{ background-color: {SIDEBAR_BG}; border: none; }}
        """)

        self.floor_list_layout = QVBoxLayout(self.sidebar)
        self.floor_list_layout.setContentsMargins(0, 0, 0, 0)
        self.floor_list_layout.setSpacing(0)

        # Header (kept as self.RoomText so existing references still work)
        self.RoomText = QLabel("  FLOORS")
        self.RoomText.setFixedHeight(44)
        self.RoomText.setStyleSheet(f"""
            font-family: {FONT_STACK}; font-size: 12px; font-weight: 700;
            color: {MUTED}; background: transparent;
            border-bottom: 1px solid {LINE}; padding-left: 12px;
        """)

        self.floor_list = QListWidget()
        self.floor_list.setSpacing(0)                      # no gap between floors
        self.floor_list.setIconSize(QSize(18, 18))
        self.floor_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.floor_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.floor_list.setStyleSheet(f"""
            QListWidget {{
                border: none; background: transparent; outline: none;
                font-family: {FONT_STACK}; font-size: 14px; font-weight: 600;
                color: {INK};
            }}
            QListWidget::item {{
                padding: 12px 14px;
                border-radius: 0px;                        /* flat edges */
                border: none;
                border-bottom: 1px solid {LINE};           /* gray line between floors */
            }}
            QListWidget::item:hover {{ background-color: #E2E5E8; }}
            QListWidget::item:selected {{
                background-color: {GREEN_DARK}; color: white;
            }}
        """)

        self.stack = QStackedWidget()
        floor_icon = make_icon(_ICON_LAYERS, GREEN_DARK, "#FFFFFF")
        for floor, buildings in SCHOOL_FLOORS.items():
            listItem = QListWidgetItem(floor_icon, floor)
            listItem.setToolTip(f"<p>Change to {floor}</p>")
            self.floor_list.addItem(listItem)
            page = FloorPage(floor, buildings)
            page.room_clicked.connect(self.room_selected.emit)
            self.stack.addWidget(page)

        self.floor_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.floor_list.setCurrentRow(0)

        self.floor_list_layout.addWidget(self.RoomText)
        self.floor_list_layout.addWidget(self.floor_list, stretch=1)

        # ---- Middle: the divider widget -----------------------------------
        self.divider = QFrame()
        self.divider.setObjectName("floorDivider")
        self.divider.setFixedWidth(1)
        self.divider.setStyleSheet(f"QFrame#floorDivider {{ background-color: {LINE}; border: none; }}")

        # ---- Right: the room grid -----------------------------------------
        layout.addWidget(self.sidebar)
        layout.addWidget(self.divider)
        layout.addWidget(self.stack, stretch=1)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    browser = FloorBrowser()
    browser.room_selected.connect(lambda info: print("Selected:", info))
    browser.resize(900, 600)
    browser.show()
    sys.exit(app.exec())