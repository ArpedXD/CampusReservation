import sys  
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from QtMain.Main import CommonContainer
import asyncio
import qasync
import ctypes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main = CommonContainer()
        self.setMinimumSize(1200,600)
        self.setCentralWidget(self.DoubleColumn())

    def DoubleColumn(self):
        self.main = CommonContainer()

        fl = QVBoxLayout(self.main.container)
        fl.setContentsMargins(0,0,0,0)

        nav_bar = QWidget()
        nav_bar.setStyleSheet("background-color: #23411A; font-size: 14px; font-weight: 700;")
        nav_barLayout = QHBoxLayout(nav_bar)
        schoolLogo = QPixmap("resources/SJC_LOGO.png")
        
        nav_label = QLabel("Campus Reservation")
        nav_name = QLabel("test_123")
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
        
app = QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)
window = MainWindow()
app.mainwindow = window
window.show()

with loop:
    loop.run_forever()