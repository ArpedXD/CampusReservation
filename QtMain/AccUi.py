from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QStackedWidget, QPushButton, QLineEdit
from PySide6.QtCore import Qt, Signal, QObject

from System.AccountHandling.Account import AccountHandler

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

    def containers(self):
        container = self.container
        container.setStyleSheet("""background-color: qlineargradient(
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

        
        l = QLabel("PhinmaEd's Reservation Login System", container)
        l.setStyleSheet("background-color:None; font-size: 25px; font-family: Arial;")
        l.adjustSize()
        layout = QVBoxLayout(container)
        
        form = QWidget()
        form.setStyleSheet("""
            background-color: qlineargradient(
                spread: pad,
                x1: 1,
                y1: 1,
                x2: 0,
                y2: 0,
                stop: 1 rgba(237, 221, 83, 255),
                stop: 0.77 rgba(175, 212, 104, 255),
                stop: 0.45 rgba(87, 199, 133, 255),
                stop: 0 rgba(42, 123, 155, 255)
            );
            border-radius:25px; 
            border: 1px solid white;
        """)

        layout.addWidget(form,alignment=Qt.AlignmentFlag.AlignCenter)
        
        formInner = QWidget()
        
        formLayout = QVBoxLayout(formInner) # use form the central Layout of other elements.

        self.innerLayout = QHBoxLayout(form)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)

        self.loginUI = self.loginform()
        self.signupUI = self.signupform()

        self.FormStack = QStackedWidget()
        self.FormStack.addWidget(self.loginUI)
        self.FormStack.addWidget(self.signupUI)

        formLayout.addWidget(self.FormStack)
        self.innerLayout.addWidget(self.FormStack)

        formInner.setStyleSheet("background-color:white; border-radius:25px;")
        
        def reposition(event):
            l.move(self.container.width() * 0.5 - l.width() * 0.5,self.container.height() * 0.1)
            form.setFixedSize(int(container.width() * 0.5), int(container.height() * 0.6))
            formInner.setFixedSize(int(form.width() * 0.99), int(form.height() * 0.99))

        container.resizeEvent = reposition
        return container

    def buttons(self, parent, types):
        Column = QWidget()
        ColumnLayout = QHBoxLayout(Column)
        ColumnLayout.setContentsMargins(0, 0, 0, 0)
        ColumnLayout.setSpacing(0)
        
        Column.setStyleSheet("background-color:red; border:1px solid black;")

        Column.setFixedSize(parent.width() * 0.5, parent.height() * 0.1)

        lgbtn = QPushButton("Login")
        sgbtn = QPushButton("Signup")
        
        lgbtn.setCursor(Qt.CursorShape.PointingHandCursor)
        lgbtn.setFixedSize(Column.width()/2, Column.height())
        sgbtn.setCursor(Qt.CursorShape.PointingHandCursor)
        sgbtn.setFixedSize(Column.width()/2, Column.height())

        if types == "login":
            lgbtn.setStyleSheet("color:white; background-color:black; border:1px solid white; border-radius:25px;")
            sgbtn.setStyleSheet("color:black; background-color:white; border:1px solid black; border-radius:25px;")
        else:
            lgbtn.setStyleSheet("color:black; background-color:white; border:1px solid black; border-radius:25px;")
            sgbtn.setStyleSheet("color:white; background-color:black; border:1px solid white; border-radius:25px;")
        ColumnLayout.addWidget(lgbtn)
        ColumnLayout.addWidget(sgbtn)

        lgbtn.clicked.connect(lambda: self.navigation.emit("login"))
        sgbtn.clicked.connect(lambda: self.navigation.emit("signup"))

        return Column

    def loginform(self):
        login = QWidget()
        login.setStyleSheet("background-color: #FFFFFF; color: #171717; border: 1px solid #E5E5E5;")

        loginlayout = QVBoxLayout(login)

        usernameLabel = QLabel("Username")
        username = QLineEdit()
        username.setPlaceholderText("Enter your username")
        usernameLabel.setBuddy(username)

        passwordLabel = QLabel("Password")
        password = QLineEdit()
        password.setPlaceholderText("Enter your password")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        passwordLabel.setBuddy(password)

        errorLabel = QLabel("")
        errorLabel.setStyleSheet("color: #DC2626; font-size: 12px;")
        errorLabel.setVisible(False)

        submit = QPushButton("Sign in")
        submit.setMinimumHeight(44)
        submit.setCursor(Qt.CursorShape.PointingHandCursor)

        credentialsHolder = QWidget()
        credentialsHolder.setObjectName("Parent")
        credentialsHolder.setStyleSheet("""
            #Parent { border: none; }
            QLabel { font-size: 13px; font-weight: 600; color: #171717; }
            QLineEdit {
                padding: 10px;
                min-width: 200px;
                min-height: 24px;
                border: 1px solid #E5E5E5;
                border-radius: 6px;
                background-color: #FAFAFA;
            }
            QLineEdit:focus {
                border: 1px solid #A16207;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #171717;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #404040; }
            QPushButton:pressed { background-color: #A16207; }
            QPushButton:disabled { background-color: #A3A3A3; }
        """)
        credentialsLayout = QVBoxLayout(credentialsHolder)
        credentialsLayout.setSpacing(8)

        credentialsLayout.addWidget(usernameLabel)
        credentialsLayout.addWidget(username)
        credentialsLayout.addSpacing(4)
        credentialsLayout.addWidget(passwordLabel)
        credentialsLayout.addWidget(password)
        credentialsLayout.addWidget(errorLabel)
        credentialsLayout.addSpacing(8)
        credentialsLayout.addWidget(submit)

        loginlayout.addWidget(self.buttons(login, "login"), alignment=Qt.AlignmentFlag.AlignCenter)
        loginlayout.addStretch()
        loginlayout.addWidget(credentialsHolder, alignment=Qt.AlignmentFlag.AlignCenter)
        loginlayout.addStretch()

        Handler = AccountHandler() # LOGIC
        submit.clicked.connect(lambda: Handler.handleLogin(username, password, submit, errorLabel))
        password.returnPressed.connect(lambda: Handler.handleLogin(username, password, submit, errorLabel))
        return login

    def signupform(self):
        signup = QWidget()
        signup.setStyleSheet("background-color: #FFFFFF; color: #171717; border: 1px solid #E5E5E5;")

        signuplayout = QVBoxLayout(signup)

        usernameLabel = QLabel("Phinmaed Gmail")
        username = QLineEdit()
        username.setPlaceholderText("@phinmaed")
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
        errorLabel.setStyleSheet("color: #DC2626; font-size: 12px;")
        errorLabel.setVisible(False)

        submit = QPushButton("Create account")
        submit.setMinimumHeight(44)
        submit.setCursor(Qt.CursorShape.PointingHandCursor)

        credentialsHolder = QWidget()
        credentialsHolder.setObjectName("Parent")
        credentialsHolder.setStyleSheet("""
            #Parent { border: none; }
            QLabel { font-size: 13px; font-weight: 600; color: #171717; }
            QLineEdit {
                padding: 10px;
                min-width: 200px;
                min-height: 24px;
                border: 1px solid #E5E5E5;
                border-radius: 6px;
                background-color: #FAFAFA;
            }
            QLineEdit:focus {
                border: 1px solid #A16207;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #171717;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #404040; }
            QPushButton:pressed { background-color: #A16207; }
            QPushButton:disabled { background-color: #A3A3A3; }
        """)
        credentialsLayout = QVBoxLayout(credentialsHolder)
        credentialsLayout.setSpacing(8)

        

        credentialsLayout.addWidget(usernameLabel)
        credentialsLayout.addWidget(username)
        credentialsLayout.addSpacing(4)
        credentialsLayout.addWidget(passwordLabel)
        credentialsLayout.addWidget(password)
        credentialsLayout.addSpacing(4)
        credentialsLayout.addWidget(confirmLabel)
        credentialsLayout.addWidget(confirmpassword)
        credentialsLayout.addWidget(errorLabel)
        credentialsLayout.addSpacing(8)
        credentialsLayout.addWidget(submit)

        signuplayout.addWidget(self.buttons(signup, "signup"), alignment=Qt.AlignmentFlag.AlignCenter)
        signuplayout.addStretch()
        signuplayout.addWidget(credentialsHolder, alignment=Qt.AlignmentFlag.AlignCenter)
        signuplayout.addStretch()

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