from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsBlurEffect, QLabel, QLineEdit
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

from QtFilters.MenuHandler import MenuHandler
from QtMenu.Menu import Menu
from QtMenu.ChangeMapping import ChangeMapping
from System.AccountHandling.Account import AccountHandler

class CommonContainer(QObject):
    NavigateToMenu = Signal(str)
    def __init__(self, form):
        super().__init__()
        self.form = form
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

    def LeftColumn(self):
        Column1 = self.Column1
        
        mainLayout = QVBoxLayout(Column1)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(0)

        OpenMenu = QPushButton()
        OpenMenu.setCursor(Qt.CursorShape.PointingHandCursor)
        OpenMenu.setStyleSheet("""
            background-color: #ffffff;
            border: 1px solid #dcdcdc; 
            border-bottom: 3px solid #b0b0b0; 
            border-radius: 6px;
        """)

        OpenMenu.setIcon(QIcon("resources/menu-button.png"))
        OpenMenu.setIconSize(QSize(35, 35))

        menu = Menu() #---- Menu Part
        menu.button3.clicked.connect(lambda: self.NavigateToMenu.emit("Profile")) # connects button to navigation (note to self: Connect the other buttons through this way aswell)
        menu.button4.clicked.connect(lambda: self.Handler.handleLogout())
        containers = menu.containers()

        buttons = ChangeMapping()
        Mapping = buttons.containers()

        mainLayout.addWidget(OpenMenu, alignment=Qt.AlignmentFlag.AlignLeft)
        mainLayout.addWidget(containers, alignment=Qt.AlignmentFlag.AlignLeft)
        mainLayout.addStretch()
        mainLayout.addWidget(Mapping, alignment=Qt.AlignmentFlag.AlignLeft)

        OpenMenu.clicked.connect(lambda: MenuHandler().visibility(containers))

        Column1.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            color:black;
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

        return Column2

    def menunavigation(self, target):
        if target == "Profile":
            if self.profile.isHidden():
                return self.profile.setHidden(False)
            self.profile.setHidden(True)

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
        ParentWidget = self.profile
        ParentWidget.setHidden(True)
        ParentWidget.setStyleSheet("background-color:rgba(255,255,255,0.5)")
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(100)
        ParentWidget.setGraphicsEffect(blur)
        self._profile_child = QWidget(ParentWidget)
        self._profile_child.setStyleSheet("background-color:red; border-radius:25px;")
        self._install_container_resize_handler()
        return ParentWidget

    def unverifiedWidget(self):
        unverified = self.unverified
        unverified.setHidden(True)
        unverified.setStyleSheet("background-color:rgba(255,255,255,0.5)")
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(100)
        unverified.setGraphicsEffect(blur)

        child = QWidget(unverified)
        child.setStyleSheet("background-color: #FFFFFF; border-radius: 25px; color: #171717; border:1px solid black;")
        layout = QVBoxLayout(child)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(10)

        heading = QLabel("Verify your account")
        heading.setStyleSheet("font-size: 22px; font-weight: 600;border: 0px")
        layout.addWidget(heading)

        subtitle = QLabel("Review your information and submit for verification.")
        subtitle.setStyleSheet("font-size: 13px; color: #525252; border: 0px")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        def add_field(caption: str):
            row = QHBoxLayout()
            title = QLabel(caption)
            title.setStyleSheet("font-size: 13px; font-weight: 600; min-width: 130px; border: 0px")

            edit = QLineEdit() 
            edit.setPlaceholderText("Add Info here")

            row.addWidget(title, stretch=1)
            row.addWidget(edit, stretch=5)
            wrapper = QWidget()
            wrapper.setLayout(row)
            layout.addWidget(wrapper)
            return wrapper, edit

        self._unverified_first_name, self._unverified_first_name_value = add_field("First name")
        self._unverified_last_name, self._unverified_last_name_value = add_field("Last name")
        self._unverified_year_level, self._unverified_year_level_value = add_field("Year level")
        self._unverified_college_course, self._unverified_college_course_value = add_field("College course")
        self._unverified_student_id, self._unverified_student_id_value = add_field("Student ID")

        err = QLabel("")
        err.setStyleSheet("border:None; color: red;")

        verify_btn = QPushButton("Verify")
        verify_btn.setMinimumHeight(44)
        verify_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #171717;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #404040; }
            QPushButton:pressed { background-color: #A16207; }
        """)
        verify_btn.clicked.connect(lambda: AccountHandler().handleVerify(self._unverified_first_name_value, self._unverified_last_name_value, self._unverified_year_level_value, self._unverified_college_course_value, self._unverified_student_id_value, err))

        delete_btn = QPushButton("Delete My info")
        delete_btn.setMinimumHeight(23)
        delete_btn.setFixedWidth(100)
        delete_btn.adjustSize()
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(200,100,100);
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: rgb(100,50,50); }
            QPushButton:pressed { background-color: #A16207; }
        """)
        logout_btn = QPushButton("Log out")
        logout_btn.setMinimumHeight(23)
        logout_btn.setFixedWidth(100)
        logout_btn.adjustSize()
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(200,100,100);
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: rgb(100,50,50); }
            QPushButton:pressed { background-color: #A16207; }
        """)
        logout_btn.clicked.connect(lambda: self.Handler.handleLogout())

        def inputResizing(event):
            val = int(unverified.height())
            self._unverified_first_name.setMinimumHeight(val * 0.08)
            self._unverified_last_name.setMinimumHeight(val * 0.08)
            self._unverified_year_level.setMinimumHeight(val * 0.08)
            self._unverified_college_course.setMinimumHeight(val * 0.08)
            self._unverified_student_id.setMinimumHeight(val * 0.08)


        layout.addWidget(err)
        layout.addWidget(verify_btn)
        layout.addWidget(delete_btn)
        layout.setSpacing(10)
        layout.addWidget(logout_btn)

        self._unverified_child = child
        return unverified