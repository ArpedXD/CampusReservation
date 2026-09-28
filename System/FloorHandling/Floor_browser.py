"""Data-driven floor/room browser.

Instead of hand-building a QWidget per room, this reads rooms_data.SCHOOL_FLOORS
and generates: one QListWidget row per floor (the sidebar), one page per floor
in a QStackedWidget (the room grid), and one RoomCard per room. Add a room to
rooms_data.py and it appears here automatically -- nothing in this file changes.

Run directly (`python floor_browser.py`) for a standalone preview.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QStackedWidget, QListWidget, QListWidgetItem,
)
import ast

from System.FloorHandling.flow_layout import FlowLayout

SCHOOL_FLOORS = None
with open("System/FloorHandling/rooms.json", 'r') as e:
    SCHOOL_FLOORS = ast.literal_eval(e.read())


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

        self.setStyleSheet("""
            QFrame#roomCard {
                border: 1px solid #dcdcdc;
                border-radius: 10px;
            }
            QFrame#roomCard:hover { border: 1px solid #5E9B2F; }
            QLabel#roomCardName { font-size: 13px; font-weight: 700; color: #1E2A3A; }
            QLabel#roomCardBuilding { font-size: 11px; font-weight: 600; color: #6b6b6b; }
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

        content = QWidget()
        outer = QVBoxLayout(content)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(18)

        for building, rooms in buildings.items():
            section = QLabel(building)
            section.setStyleSheet("font-size: 15px; font-weight: 800; color: #14210C;")
            outer.addWidget(section)

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
    """Sidebar list of floors + a QStackedWidget of FloorPages.

    This is the piece you drop into CommonContainer.RightColumn() (or wherever
    you want the room grid to live) instead of hand-adding every room widget.
    """
    room_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.floor_list_layout = QVBoxLayout()
        self.floor_list = QListWidget()
        self.floor_list.setSpacing(5)
        self.floor_list.setFixedWidth(150)
        self.floor_list.setStyleSheet("""
            QListWidget { border: none; background: transparent; font-size: 13px; }
            QListWidget::item { padding: 10px 12px; border-radius: 6px; border: 1px solid 23411A;}
            QListWidget::item:selected { background-color: #23411A; color: white; }
        """)
        self.floor_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.stack = QStackedWidget()
        self.RoomText = QLabel()
        self.RoomText.setText("Rooms")
        for floor, buildings in SCHOOL_FLOORS.items():
            listItem = QListWidgetItem(floor)
            listItem.setToolTip(
                f"""
                    <p> Change to {floor}</p>
                """
            )
            self.floor_list.addItem(listItem)
            page = FloorPage(floor, buildings)
            page.room_clicked.connect(self.room_selected.emit)
            self.stack.addWidget(page)

        self.floor_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.floor_list.setCurrentRow(0)

        layout.addLayout(self.floor_list_layout)
        self.floor_list_layout.addWidget(self.RoomText)
        self.floor_list_layout.addWidget(self.floor_list)

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