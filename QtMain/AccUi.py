from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QStackedWidget, QPushButton, QLineEdit, QSizePolicy
from PySide6.QtCore import Qt, Signal, QObject, QTimer
from PySide6.QtGui import QPixmap
from shiboken6 import isValid
from System.AccountHandling.Account import AccountHandler

# ---- shared design tokens ----------------------------------------------
INK = "#171717"
SUBTLE = "#000000"
BORDER = "#D9D9D9"
FIELD_BG = "#FAFAFA"
ACCENT = "#2A7B9B"
ACCENT_DARK = "#1F5F78"


class Form(QObject):
    navigation = Signal(str)
    def __init__(self):
        super().__init__()
        self.container = QWidget()
        self.data = {
            "verified" : False,
            "firstname": None,
            "lastname": None,
            "YearLevel": None,
            "Course": None,
            "student_id" : None,
        }
        self.navigation.connect(self.connection)

        self.loader = QWidget()
        self.toastDelete()
        self.container.resizeEvent = self.resizeFilter

    def toastDelete(self):
        self.loader.deleteLater()

    def toast(self, messages=None):
        parent = self.container
        # Edit these to match what is actually loading; the last one stays on screen
        messages = messages or [
            "Getting things ready",
            "Fetching your data",
            "Putting it all together",
            "Almost there",
            "Still working, thanks for waiting",
        ]

        self.loader = QWidget(parent)
        self.loader.setStyleSheet("background-color:rgba(255,255,255, 0.8);")
        self.loader.setFixedSize(int(self.container.width()), int(self.container.height()))

        self.loading = QWidget(self.loader)
        self.loading.setObjectName("widg")
        self.loading.setStyleSheet("#widg{background-color:white; border: 1px solid black}")

        # Text: one status message at a time
        self.loading_text = QLabel(messages[0], self.loading)
        self.loading_text.setAlignment(Qt.AlignCenter)
        self.loading_text.setWordWrap(True)
        self.loading_text.setStyleSheet(
            "background:transparent; color:#222; font-size:16px; font-weight:600;"
        )

        # Movement: a bar sweeping through a track (the track clips the bar)
        self.loading_track = QWidget(self.loading)
        self.loading_track.setStyleSheet("background-color:#e6e6e6;")
        self.loading_bar = QWidget(self.loading_track)
        self.loading_bar.setStyleSheet("background-color:red;")

        self._tick = 0

        def layoutE():
            lw, lh = self.loader.width(), self.loader.height()

            # A quarter of the loader, but never so small that the text gets squashed
            w = min(max(int(lw / 4), 240), lw)
            h = min(max(int(lh / 4), 120), lh)
            self.loading.setFixedSize(w, h)

            # Centre: half of the leftover space on each side
            self.loading.move((lw - w) // 2, (lh - h) // 2)

            margin = max(int(w * 0.08), 12)
            track_h = 4
            inner_w = max(w - margin * 2, 1)

            self.loading_text.setGeometry(margin, 0, inner_w, h - margin)
            self.loading_track.setGeometry(margin, h - margin - track_h, inner_w, track_h)
            self.loading_bar.setFixedSize(max(int(inner_w * 0.3), 1), track_h)

        def step():
            self._tick += 1

            # Sweep: enters from the left edge, exits at the right, then repeats (~1.2s)
            period = 75
            t = (self._tick % period) / period
            bar_w = self.loading_bar.width()
            track_w = self.loading_track.width()
            self.loading_bar.move(int(-bar_w + (track_w + bar_w) * t), 0)

            # Message: advance every ~1.8s, then hold on the last one
            index = min(self._tick // 110, len(messages) - 1)
            if self.loading_text.text() != messages[index]:
                self.loading_text.setText(messages[index])

        def loadE(event):
            layoutE()

        self.loader.resizeEvent = loadE

        # Parented to the loader, so the timer is destroyed together with it
        self.loading_timer = QTimer(self.loader)
        self.loading_timer.timeout.connect(step)
        self.loading_timer.start(16)  # ~60 fps

        layoutE()
        self.loader.show()
        self.loader.raise_()

    def resizeFilter(self, event):
        if self.loader and isValid(self.loader):
            self.loader.setFixedSize(int(self.container.width()), int(self.container.height()))

    def containers(self):
        container = self.container
        container.setStyleSheet("background-color: #FFFFFF;")

        mainLayout = QHBoxLayout(container)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ------------------------------------------------------------
        # LEFT: the functional login / signup panel
        # ------------------------------------------------------------
        
        self.sjc_logo = QPixmap('resources/SJC_LOGO.png')

        leftPanel = QWidget()
        leftPanel.setObjectName("LeftPanel")
        leftPanel.setStyleSheet("#LeftPanel { background-color: #FFFFFF; border: none}")

        leftLayout = QVBoxLayout(leftPanel)
        leftLayout.setContentsMargins(64, 48, 64, 48)
        leftLayout.setSpacing(0)
        topLayout = QHBoxLayout()

        brand = QLabel("PhinmaEd")
        brand.setStyleSheet(f"""
            background: transparent;
            color: {INK};
            font-size: 20px;
            font-weight: 700;
            font-family: Bold;
        """)
        brandimg = QLabel()
        brandimg.setFixedSize(50,50)
        brandimg.setPixmap(self.sjc_logo)
        brandimg.setScaledContents(True)
        topLayout.addWidget(brandimg, alignment=Qt.AlignmentFlag.AlignLeft)
        topLayout.addSpacing(5)
        topLayout.addWidget(brand, alignment=Qt.AlignmentFlag.AlignLeft)
        topLayout.addStretch(1)

        self.loginUI = self.loginform()
        self.signupUI = self.signupform()

        self.FormStack = QStackedWidget()
        self.FormStack.setStyleSheet("background: transparent; border: none;")
        self.FormStack.addWidget(self.loginUI)
        self.FormStack.addWidget(self.signupUI)

        leftLayout.addLayout(topLayout)
        leftLayout.addWidget(self.FormStack, alignment=Qt.AlignmentFlag.AlignCenter)
        leftLayout.addStretch(2)

        # ------------------------------------------------------------
        # RIGHT: decorative / branding panel
        # a soft white-to-transparent wash fading into the brand
        # gradient, with a Login/Signup headline, supporting copy,
        # and a white placeholder tile (bottom-right) reserved for
        # an image you'll drop in later.
        # ------------------------------------------------------------
        rightPanel = QWidget()
        
        rightPanel.setObjectName("RightPanel")
        rightpanelimg = QLabel()
        rightPanellayout = QVBoxLayout(rightPanel)
        rightPanellayout.setSpacing(0)
        rightPanellayout.setContentsMargins(0, 0, 0, 0)
        rightPanellayout.addWidget(rightpanelimg)
        rightpanelimg.setScaledContents(True)
        schoolLogo = QPixmap("resources/School2.png")
        rightpanelimg.setPixmap(schoolLogo)

        rightLayout = QVBoxLayout(rightpanelimg)
        rightLayout.setContentsMargins(56, 56, 56, 56)
        rightLayout.setSpacing(16)

        imageRow = QHBoxLayout()
        imageRow.addStretch(1)
        # Placeholder tile for your future image — bottom-right corner
        # of the right panel, plain white background.
        self.imagePlaceholder = QLabel()
        self.imagePlaceholder.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.imagePlaceholder.setPixmap(self.sjc_logo)
        self.imagePlaceholder.setScaledContents(True)
        self.imagePlaceholder.setObjectName("ImagePlaceholder")
        self.imagePlaceholder.setFixedSize(100, 100)
        self.imagePlaceholder.setStyleSheet("""
            #ImagePlaceholder {
                border-radius: 20px;
                background:transparent;
            }
        """)

        imageRow.addWidget(
            self.imagePlaceholder,
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
        )
        
        rightLayout.addLayout(imageRow)
        
        mainLayout.addWidget(leftPanel, 1)
        mainLayout.addWidget(rightPanel, 2)

        self.toast()
        return container

    def buttons(self, parent, types):
        Column = QWidget()
        Column.setObjectName("Toggle")
        ColumnLayout = QHBoxLayout(Column)
        ColumnLayout.setContentsMargins(0, 0, 0, 0)
        ColumnLayout.setSpacing(0)
        Column.setFixedSize(268, 46)

        Column.setStyleSheet("""
            #Toggle {
                background-color: #F2F2F2;
                border: 1px solid #E5E5E5;
                border-radius: 21px;
            }
        """)

        lgbtn = QPushButton("Login")
        sgbtn = QPushButton("Signup")

        lgbtn.setCursor(Qt.CursorShape.PointingHandCursor)
        sgbtn.setCursor(Qt.CursorShape.PointingHandCursor)
        lgbtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding )
        sgbtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding )

        activeStyle = f"""
            QPushButton {{
                color: white;
                background-color:black;
                border: none;
                border-radius: none;
                font-size: 14px;
                font-weight: 600;
                font-family: Arial;
            }}
        """
        inactiveStyle = f"""
            QPushButton {{
                color: black;
                background-color:rgb(200,200,200);
                border: none;
                border-radius: none;
                font-size: 14px;
                font-weight: 600;
                font-family: Arial;
            }}
            QPushButton:hover {{
                color: {INK};
            }}
        """

        if types == "login":
            lgbtn.setStyleSheet(activeStyle)
            sgbtn.setStyleSheet(inactiveStyle)
        else:
            lgbtn.setStyleSheet(inactiveStyle)
            sgbtn.setStyleSheet(activeStyle)

        ColumnLayout.addWidget(lgbtn)
        ColumnLayout.addWidget(sgbtn)

        lgbtn.clicked.connect(lambda: self.navigation.emit("login"))
        sgbtn.clicked.connect(lambda: self.navigation.emit("signup"))

        return Column

    def loginform(self):
        login = QWidget()
        login.setFixedWidth(360)
        login.setStyleSheet("background-color: transparent; border: none;")
        
        loginlayout = QVBoxLayout(login)

        loginlayout.addWidget(self.buttons(login, "login"), alignment=Qt.AlignmentFlag.AlignCenter)

        heading = QLabel("Login to your Account")
        heading.setStyleSheet(f"""
            background: transparent;
            color: {INK};
            font-size: 22px;
            font-weight: 700;
            font-family: Bold ;
        """)
        headingSub = QLabel("Sign in to continue to your PhinmaEd account.")
        headingSub.setWordWrap(True)
        headingSub.setStyleSheet(f"""
            background: transparent;
            color: {SUBTLE};
            font-size: 13px;
            font-family: Arial;
        """)

        loginlayout.addWidget(heading)
        loginlayout.addWidget(headingSub)
        loginlayout.addSpacing(20)

        usernameLabel = QLabel("Username")
        username = QLineEdit()
        username.setPlaceholderText("Enter your username")
        usernameLabel.setBuddy(username)

        passwordLabel = QLabel("Password")
        password = QLineEdit()
        password.setPlaceholderText("Enter your password")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        passwordLabel.setBuddy(password)

        errorLabel = QLabel("hi")
        errorLabel.setWordWrap(True)
        errorLabel.setStyleSheet("background: transparent; color: #DC2626; font-size: 12px; font-family: Arial;")
        errorLabel.setVisible(False)

        submit = QPushButton("Sign in")
        submit.setMinimumHeight(46)
        submit.setCursor(Qt.CursorShape.PointingHandCursor)

        credentialsHolder = QWidget()
        credentialsHolder.setObjectName("Parent")
        credentialsHolder.setStyleSheet(f"""
            #Parent {{ background: transparent; border: none; }}
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {INK};
                font-family: Arial;
                background: transparent;
            }}
            QLineEdit {{
                padding: 12px 14px;
                min-height: 22px;
                border: 1px solid {BORDER};
                border-radius: 10px;
                background-color: {FIELD_BG};
                font-size: 14px;
                font-family: Arial;
                color: {INK};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {ACCENT};
                background-color: #FFFFFF;
            }}
            QPushButton {{
                background-color: {INK};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 15px;
                font-family: Arial;
            }}
            QPushButton:hover {{ background-color: #333333; }}
            QPushButton:pressed {{ background-color: {ACCENT_DARK}; }}
            QPushButton:disabled {{ background-color: #A3A3A3; }}
        """)
        credentialsLayout = QVBoxLayout(credentialsHolder)
        credentialsLayout.setSpacing(6)
        credentialsLayout.setContentsMargins(0, 0, 0, 0)
        credentialsLayout.addWidget(usernameLabel)
        credentialsLayout.addWidget(username)
        credentialsLayout.addSpacing(14)
        credentialsLayout.addWidget(passwordLabel)
        credentialsLayout.addWidget(password)
        credentialsLayout.addSpacing(5)
        credentialsLayout.addWidget(errorLabel)
        credentialsLayout.addSpacing(10)
        credentialsLayout.addWidget(submit)

        loginlayout.addWidget(credentialsHolder)

        Handler = AccountHandler() # LOGIC
        submit.clicked.connect(lambda: Handler.handleLogin(username, password, submit, errorLabel))
        password.returnPressed.connect(lambda: Handler.handleLogin(username, password, submit, errorLabel))
        return login

    def signupform(self):
        signup = QWidget()
        signup.setFixedWidth(360)
        signup.setStyleSheet("background-color: transparent; border: none;")

        signuplayout = QVBoxLayout(signup)
        signuplayout.setSpacing(0)
        signuplayout.setContentsMargins(0, 0, 0, 0)

        signuplayout.addWidget(self.buttons(signup, "signup"), alignment=Qt.AlignmentFlag.AlignCenter)
        signuplayout.addSpacing(28)

        heading = QLabel("Create your account")
        heading.setStyleSheet(f"""
            background: transparent;
            color: {INK};
            font-size: 22px;
            font-weight: 700;
            font-family: Bold;
        """)
        headingSub = QLabel("Use your Phinmaed Gmail to get started.")
        headingSub.setWordWrap(True)
        headingSub.setStyleSheet(f"""
            background: transparent;
            color: {SUBTLE};
            font-size: 13px;
            font-family: Arial;
        """)

        signuplayout.addWidget(heading)
        signuplayout.addWidget(headingSub)
        signuplayout.addSpacing(20)

        usernameLabel = QLabel("Phinmaed Gmail")
        username = QLineEdit()
        username.setPlaceholderText("john@phinmaed")
        usernameLabel.setBuddy(username)

        passwordLabel = QLabel("Password")
        password = QLineEdit()
        password.setPlaceholderText("Create a password")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        passwordLabel.setBuddy(password)

        confirmLabel = QLabel("Confirm password")
        confirmpassword = QLineEdit()
        confirmpassword.setPlaceholderText("Re-enter your password")
        confirmpassword.setEchoMode(QLineEdit.EchoMode.Password)
        confirmLabel.setBuddy(confirmpassword)

        errorLabel = QLabel("")
        errorLabel.setWordWrap(True)
        errorLabel.setStyleSheet("background: transparent; color: #DC2626; font-size: 12px; font-family: Arial;")
        errorLabel.setVisible(False)

        submit = QPushButton("Create account")
        submit.setMinimumHeight(46)
        submit.setCursor(Qt.CursorShape.PointingHandCursor)

        credentialsHolder = QWidget()
        credentialsHolder.setObjectName("Parent")
        credentialsHolder.setStyleSheet(f"""
            #Parent {{ background: transparent; border: none; }}
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {INK};
                font-family: Arial;
                background: transparent;
            }}
            QLineEdit {{
                padding: 12px 14px;
                min-height: 22px;
                border: 1px solid {BORDER};
                border-radius: 10px;
                background-color: {FIELD_BG};
                font-size: 14px;
                font-family: Arial;
                color: {INK};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {ACCENT};
                background-color: #FFFFFF;
            }}
            QPushButton {{
                background-color: {INK};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 15px;
                font-family: Arial;
            }}
            QPushButton:hover {{ background-color: #333333; }}
            QPushButton:pressed {{ background-color: {ACCENT_DARK}; }}
            QPushButton:disabled {{ background-color: #A3A3A3; }}
        """)
        credentialsLayout = QVBoxLayout(credentialsHolder)
        credentialsLayout.setSpacing(6)
        credentialsLayout.setContentsMargins(0, 0, 0, 0)

        credentialsLayout.addWidget(usernameLabel)
        credentialsLayout.addWidget(username)
        credentialsLayout.addSpacing(14)
        credentialsLayout.addWidget(passwordLabel)
        credentialsLayout.addWidget(password)
        credentialsLayout.addSpacing(14)
        credentialsLayout.addWidget(confirmLabel)
        credentialsLayout.addWidget(confirmpassword)
        credentialsLayout.addWidget(errorLabel)
        credentialsLayout.addSpacing(10)
        credentialsLayout.addWidget(submit)

        signuplayout.addWidget(credentialsHolder)

        Handler = AccountHandler() # LOGIC
        submit.clicked.connect(lambda: Handler.handleSignup(username, password, confirmpassword, submit, errorLabel))
        confirmpassword.returnPressed.connect(lambda: Handler.handleSignup(username, password, confirmpassword, submit, errorLabel))
        return signup

    def connection(self, target):
        if target == "login":
            self.FormStack.setCurrentWidget(self.loginUI)
            return
        self.FormStack.setCurrentWidget(self.signupUI)
        return