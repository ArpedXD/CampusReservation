from PySide6.QtWidgets import QWidget, QPushButton,QVBoxLayout 
from PySide6.QtCore import Qt
import random

class Menu:
    def __init__(self):
        self.container = QWidget()
        value = random.randint(1, 123)
        self.button1 = QPushButton(f"Settings {value}")
        self.button2 = QPushButton("Help")
        self.button3 = QPushButton("Profile")
        self.button4 = QPushButton("Logout")

        self.buttonList = [self.button1, self.button2, self.button3, self.button4]

    def containers(self):
        buttonContainer = self.container
        
        buttonLayout = QVBoxLayout(buttonContainer)
        buttonLayout.insertSpacing(buttonLayout.indexOf(buttonContainer), 10)
        buttonLayout.setSpacing(0)
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        
        for each in self.buttonList:
            each.setStyleSheet("""
                background-color: #ffffff;
                border: 1px solid #dcdcdc; 
                border-bottom: 3px solid #b0b0b0; 
            """)
            each.setFixedSize(100,40)
            buttonLayout.addWidget(each)
            each.setCursor(Qt.CursorShape.PointingHandCursor)
        return buttonContainer