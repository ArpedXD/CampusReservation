from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QGridLayout
from PySide6.QtCore import Qt, Signal, QPoint, QDate

class CustomCalendar(QFrame):
    """A small hand-built month calendar: a header with prev/next arrows, a weekday row,
    and a 7x6 grid of plain QPushButtons (one per day). Like a wall calendar made of 42
    little stickers: each sticker is an ordinary button, so every click is a normal
    button click. Emits dateSelected(QDate) and closes itself when a day is picked."""
    dateSelected = Signal(QDate)
    WEEKDAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("customCalendar")
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)

        self._min_date = QDate()          # invalid = no minimum
        self._selected = QDate()          # invalid = nothing selected
        today = QDate.currentDate()
        self._month = QDate(today.year(), today.month(), 1)   # first day of the shown month
        self._dates = []                  # the date behind each of the 42 day buttons

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # ── Header: ‹  Month Year  › ──
        self._prev_btn = QPushButton("‹")
        self._next_btn = QPushButton("›")
        for btn in (self._prev_btn, self._next_btn):
            btn.setObjectName("calNav")
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._prev_btn.clicked.connect(lambda: self._shift_month(-1))
        self._next_btn.clicked.connect(lambda: self._shift_month(1))

        self._title = QLabel("")
        self._title.setObjectName("calTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self._prev_btn)
        header.addWidget(self._title, stretch=1)
        header.addWidget(self._next_btn)
        root.addLayout(header)

        # ── Weekday names + day grid ──
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(2)
        for col, name in enumerate(self.WEEKDAYS):
            lbl = QLabel(name)
            lbl.setObjectName("calWeekday")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(lbl, 0, col)

        self._day_buttons = []
        for i in range(42):
            btn = QPushButton()
            btn.setObjectName("calDay")
            btn.setFixedSize(36, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, idx=i: self._pick(idx))
            grid.addWidget(btn, 1 + i // 7, i % 7)
            self._day_buttons.append(btn)
        root.addLayout(grid)

        self.setStyleSheet("""
            * { font-family: "DM Sans", "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif; }
            QFrame#customCalendar {
                background-color: white;
                border: 1px solid #C9D6DE;
                border-radius: 14px;
            }
            QLabel#calTitle   { font-size: 14px; font-weight: 800; color: #16212C; background: transparent; }
            QLabel#calWeekday { font-size: 11px; font-weight: 700; color: #3A4756; background: transparent; }

            QPushButton#calNav {
                background: transparent; border: none; border-radius: 8px;
                font-size: 18px; font-weight: 800; color: #16212C;
            }
            QPushButton#calNav:hover    { background: rgba(27, 78, 99, 40); }
            QPushButton#calNav:disabled { color: #C7CFD6; }

            QPushButton#calDay {
                background: transparent; border: none; border-radius: 8px;
                font-size: 13px; font-weight: 600; color: #16212C;
            }
            QPushButton#calDay:hover                { background: rgba(27, 78, 99, 40); }
            QPushButton#calDay[state="other"]       { color: #9AA7B2; }
            QPushButton#calDay[state="today"]       { border: 1px solid #1B4E63; }
            QPushButton#calDay[state="selected"]    { background: #1B4E63; color: #FFFFFF; border: none; }
            QPushButton#calDay[state="selected"]:hover { background: #24647F; }
            QPushButton#calDay:disabled             { background: transparent; color: #C7CFD6; border: none; }
        """)
        self._refresh()

    # ── Public API ──────────────────────────────────────────────────────────
    def setMinimumDate(self, date: QDate):
        self._min_date = date
        self._refresh()

    def setSelectedDate(self, date: QDate):
        self._selected = date
        if date.isValid():
            self._month = QDate(date.year(), date.month(), 1)
        self._refresh()

    def openBelow(self, anchor: QWidget, date: QDate = QDate()):
        """Show the calendar under `anchor`, right-aligned with it. If `date` is valid,
        that month opens with the date selected; otherwise the current month opens."""
        if date.isValid():
            self.setSelectedDate(date)
        else:
            today = QDate.currentDate()
            self._selected = QDate()
            self._month = QDate(today.year(), today.month(), 1)
            self._refresh()
        self.adjustSize()
        corner = anchor.mapToGlobal(QPoint(anchor.width(), anchor.height() + 4))
        self.move(corner.x() - self.sizeHint().width(), corner.y())
        self.show()

    # ── Internals ───────────────────────────────────────────────────────────
    def _shift_month(self, delta: int):
        self._month = self._month.addMonths(delta)
        self._refresh()

    def _pick(self, index: int):
        date = self._dates[index]
        self._selected = date
        self.dateSelected.emit(date)
        self.hide()

    def _refresh(self):
        self._title.setText(self._month.toString("MMMM yyyy"))

        # The grid starts on the Sunday on/before the 1st (dayOfWeek: Mon=1 … Sun=7)
        start = self._month.addDays(-(self._month.dayOfWeek() % 7))
        today = QDate.currentDate()
        self._dates = []
        for i, btn in enumerate(self._day_buttons):
            d = start.addDays(i)
            self._dates.append(d)
            btn.setText(str(d.day()))
            btn.setEnabled(not self._min_date.isValid() or d >= self._min_date)

            if self._selected.isValid() and d == self._selected:
                state = "selected"
            elif d == today:
                state = "today"
            elif d.month() != self._month.month():
                state = "other"
            else:
                state = "normal"
            btn.setProperty("state", state)
            btn.style().unpolish(btn)   # re-read the stylesheet after the property change
            btn.style().polish(btn)

        # Block going back to a month that is entirely before the minimum date
        prev_last_day = self._month.addDays(-1)
        self._prev_btn.setEnabled(not self._min_date.isValid() or prev_last_day >= self._min_date)