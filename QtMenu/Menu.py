from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QButtonGroup, QSizePolicy
from PySide6.QtCore import Qt, QSize, QByteArray, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer


# 24x24 stroke icons (Feather/Lucide style). Only the inner shapes are stored;
# the colour is injected at render time so one drawing serves every state.
ICON_SHAPES = {
    "home": (
        '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<polyline points="9 22 9 12 15 12 15 22"/>'
    ),
    # calendar with a plus: "make a new booking"
    "calendar_plus": (
        '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
        '<line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>'
        '<line x1="3" y1="10" x2="21" y2="10"/>'
        '<line x1="12" y1="14" x2="12" y2="18"/><line x1="10" y1="16" x2="14" y2="16"/>'
    ),
    # calendar with a tick: "bookings I already have"
    "calendar_check": (
        '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
        '<line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>'
        '<line x1="3" y1="10" x2="21" y2="10"/>'
        '<polyline points="9.5 16 11.5 18 15 14"/>'
    ),
    "building": (
        '<rect x="4" y="2" width="16" height="20" rx="2"/>'
        '<path d="M9 22v-4h6v4"/>'
        '<path d="M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>'
    ),
    "feedback": (
        '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'
    ),
    # "sliders": three control sliders, a clean stand-in for settings
    "settings": (
        '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/>'
        '<line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/>'
        '<line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/>'
        '<line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/>'
        '<line x1="17" y1="16" x2="23" y2="16"/>'
    ),
    # door with an arrow leaving: "log out"
    "logout": (
        '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
        '<polyline points="16 17 21 12 16 7"/>'
        '<line x1="21" y1="12" x2="9" y2="12"/>'
    ),
}

GREEN = "#166534"   # icon colour at rest, and the selected pill background
WHITE = "#ffffff"   # icon colour on the selected pill
RED = "#b91c1c"     # logout icon


def make_icon(shape_key, rest_color, active_color=WHITE, size=20, gap=8):
    """Build a QIcon that swaps colour when its button is checked.

    Analogy: a reversible jacket. Same shape, but flip it (checked) and the
    inside colour shows. A transparent strip is added on the right so the
    label sits a comfortable distance from the icon without hacking the text.
    """
    def render(color):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'{ICON_SHAPES[shape_key]}</svg>'
        )
        renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
        ratio = 2  # draw at 2x so the icon stays crisp on HiDPI screens
        pm = QPixmap((size + gap) * ratio, size * ratio)
        pm.setDevicePixelRatio(ratio)
        pm.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm)
        renderer.render(painter, QRectF(0, 0, size, size))
        painter.end()
        return pm

    rest, active = render(rest_color), render(active_color)
    icon = QIcon()
    icon.addPixmap(rest, QIcon.Mode.Normal, QIcon.State.Off)
    icon.addPixmap(rest, QIcon.Mode.Active, QIcon.State.Off)
    icon.addPixmap(active, QIcon.Mode.Normal, QIcon.State.On)
    icon.addPixmap(active, QIcon.Mode.Active, QIcon.State.On)
    return icon


class Menu:
    # Analogy: a hotel lift panel. Floors you can stay on light up while you
    # are there; the hover tint is your finger hovering, pressed is the click.
    # Logout is the emergency exit: red, close by, never "the current floor".
    BUTTON_QSS = """
        /* The panel itself is clear glass: the sidebar's white shows through,
           so no grey box appears behind the buttons. */
        QWidget#menuContainer {
            background-color: transparent;
            border: none;
        }

        QPushButton {
            background-color: transparent;
            color: white;
            border: 2px solid transparent;
            border-radius: 10px;
            padding: 0px 14px;
            text-align: left;
            font-size: 14px;
            font-weight: 500;
        }
        QPushButton:hover:!checked {
            background-color: #f0fdf4;
            color: #14532d;
        }
        QPushButton:pressed {
            background-color: #dcfce7;
        }
        QPushButton:checked {
            background-color: #166534;
            color: #ffffff;
        }
        QPushButton:checked:hover {
            background-color: #166534;
        }

        QPushButton#logoutBtn {
            color: #b91c1c;
        }
        QPushButton#logoutBtn:hover {
            background-color: #fef2f2;
        }
        QPushButton#logoutBtn:pressed {
            background-color: #fee2e2;
        }
    """

    def __init__(self):
        self.container = QWidget()
        self.container.setObjectName("menuContainer")
        self.container.setAutoFillBackground(False)

        self.button1 = QPushButton("Home")
        self.button2 = QPushButton("Reserve Facility")
        self.button3 = QPushButton("My Reservation")
        self.button4 = QPushButton("Facilities")
        self.button5 = QPushButton("Suggestion/Feedback/Help")
        self.button6 = QPushButton("Logout")

        self.buttonList = [self.button1, self.button2, self.button3, self.button4, self.button5, self.button6]
        # Page-like buttons that hold the green highlight. Logout is an action,
        # so it stays out of the group.
        self.selectableButtons = self.buttonList

        # Analogy: car radio presets. Pressing one pops the previous one out.
        self.group = QButtonGroup(self.container)
        self.group.setExclusive(True)

        self._icons = {
            self.button1: make_icon("home", GREEN),
            self.button2: make_icon("calendar_plus", GREEN),
            self.button3: make_icon("calendar_check", GREEN),
            self.button4: make_icon("building", GREEN),
            self.button5: make_icon("feedback", GREEN),
            self.button6: make_icon("settings", GREEN),
        }
        self.button1.setCheckable(True)
        self.button1.setChecked(True)
        
    def containers(self):
        buttonContainer = self.container
        buttonContainer.setStyleSheet(self.BUTTON_QSS)

        buttonLayout = QVBoxLayout(buttonContainer)
        buttonLayout.setSpacing(4)
        buttonLayout.setContentsMargins(0, 0, 0, 0)

        for each in self.buttonList:
            each.setIcon(self._icons[each])
            each.setIconSize(QSize(28, 20))
            each.setFixedHeight(44)  # 44px = comfortable click/touch target
            each.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            each.setCursor(Qt.CursorShape.PointingHandCursor)
            # Buttons never grab focus on their own. Qt hands the first
            # focusable widget a focus ring when the window opens, which was
            # the stray green outline on Settings.
            each.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            if each in self.selectableButtons:
                each.setCheckable(True)
                self.group.addButton(each)

            buttonLayout.addWidget(each)

        return buttonContainer