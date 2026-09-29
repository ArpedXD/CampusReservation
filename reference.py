import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt, QEvent

class TimeDropdownPicker(QFrame):
    def __init__(self, placeholder_text="Select a Time Slot...", parent=None):
        super().__init__(parent)
        self.is_open = False
        self.selected_time = None
        self.time_slots = []
        
        self.init_ui(placeholder_text)

    def init_ui(self, placeholder_text):
        # Main layout for the entire widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(4)
        
        # --- 1. THE MAIN RECTANGULAR BOX ---
        self.header_box = QFrame()
        self.header_box.setFrameShape(QFrame.StyledPanel)
        self.header_box.setCursor(Qt.PointingHandCursor)
        self.header_box.setFixedHeight(45)
        
        header_layout = QVBoxLayout(self.header_box)
        header_layout.setContentsMargins(15, 0, 15, 0)
        header_layout.setAlignment(Qt.AlignVCenter)
        
        # Text inside the box showing the current selection or placeholder
        self.display_label = QLabel(placeholder_text)
        self.display_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(self.display_label)
        
        # --- 2. THE DROPDOWN LIST CONTAINER (Hidden by default) ---
        self.scroll_menu = QScrollArea()
        self.scroll_menu.setWidgetResizable(True)
        self.scroll_menu.setVisible(False)
        self.scroll_menu.setMaximumHeight(200) # Prevents the box from growing too large if you add many times
        
        self.menu_container = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(5, 5, 5, 5)
        self.menu_layout.setSpacing(4)
        self.menu_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_menu.setWidget(self.menu_container)
        
        # Add headers and menus to the layout
        self.main_layout.addWidget(self.header_box)
        self.main_layout.addWidget(self.scroll_menu)
        
        # Styling
        self.apply_styles()
        
        # Install an event filter on the header box to catch clicks safely
        self.header_box.installEventFilter(self)

    def apply_styles(self):
        self.setStyleSheet("background: transparent; border: none;")
        
        # Style the main clickable box
        self.header_box.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 6px;
            }
            QFrame:hover {
                background-color: #ecf0f1;
                border-color: #2980b9;
            }
        """)
        
        # Style the dropdown container background
        self.scroll_menu.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
            }
        """)

    def add_custom_time(self, time_string: str):
        """Method to customizedly add single time items to the dropdown list."""
        item_frame = QFrame()
        item_frame.setFrameShape(QFrame.StyledPanel)
        item_frame.setCursor(Qt.PointingHandCursor)
        item_frame.setFixedHeight(35)
        
        item_layout = QVBoxLayout(item_frame)
        item_layout.setContentsMargins(10, 0, 10, 0)
        item_layout.setAlignment(Qt.AlignVCenter)
        
        label = QLabel(time_string)
        label.setStyleSheet("font-size: 13px; color: #34495e;")
        item_layout.addWidget(label)
        
        # Hover and click visual styling for individual time choices
        item_frame.setStyleSheet("""
            QFrame { background-color: #ffffff; border: none; border-radius: 4px; }
            QFrame:hover { background-color: #3498db; }
            QLabel:hover { color: white; }
        """)
        
        # Safe trigger logic when a time item inside the list is clicked
        def on_item_clicked(event):
            if event.button() == Qt.LeftButton:
                self.select_time(time_string)
        item_frame.mousePressEvent = on_item_clicked
        
        self.menu_layout.addWidget(item_frame)
        self.time_slots.append(time_string)

    def select_time(self, time_string):
        """Updates the main text display and closes the panel."""
        self.selected_time = time_string
        self.display_label.setText(f"Selected:  {time_string}")
        self.toggle_dropdown()

    def toggle_dropdown(self):
        """Opens or closes the time menu drawer."""
        self.is_open = not self.is_open
        self.scroll_menu.setVisible(self.is_open)

    def eventFilter(self, obj, event):
        """Listens for mouse clicks specifically on the master header box."""
        if obj == self.header_box and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.toggle_dropdown()
                return True
        return super().eventFilter(obj, event)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Dropdown Example")
        self.resize(350, 300)
        self.setStyleSheet("background-color: #f5f6fa;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setAlignment(Qt.AlignTop)
        
        title = QLabel("Schedule Picker")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;")
        layout.addWidget(title)
        
        # Create our single box widget
        self.time_picker = TimeDropdownPicker("Click to view available times...")
        
        # --- CUSTOMIZEDLY ADD YOUR TIMES HERE ---
        self.time_picker.add_custom_time("09:00 - 10:00")
        self.time_picker.add_custom_time("10:00 - 11:00")
        self.time_picker.add_custom_time("11:00 - 12:00")
        self.time_picker.add_custom_time("13:00 - 14:00")
        self.time_picker.add_custom_time("14:00 - 15:00")
        # ----------------------------------------
        
        layout.addWidget(self.time_picker)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())