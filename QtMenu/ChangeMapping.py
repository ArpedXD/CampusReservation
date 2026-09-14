from PySide6.QtWidgets import QWidget,QPushButton,QVBoxLayout 
from PySide6.QtCore import Qt

class ChangeMapping():
    def __init__(self):
        self.container = QWidget()

    def containers(self):
        buttonContainer = self.container

        Layout = QVBoxLayout(buttonContainer)
        button1 = QPushButton("^")
        button2 = QPushButton("v")
        buttonList = [button1, button2]
        
        for each in buttonList:
            each.setStyleSheet("""
                background-color: #ffffff;
                border: 1px solid #dcdcdc; 
                border-bottom: 3px solid #b0b0b0; 
            """)
            each.setFixedSize(100,40)
            Layout.addWidget(each)
            each.setCursor(Qt.CursorShape.PointingHandCursor)
        return buttonContainer