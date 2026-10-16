from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGraphicsDropShadowEffect, QScrollArea, QStackedWidget, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QColor

from QtMenu.Menu import Menu
from System.AccountHandling.Account import AccountHandler
from System.FloorHandling.Floor_browser import FloorBrowser
from QtMain.Component.Reservation import Reservation
from QtMain.Component.home import Home
from QtMain.Component.profile import Profile
from QtMain.Component.facilities import Facilities
from QtMain.Component.Feedback import Feedback


gradient = """qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 #04110c, stop:0.55 #08241a, stop:1 #0d3b2b)"""


class CommonContainer(QWidget):
    NavigateToMenu = Signal(str)

    def __init__(self):
        super().__init__()
        self.form = None
        self.container = QWidget()
        self.container.setStyleSheet("""
            background:qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #04110c, stop:0.55 #08241a, stop:1 #0d3b2b);
        """)
        self.Column1 = QWidget()
        self.Column2 = QWidget()
        self.Column3 = QWidget()
        self.Column3.hide()
        self.NavigateToMenu.connect(self.menunavigation)
        self.Handler = AccountHandler()

        self._unverified_child = None
        self._resize_handler_installed = False

        self.unverified = QWidget(self.container)
        self.unverifiedWidget()

        self.reservation = Reservation(self.container)

        self.profile = Profile()
        self.facilities = Facilities()
        self.feedback = Feedback()

        self._install_container_resize_handler()


    def firstColumn(self):
        Column1 = self.Column1
        Column1.setObjectName("sideMenu")
        Column1.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        Column1.setMinimumWidth(200)
    
        mainLayout = QVBoxLayout(Column1)
        mainLayout.setContentsMargins(12, 16, 12, 16)
        mainLayout.setSpacing(0)
    
        menu = Menu() #---- Menu Part
        menu.button1.clicked.connect(lambda: self.NavigateToMenu.emit("Home"))
        menu.button2.clicked.connect(lambda: self.NavigateToMenu.emit("Reserve"))
        menu.button3.clicked.connect(lambda: self.NavigateToMenu.emit("Profile")) # connects button to navigation (note to self: Connect the other buttons through this way aswell)
        menu.button4.clicked.connect(lambda: self.NavigateToMenu.emit("Facilities")) # facilities
        menu.button5.clicked.connect(lambda: self.NavigateToMenu.emit("Feedback")) # suggestion / feedback 
        menu.button6.clicked.connect(lambda: self.Handler.handleLogout()) # Settings

        containers = menu.containers()
    
        mainLayout.addWidget(containers)  # no left-alignment: buttons fill the sidebar width
        mainLayout.addStretch()
    
        # The "#sideMenu" selector keeps this style on the column only,
        # so it no longer leaks into every child widget.
        Column1.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #04110c, stop:0.55 #08241a, stop:1 #0d3b2b);
        """)
        # child widget
        return Column1

    def secondColumn(self):
        Column2 = self.Column2
        Column2.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #04110c, stop:0.55 #08241a, stop:1 #0d3b2b);
        """)
        ColumnLayout = QVBoxLayout(Column2)
        ColumnLayout.setContentsMargins(0,0,0,0)
        ColumnLayout.setSpacing(0)

        self.floor_browser = FloorBrowser()
        self.floor_browser.room_selected.connect(self.reservation.open_reservation_form)

        self.main_stack = QStackedWidget()
        self.home = Home()

        self.main_stack.addWidget(self.home)
        self.main_stack.addWidget(self.floor_browser)
        self.main_stack.addWidget(self.profile) 
        self.main_stack.addWidget(self.facilities)
        self.main_stack.addWidget(self.feedback)

        ColumnLayout.addWidget(self.main_stack)

        return Column2
    
    def thirdColumn(self):
        Column3 = self.Column3
        Column3.setObjectName("reservationColumn")
        Column3.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Scoped by id. The old unscoped "background-color: white; color: black" cascaded into
        # every child, and a white backdrop under the glass cards made their light text unreadable.
        Column3.setStyleSheet(f"QWidget#reservationColumn {{ background: {gradient}; }}")

        ColumnLayout = QVBoxLayout(Column3)
        ColumnLayout.setContentsMargins(0, 16, 0, 16)
        ColumnLayout.setSpacing(0)
        ColumnLayout.addWidget(self.reservation)
        return Column3

    def menunavigation(self, target):
        if target == "Home":
            self.main_stack.setCurrentIndex(0)
            self.Column3.hide()
            return
        if target == "Reserve":
            self.main_stack.setCurrentIndex(1)
            self.Column3.show()
            self.Column3.raise_()   # always paint above Column2 if the two ever touch
            self.Column3.resize(int(self.Column3.width()), int(self.Column3.height()))
            return
        if target == "Profile":
            self.Handler.handleFetchData()
            self.main_stack.setCurrentIndex(2)
            self.Column3.hide()
            return
        if target == "Facilities":
            self.main_stack.setCurrentIndex(3)
            self.Column3.hide()
        if target == "Feedback":
            self.main_stack.setCurrentIndex(4)
            self.Column3.hide()

    def updateVerificationOverlay(self, verified: bool):
        self.unverified.setHidden(verified)

    def updateUnverifiedFields(self, data: dict):
        fields = (
            (self._unverified_first_name, "First_name"),
            (self._unverified_last_name, "Last_name"),
            (self._unverified_year_level, "Year_level"),
            (self._unverified_college_course, "College_course"),
            (self._unverified_student_id, "student_id"),
        )
        for label, key in fields:
            if label is None:
                continue
            value = data.get(key)
            label.setText("—" if value is None or value == "" else str(value))

    def _update_overlay_geometry(self, overlay, child, width_ratio: float = 0.8, height_ratio: float = 0.8):
        if overlay is None or child is None:
            return
        w = self.container.width()
        h = self.container.height()
        overlay.setFixedSize(w, h)
        overlay.move(0, 0)
        cw = int(w * width_ratio)
        ch = int(h * height_ratio)
        child.setFixedSize(cw, ch)
        child.move(int(w * 0.5 - cw * 0.5), int(h * 0.5 - ch * 0.5))

    def _install_container_resize_handler(self):
        if self._resize_handler_installed:
            return
        self._resize_handler_installed = True

        def resizing(event):
            # Only the unverified overlay floats over the container now;
            # the profile lives inside Column2's stack and sizes itself.
            self._update_overlay_geometry(self.unverified, self._unverified_child)

        self.container.resizeEvent = resizing
        self._update_overlay_geometry(self.unverified, self._unverified_child)


    def unverifiedWidget(self):
        unverified = self.unverified
        unverified.setHidden(True)
 
        # Overlay = a light veil only. The old QGraphicsBlurEffect lived here, but
        # a blur on a parent blurs its children too, so the card text was blurred.
        unverified.setObjectName("unverifiedOverlay")
        unverified.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
 
        child = QWidget(unverified)
        child.setObjectName("unverifiedCard")
        child.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
 
        # Soft shadow gives the "floating glass" depth (delete these 4 lines to disable)
        shadow = QGraphicsDropShadowEffect(child)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(30, 60, 20, 70))
        child.setGraphicsEffect(shadow)
 
        # ── Logo placeholder (top-left) ──────────────────────────
        logo_size = 48
        logo = QLabel()
        logo.setObjectName("unverifiedLogo")
        logo.setFixedSize(logo_size, logo_size)
        pixmap = QPixmap("resources/SJC_LOGo.png")  # <- point this at your real logo
        logo.setScaledContents(True)
        logo.setPixmap(pixmap)
 
        # ── Card skeleton: logo row + scrollable, width-capped form ──
        card_layout = QVBoxLayout(child)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(8)
        card_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignLeft)
 
        scroll = QScrollArea()
        scroll.setObjectName("unverifiedScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        card_layout.addWidget(scroll, stretch=1)
 
        content = QWidget()
        content.setObjectName("unverifiedContent")
        content.setMaximumWidth(480)  # inputs never stretch absurdly wide
        scroll.setWidget(content)
        # setWidget() turns on an opaque auto-fill; switch it off so glass shows through
        content.setAutoFillBackground(False)
        scroll.viewport().setAutoFillBackground(False)
 
        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)
 
        heading = QLabel("Verify your account")
        heading.setObjectName("unverifiedHeading")
        heading.setWordWrap(True)
        layout.addWidget(heading)
 
        subtitle = QLabel("Review your information and submit for verification.")
        subtitle.setObjectName("unverifiedSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        layout.addSpacing(6)
 
        def add_field(caption: str):
            wrapper = QWidget()
            wrapper.setObjectName("fieldRow")
            column = QVBoxLayout(wrapper)  # caption sits above input: survives narrow windows
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(6)
 
            title = QLabel(caption)
            title.setObjectName("fieldCaption")
 
            edit = QLineEdit()
            edit.setObjectName("fieldInput")
            edit.setPlaceholderText("Add Info here")
            edit.setMinimumHeight(42)
 
            column.addWidget(title)
            column.addWidget(edit)
            layout.addWidget(wrapper)
            return wrapper, edit
 
        self._unverified_first_name, self._unverified_first_name_value = add_field("First name")
        self._unverified_last_name, self._unverified_last_name_value = add_field("Last name")
        self._unverified_year_level, self._unverified_year_level_value = add_field("Year level")
        self._unverified_college_course, self._unverified_college_course_value = add_field("College course")
        self._unverified_student_id, self._unverified_student_id_value = add_field("Student ID")
 
        err = QLabel("")
        err.setObjectName("unverifiedError")
        err.setWordWrap(True)
 
        verify_btn = QPushButton("Verify")
        verify_btn.setObjectName("verifyButton")
        verify_btn.setMinimumHeight(44)
        verify_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        verify_btn.clicked.connect(lambda: AccountHandler().handleVerify(self._unverified_first_name_value, self._unverified_last_name_value, self._unverified_year_level_value, self._unverified_college_course_value, self._unverified_student_id_value, err, verify_btn))
 
        delete_btn = QPushButton("Delete My Account")
        delete_btn.setObjectName("deleteButton")
        delete_btn.setMinimumHeight(34)
        delete_btn.setMinimumWidth(120)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.Handler.handleDelete(err))

        logout_btn = QPushButton("Log out")
        logout_btn.setObjectName("logoutButton")
        logout_btn.setMinimumHeight(34)
        logout_btn.setMinimumWidth(120)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(lambda: self.Handler.handleLogout())
 
        layout.addWidget(err)
        layout.addWidget(verify_btn)
        layout.addSpacing(4)
 
        # Delete + Log out share one row instead of stacking
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.addWidget(delete_btn)
        actions.addStretch(1)
        actions.addWidget(logout_btn)
        layout.addLayout(actions)
        layout.addStretch(1)
 
        # ── One stylesheet, object-name selectors only (no cascading border leaks) ──
        child.setStyleSheet("""
            * { font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif; }
 
            QWidget#unverifiedCard {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0   rgba(255, 255, 255, 100),
                    stop:0.5 rgba(241, 248, 209, 50),
                    stop:1   rgba(190, 224, 120, 50));
                border: 1px solid rgba(150, 158, 140, 150);
                border-radius: 24px;
            }
 
            QScrollArea#unverifiedScroll { background: transparent; border: none; }
            QScrollArea#unverifiedScroll > QWidget { background: transparent; }
            QWidget#unverifiedContent, QWidget#fieldRow { background: transparent; }
 
            QScrollBar:vertical { background: transparent; width: 8px; margin: 4px 0 4px 0; }
            QScrollBar::handle:vertical { background: rgba(70, 90, 50, 140); border-radius: 4px; min-height: 28px; }
            QScrollBar::handle:vertical:hover { background: rgba(70, 90, 50, 200); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
 
            QLabel { background: transparent; border: none; color: white; }
            QLabel#unverifiedHeading  { font-size: 26px; font-weight: 800; color: white; }
            QLabel#unverifiedSubtitle { font-size: 13px; font-weight: 600; color: white; }
            QLabel#fieldCaption       { font-size: 13px; font-weight: 700; color: white; }
            QLabel#unverifiedError    { font-size: 12px; font-weight: 700; color: white; }
 
            QLineEdit#fieldInput {
                background-color: rgba(255, 255, 255, 245);
                color: #14210C;
                border: 1px solid #C4CBB8;
                border-radius: 10px;
                padding: 0px 14px;
                font-size: 14px;
                font-weight: 600;
                selection-background-color: #A9D46C;
                selection-color: #14210C;
                placeholder-text-color: #5F6B54;
            }
            QLineEdit#fieldInput:hover    { border: 1px solid #A3AE94; }
            QLineEdit#fieldInput:focus    { border: 1px solid #5E9B2F; background-color: #FFFFFF; }
            QLineEdit#fieldInput:disabled { background-color: rgba(255, 255, 255, 140); color: #5F6B54; }
 
            QPushButton#verifyButton {
                background-color: #23411A; color: #FFFFFF;
                border: none; border-radius: 10px;
                font-size: 15px; font-weight: 700;
            }
            QPushButton#verifyButton:hover    { background-color: #33591F; }
            QPushButton#verifyButton:pressed  { background-color: #182F11; }
            QPushButton#verifyButton:disabled { background-color: #8FA07F; color: #EEF2E8; }
 
            QPushButton#deleteButton {
                background-color: rgba(255, 255, 255, 200); color: #B3261E;
                border: 1px solid rgba(179, 38, 30, 150); border-radius: 8px;
                font-size: 13px; font-weight: 700; padding: 0px 12px;
            }
            QPushButton#deleteButton:hover   { background-color: #B3261E; color: #FFFFFF; }
            QPushButton#deleteButton:pressed { background-color: #8C1D18; color: #FFFFFF; }
 
            QPushButton#logoutButton {
                background-color: rgba(255, 255, 255, 200); color: #2F3E22;
                border: 1px solid rgba(120, 130, 110, 170); border-radius: 8px;
                font-size: 13px; font-weight: 700; padding: 0px 12px;
            }
            QPushButton#logoutButton:hover   { background-color: #2F3E22; color: #FFFFFF; }
            QPushButton#logoutButton:pressed { background-color: #1F2A14; color: #FFFFFF; }
        """)
 
        self._unverified_child = child
        return unverified