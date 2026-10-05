import sys  
from PySide6.QtWidgets import QApplication,QMainWindow
from QtMain.Main import CommonContainer
import qasync
import asyncio

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main = CommonContainer()
        self.setMinimumSize(1200,600)
        self.setCentralWidget(self.doubl())

    def doubl(self):
        self.main = CommonContainer()
        layout = self.main.common()

        layout.addWidget(self.main.firstColumn(), stretch=1)
        layout.addWidget(self.main.secondColumn(), stretch=3)
        layout.addWidget(self.main.thirdColumn(), stretch=1)

        # Raises UI to profile AFTER widget
        self.main.profile.raise_()
        self.main.unverified.raise_()
        self.main.reservation.raise_()
        return self.main.container
        
app = QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)
window = MainWindow()
app.mainwindow = window
window.show()

with loop:
    loop.run_forever()