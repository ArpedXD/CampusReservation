import sys  
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from QtMain.Main import CommonContainer
from QtMain.AccUI import Form
from PySide6.QtCore import Signal, QTimer
import asyncio
import qasync
from System.AccountHandling.Account import AccountHandler
import ctypes


myappid = "mycompany.myproduct.subproduct.version"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow):
    mainSignal = Signal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campus Reservation")
        self.setWindowIcon(QIcon("resources/SJC_LOGO.png"))
        self.setMinimumSize(1200,600)
        self.showMaximized()
        self.stack = QStackedWidget()
        self.nav_name = QLabel("[Name]")
        self.form = Form()
        self.main = None

        self.FormUI = self.Form()
        self.Dashboard = self.DoubleColumn()

        self.setCentralWidget(self.stack)
        self.stack.addWidget(self.FormUI)
        self.mainSignal.connect(self.stackHandler)
        QTimer.singleShot(0,self.startcheck)

    def Form(self):
        self.form.containers()
        return self.form.container

    def DoubleColumn(self):
        self.main = CommonContainer()

        fl = QVBoxLayout(self.main.container)
        fl.setContentsMargins(0,0,0,0)

        nav_bar = QWidget()
        nav_bar.setStyleSheet("background-color: #23411A; font-size: 14px; font-weight: 700;")
        nav_barLayout = QHBoxLayout(nav_bar)
        schoolLogo = QPixmap("resources/SJC_LOGO.png")
        
        nav_label = QLabel("Campus Reservation")
        nav_name = self.nav_name
        logo = QLabel()
        logo.setFixedSize(50,50)
        logo.setPixmap(schoolLogo)
        logo.setScaledContents(True)
        nav_barLayout.addWidget(logo)
        nav_barLayout.addWidget(nav_label, alignment=Qt.AlignmentFlag.AlignLeft)
        nav_barLayout.addStretch()
        nav_barLayout.addWidget(nav_name, alignment=Qt.AlignmentFlag.AlignRight)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        fl.addWidget(nav_bar, stretch=1)
        fl.addLayout(layout, stretch=10)

        layout.addWidget(self.main.firstColumn(), stretch=1)
        layout.addWidget(self.main.secondColumn(), stretch=3)
        layout.addWidget(self.main.thirdColumn(), stretch=3)

        # Raises UI to profile AFTER widget
        self.main.unverified.raise_()
        self.main._install_container_resize_handler()
        return self.main.container
    
    def startcheck(self): # Handles function when the application starts
        self.VerifyLoginSync = AccountHandler().handleInformations()

    def stackHandler(self, stacks):
        if stacks == "Form":
            self.stack.setCurrentWidget(self.FormUI)
        if stacks == "DoubleColumn":
            self.Dashboard = self.DoubleColumn()
            AccountHandler().getusernames()
            self.stack.addWidget(self.Dashboard)
            self.stack.setCurrentWidget(self.Dashboard)
    

app = QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)
window = MainWindow()
app.mainwindow = window
window.show()

with loop:
    loop.run_forever()