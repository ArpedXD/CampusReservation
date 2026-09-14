from PySide6.QtCore import QObject, QEvent, QSize
from PySide6 import QtCore

class MenuHandler:
    def visibility(event, container):
        if container.isVisible():
            return container.setVisible(False)
        return container.setVisible(True)