from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsBlurEffect, QLabel, QLineEdit, QGraphicsDropShadowEffect, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal, QObject, QRect, QRectF, QPoint
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QLinearGradient
from PySide6.QtCore import QSize

from QtFilters.MenuHandler import MenuHandler
from QtMenu.Menu import Menu
from System.AccountHandling.Account import AccountHandler
from QFloor.Floor_browser import FloorBrowser

class CommonContainer(QObject):
    NavigateToMenu = Signal(str)
    def __init__(self):
        super().__init__()
        self.form = None
        self.container = QWidget()
        self.Column1 = QWidget()
        self.Column2 = QWidget()
        self.NavigateToMenu.connect(self.menunavigation)
        self.Handler = AccountHandler()

        self._unverified_child = None
        self._profile_child = None
        self._resize_handler_installed = False

        self.unverified = QWidget(self.container)
        self.unverifiedWidget()
        self.profile = QWidget(self.container)
        self.ProfileWidget()

    def common(self):
        self.container.setStyleSheet("""background-color: qlineargradient(
            spread: pad,
            x1: 0,
            y1: 0,
            x2: 1,
            y2: 1,
            stop: 0 rgba(42, 123, 155, 255),
            stop: 0.45 rgba(87, 199, 133, 255),
            stop: 0.77 rgba(175, 212, 104, 255),
            stop: 1 rgba(237, 221, 83, 255)
        );""")

        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(10,10,10,10)
        return layout
    
    def open_reservation_form(self, info: dict):
        print(info)

    def LeftColumn(self):
        Column1 = self.Column1
        
        mainLayout = QVBoxLayout(Column1)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(0)
        OpenMenu = QPushButton()
        OpenMenu.setCursor(Qt.CursorShape.PointingHandCursor)

        OpenMenu.setIcon(QIcon("resources/menu-button.png"))
        OpenMenu.setText("hi")
        OpenMenu.setIconSize(QSize(35, 35))

        menu = Menu() #---- Menu Part
        menu.button3.clicked.connect(lambda: self.NavigateToMenu.emit("Profile")) # connects button to navigation (note to self: Connect the other buttons through this way aswell)
        menu.button4.clicked.connect(lambda: self.Handler.handleLogout())
        containers = menu.containers()

        mainLayout.addWidget(OpenMenu, alignment=Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(containers, alignment=Qt.AlignmentFlag.AlignLeft)
        mainLayout.addStretch()

        OpenMenu.clicked.connect(lambda: MenuHandler().visibility(containers))

        Column1.setStyleSheet("""
            background-color: white;
            color:blacks;
        """)
        # child widget
        return Column1

    def RightColumn(self):
        Column2 = self.Column2
        Column2.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            color:black;
        """)
        ColumnLayout = QVBoxLayout(Column2)

        self.floor_browser = FloorBrowser()
        self.floor_browser.setFixedSize(Column2.width(), Column2.height())
        self.floor_browser.room_selected.connect(self.open_reservation_form)
        ColumnLayout.addWidget(self.floor_browser)

        def resize(event):
            self.floor_browser.setFixedSize(Column2.width(), Column2.height())

        Column2.resizeEvent = resize

        return Column2

    def menunavigation(self, target):
        if target == "Profile":
            self.Handler.handleFetchData()
            if self.profile.isHidden():
                return self.profile.setHidden(False)
            return self.profile.setHidden(True)
        
    def ChangeProfileCredentials(self, credentials: dict):
        print('test')
        self._profile_username.setText(f"{credentials["Last_name"]}, {credentials["First_name"]}")
        self._profile_email.setText(credentials["Email"])
        self._profile_year_level.setText(f"Year {credentials["Year_Level"]}")
        self._profile_course.setText(credentials["College_course"])
        self._profile_student_id.setText(credentials["student_id"])

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

    def _update_overlay_geometry(self, overlay, child):
        if overlay is None or child is None:
            return
        w = self.container.width()
        h = self.container.height()
        overlay.setFixedSize(w, h)
        overlay.move(0, 0)
        cw = int(w * 0.8)
        ch = int(h * 0.8)
        child.setFixedSize(cw, ch)
        child.move(int(w * 0.5 - cw * 0.5), int(h * 0.5 - ch * 0.5))

    def _install_container_resize_handler(self):
        if self._resize_handler_installed:
            return
        self._resize_handler_installed = True

        def resizing(event):
            self._update_overlay_geometry(self.unverified, self._unverified_child)
            self._update_overlay_geometry(self.profile, self._profile_child)

        self.container.resizeEvent = resizing
        self._update_overlay_geometry(self.unverified, self._unverified_child)
        self._update_overlay_geometry(self.profile, self._profile_child)

    def ProfileWidget(self):
        """Builds the profile overlay like a frosted shower door: we photograph what's
        behind the glass, smudge it soft, and paint that under the card, so the
        background looks blurred while the text on top stays sharp. Why: Qt's blur
        effect would smear the text too."""
        ParentWidget = self.profile
        ParentWidget.setHidden(True)
        ParentWidget.setObjectName("profileOverlay")
        ParentWidget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Own rule so the container's gradient stylesheet doesn't leak into the overlay
        ParentWidget.setStyleSheet("QWidget#profileOverlay { background: transparent; }")
 
        # Shared state for the frosted-glass effect
        glass = {"blurred": None, "capturing": False}
 
        # ── The card (self._profile_child is what the resize handler positions/sizes) ──
        self._profile_child = QWidget(ParentWidget)
        card = self._profile_child
        card.setObjectName("profileCard")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
 
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 45))
        card.setGraphicsEffect(shadow)
 
        # ── 1) Close button (top right) ──────────────────────────────────────
        close_btn = QPushButton("×")
        close_btn.setObjectName("profileClose")
        close_btn.setToolTip("Close")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(lambda: self.NavigateToMenu.emit("Profile"))
 
        # ── 3) Credentials header ────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("profileHeader")
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(16, 12, 16, 12)
        header_row.setSpacing(16)
 
        # Picture placeholder (QPixmap drawn in code, so no image file is needed).
        # Swap it later with: self._profile_picture.setPixmap(QPixmap("path/to/photo.png"))
        placeholder = QPixmap(128, 128)
        placeholder.fill(Qt.GlobalColor.transparent)
        p = QPainter(placeholder)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        circle = QPainterPath()
        circle.addEllipse(0, 0, 128, 128)
        p.setClipPath(circle)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 170))
        p.drawEllipse(0, 0, 128, 128)           # plate
        p.setBrush(QColor(30, 42, 58, 110))
        p.drawEllipse(44, 24, 40, 40)           # head
        p.drawEllipse(24, 76, 80, 80)           # shoulders (clipped by the circle)
        p.end()
 
        avatar = QLabel()
        avatar.setObjectName("profileAvatar")
        avatar.setFixedSize(64, 64)
        avatar.setScaledContents(True)
        avatar.setPixmap(placeholder)
        self._profile_picture = avatar
 
        def make_label(name: str, text: str) -> QLabel:
            label = QLabel(text)
            label.setObjectName(name)
            return label
 
        # Fill these later, e.g. self._profile_username.setText("arp")
        self._profile_username = make_label("profileUsername", "Username")
        self._profile_email = make_label("profileDetail", "Email")
        self._profile_year_level = make_label("profileDetail", "Year level")
        self._profile_course = make_label("profileDetail", "Course")
        self._profile_student_id = make_label("profileDetail", "Student ID")
 
        details = QHBoxLayout()
        details.setContentsMargins(0, 0, 0, 0)
        details.setSpacing(14)
        details.addWidget(self._profile_email)
        details.addWidget(self._profile_year_level)
        details.addWidget(self._profile_course)
        details.addWidget(self._profile_student_id)
        details.addStretch(1)
 
        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(4)
        info.addStretch(1)
        info.addWidget(self._profile_username)
        info.addLayout(details)
        info.addStretch(1)
 
        role = QLabel("STUDENT")
        role.setObjectName("profileRole")
        role.setAlignment(Qt.AlignmentFlag.AlignCenter)
 
        header_row.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_row.addLayout(info, stretch=1)
        header_row.addWidget(role, alignment=Qt.AlignmentFlag.AlignVCenter)
 
        # ── 4) Blank scrollable plate ────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setObjectName("profileScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
 
        # The viewport is the glass pane; the plate scrolls on top of it
        viewport = scroll.viewport()
        viewport.setObjectName("profileViewport")
        viewport.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        viewport.setAutoFillBackground(False)
 
        plate = QWidget()
        plate.setObjectName("profilePlate")
        scroll.setWidget(plate)
        plate.setAutoFillBackground(False)   # setWidget() turns it on; glass must show through
 
        # Empty for now: add future content with self._profile_body_layout.addWidget(...)
        self._profile_body_layout = QVBoxLayout(plate)
        self._profile_body_layout.setContentsMargins(16, 16, 16, 16)
        self._profile_body_layout.addStretch(1)
 
        # ── Card skeleton: close row, header (~10%), scroll body (~90%) ──────
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 14, 20, 20)
        card_layout.setSpacing(12)
 
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.addStretch(1)
        top_bar.addWidget(close_btn)
 
        card_layout.addLayout(top_bar)
        card_layout.addWidget(header, stretch=1)
        card_layout.addWidget(scroll, stretch=9)
 
        # ── 5) Glassmorphism (white) ─────────────────────────────────────────
        card.setStyleSheet("""
            * { font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif; }
 
            QWidget#profileCard { background: transparent; border: none; }
 
            QWidget#profileHeader {
                background-color: rgba(255, 255, 255, 90);
                border: 1px solid rgba(255, 255, 255, 190);
                border-radius: 18px;
            }
 
            QScrollArea#profileScroll { background: transparent; border: none; }
            QWidget#profileViewport {
                background-color: rgba(255, 255, 255, 70);
                border: 1px solid rgba(255, 255, 255, 190);
                border-radius: 18px;
            }
            QWidget#profilePlate { background: transparent; }
 
            QScrollBar:vertical { background: transparent; width: 8px; margin: 8px 0 8px 0; }
            QScrollBar::handle:vertical { background: rgba(255, 255, 255, 200); border-radius: 4px; min-height: 28px; }
            QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 255); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
 
            QLabel { background: transparent; border: none; color: #1E2A3A; }
            QLabel#profileAvatar   { border: 2px solid rgba(255, 255, 255, 220); border-radius: 32px; }
            QLabel#profileUsername { font-size: 18px; font-weight: 800; color: #1E2A3A; }
            QLabel#profileDetail   { font-size: 12px; font-weight: 600; color: #4A5868; }
            QLabel#profileRole {
                background-color: rgba(255, 255, 255, 140);
                border: 1px solid rgba(255, 255, 255, 220);
                border-radius: 12px;
                padding: 4px 14px;
                font-size: 12px; font-weight: 800; color: #1E2A3A;
            }
 
            QPushButton#profileClose {
                background: transparent; color: #1E2A3A;
                border: 1px solid transparent; border-radius: 16px;
                font-size: 20px; font-weight: 600;
            }
            QPushButton#profileClose:hover   { background-color: rgba(255, 255, 255, 170); border: 1px solid rgba(255, 255, 255, 230); }
            QPushButton#profileClose:pressed { background-color: rgba(255, 255, 255, 230); }
        """)
 
        # ── Backdrop blur (fake "frosted glass") ─────────────────────────────
        def blur(pixmap: QPixmap, factor: int = 24) -> QPixmap:
            # Shrink to a few pixels, then stretch back with smoothing: fast and very soft.
            # Bigger factor = blurrier.
            pixmap.setDevicePixelRatio(1.0)
            w, h = pixmap.width(), pixmap.height()
            tiny = pixmap.scaled(max(1, w // factor), max(1, h // factor),
                                 Qt.AspectRatioMode.IgnoreAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
            return tiny.scaled(w, h,
                               Qt.AspectRatioMode.IgnoreAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
 
        def capture_backdrop():
            # Photograph the container without the overlay/card, then blur it
            glass["capturing"] = True
            card.hide()
            snapshot = self.container.grab()
            card.show()
            glass["capturing"] = False
            glass["blurred"] = blur(snapshot)
 
        def on_show(event):
            capture_backdrop()
 
        def paint_overlay(event):
            # Light white veil over the whole window (skipped while photographing)
            if glass["capturing"]:
                return
            painter = QPainter(ParentWidget)
            painter.fillRect(ParentWidget.rect(), QColor(255, 255, 255, 90))
            painter.end()
 
        def paint_card(event):
            painter = QPainter(card)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
 
            shape = QPainterPath()
            shape.addRoundedRect(QRectF(card.rect()).adjusted(1, 1, -1, -1), 24, 24)
 
            # a) blurred slice of the backdrop that sits exactly behind the card
            blurred = glass["blurred"]
            if blurred is not None:
                origin = card.mapTo(self.container, QPoint(0, 0))
                kx = blurred.width() / max(1, self.container.width())
                ky = blurred.height() / max(1, self.container.height())
                source = QRect(int(origin.x() * kx), int(origin.y() * ky),
                               int(card.width() * kx), int(card.height() * ky))
                painter.setClipPath(shape)
                painter.drawPixmap(card.rect(), blurred, source)
                painter.setClipping(False)
 
            # b) white frost tint
            tint = QLinearGradient(0, 0, card.width(), card.height())
            tint.setColorAt(0.0, QColor(255, 255, 255, 140))
            tint.setColorAt(1.0, QColor(255, 255, 255, 70))
            painter.fillPath(shape, QBrush(tint))
 
            # c) white glass edge
            painter.setPen(QPen(QColor(255, 255, 255, 190), 1.5))
            painter.drawPath(shape)
            painter.end()
 
        ParentWidget.showEvent = on_show
        ParentWidget.paintEvent = paint_overlay
        card.paintEvent = paint_card
 
        self._install_container_resize_handler()
        return ParentWidget

    def unverifiedWidget(self):
        unverified = self.unverified
        unverified.setHidden(True)
 
        # Overlay = a light veil only. The old QGraphicsBlurEffect lived here, but
        # a blur on a parent blurs its children too, so the card text was blurred.
        unverified.setObjectName("unverifiedOverlay")
        unverified.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        unverified.setStyleSheet(
            "QWidget#unverifiedOverlay { background-color: rgba(255, 255, 255, 0.5); }"
        )
 
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
 
            QLabel { background: transparent; border: none; color: #1F2A14; }
            QLabel#unverifiedHeading  { font-size: 26px; font-weight: 800; color: #14210C; }
            QLabel#unverifiedSubtitle { font-size: 13px; font-weight: 600; color: #38482A; }
            QLabel#fieldCaption       { font-size: 13px; font-weight: 700; color: #22321A; }
            QLabel#unverifiedError    { font-size: 12px; font-weight: 700; color: #B00020; }
 
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