import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon


# =========================================================
# COLUMN 1
# =========================================================

class Column1(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Column1")

        # -------------------------
        # Styling
        # -------------------------

        self.setStyleSheet("""
            QWidget#Column1 {
                background-color: white;
            }

            QLabel {
                color: black;
                background-color: transparent;
            }

            QPushButton#OpenMenu {
                background-color: transparent;
                border: none;
            }

            QPushButton#OpenMenu:hover {
                background-color: lightgray;
            }
        """)

        # -------------------------
        # Layout
        # -------------------------

        self.Column1Container = QVBoxLayout(self)

        self.Column1Container.setContentsMargins(
            10, 10, 10, 10
        )

        label = QLabel("Hello")

        self.Column1Container.addWidget(label)

        # -------------------------
        # Menu button
        # -------------------------

        self.OpenMenu = QPushButton(self)

        self.OpenMenu.setObjectName("OpenMenu")

        self.OpenMenu.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        # If you have the image:
        self.OpenMenu.setIcon(
            QIcon("resources/menu-button.png")
        )

        # Make sure it is above layout widgets
        self.OpenMenu.raise_()

    # =====================================================
    # RESPONSIVE RESIZE
    # =====================================================

    def resizeEvent(self, event):

        # 10% of Column1's width
        size = int(self.width() * 0.10)

        # Optional minimum / maximum
        size = max(40, min(size, 80))

        # Absolute position + responsive size
        self.OpenMenu.setGeometry(
            0,      # X
            0,      # Y
            size,   # Width
            size    # Height
        )

        # Make icon scale with button
        self.OpenMenu.setIconSize(
            QSize(size, size)
        )

        # Keep button above other children
        self.OpenMenu.raise_()

        super().resizeEvent(event)


# =========================================================
# COLUMN 2
# =========================================================

class Column2(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Column2")

        self.setStyleSheet("""
            QWidget#Column2 {
                background-color: #dddddd;
            }

            QLabel {
                color: black;
                background-color: transparent;
            }
        """)

        self.Column2Layout = QVBoxLayout(self)

        self.Column2Layout.setContentsMargins(
            10, 10, 10, 10
        )

        label = QLabel("Column 2")

        self.Column2Layout.addWidget(label)


# =========================================================
# MAIN CONTAINER
# =========================================================

class Container(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Container")

        self.setStyleSheet("""
            QWidget#Container {
                background-color: rgb(25, 25, 25);
            }
        """)

        # -------------------------
        # Main horizontal layout
        # -------------------------

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            10, 10, 10, 1
        )

        # Column 1 gets 3 parts
        layout.addWidget(
            Column1(),
            stretch=3
        )

        # Column 2 gets 1 part
        layout.addWidget(
            Column2(),
            stretch=1
        )


# =========================================================
# APPLICATION
# =========================================================

app = QApplication(sys.argv)

window = Container()

window.resize(1000, 600)

window.show()

sys.exit(app.exec())