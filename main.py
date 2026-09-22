import sys  
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QIcon
from QtMain.Main import CommonContainer
from QtMain.AccUi import Form
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
        self.stack = QStackedWidget()

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
        layout = self.main.common()

        layout.addWidget(self.main.LeftColumn(), stretch=1)
        layout.addWidget(self.main.RightColumn(), stretch=3)

        # Raises UI to profile AFTER widget
        self.main.profile.raise_()
        self.main.unverified.raise_()
        return self.main.container
    
    def startcheck(self): # Handles function when the application starts
        self.VerifyLoginSync = AccountHandler().handleInformations()

    def stackHandler(self, stacks):
        if stacks == "Form":
            self.stack.setCurrentWidget(self.FormUI)
        if stacks == "DoubleColumn":
            self.Dashboard = self.DoubleColumn()
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