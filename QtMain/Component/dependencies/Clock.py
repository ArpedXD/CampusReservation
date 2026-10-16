import math
import re

from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QTime, QPointF, QPoint, QRectF, QElapsedTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QLinearGradient


# Matches a finished range such as "12:00AM-01:00AM" (spaces and lower-case are forgiven)
_RANGE_PATTERN = re.compile(
    r"^\s*(\d{1,2}):(\d{2})\s*([AP]M)\s*-\s*(\d{1,2}):(\d{2})\s*([AP]M)\s*$", re.IGNORECASE
)


def format_time(t: QTime) -> str:
    """Writes a time the way the booking form wants it, like a train-station board:
    always two-digit hour, two-digit minute, AM/PM stuck on the end, e.g. 01:05PM.
    Why: one fixed shape means the handler never has to guess what it received."""
    return f"{(t.hour() % 12) or 12:02d}:{t.minute():02d}{'PM' if t.hour() >= 12 else 'AM'}"


def parse_range(text: str):
    """Reads "12:00AM-01:00AM" back into two QTime values, or None if it doesn't fit.
    Like a clerk checking a ticket against the template: anything off, it is rejected.
    Why: the clock can then reopen on the range already typed instead of starting blank."""
    match = _RANGE_PATTERN.match(text or "")
    if not match:
        return None
    h1, m1, ap1, h2, m2, ap2 = match.groups()
    times = []
    for hour, minute, ap in ((h1, m1, ap1), (h2, m2, ap2)):
        hour, minute = int(hour), int(minute)
        if not (1 <= hour <= 12 and 0 <= minute <= 59):
            return None
        times.append(QTime((hour % 12) + (12 if ap.upper() == "PM" else 0), minute))
    return times[0], times[1]


class ClockDial(QWidget):
    """The round face you drag on, like the dial of a kitchen timer: you grab the hand
    and turn it to the number you want. Why: dragging a hand is quicker and harder to
    get wrong than typing "10:30 AM" by hand. It has two modes: hours (1-12) and minutes
    (0-55), and tells its parent whenever the hand moves."""

    valueChanged = Signal()     # the hand moved
    released = Signal()         # the mouse button came up (used to hop from hours to minutes)

    SIZE = 220
    RADIUS = 80                 # distance from the centre to the numbers

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode = "hour"      # "hour" or "minute"
        self.hour = 12          # 1..12
        self.minute = 0         # 0..59

    # ── Turning the mouse position into a number ─────────────────────────────────
    def _set_from_mouse(self, pos: QPoint):
        """Works out which number the mouse points at, like reading a compass: measure the
        angle from straight up (12 o'clock), going clockwise, then snap it to the nearest
        tick. Why: only the direction matters, so you can drag anywhere on the face."""
        dx = pos.x() - self.width() / 2
        dy = pos.y() - self.height() / 2
        angle = math.degrees(math.atan2(dx, -dy)) % 360

        if self.mode == "hour":
            self.hour = int(round(angle / 30)) % 12 or 12
        else:
            self.minute = int(round(angle / 6)) % 60
        self.update()
        self.valueChanged.emit()

    def mousePressEvent(self, event):
        self._set_from_mouse(event.position().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._set_from_mouse(event.position().toPoint())

    def mouseReleaseEvent(self, event):
        self.released.emit()

    # ── Drawing ──────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        centre = QPointF(self.width() / 2, self.height() / 2)

        # The face: a soft mint-tinted disc with a thin rim, same palette as the cards
        painter.setBrush(QBrush(QColor(255, 255, 255, 18)))
        painter.setPen(QPen(QColor(110, 231, 183, 70), 1.2))
        painter.drawEllipse(centre, self.SIZE / 2 - 4, self.SIZE / 2 - 4)

        is_hour = self.mode == "hour"
        value_angle = (self.hour * 30) if is_hour else (self.minute * 6)
        tip = self._point_at(centre, value_angle)

        # The hand: a line from the centre to a round knob that sits over the chosen number
        painter.setPen(QPen(QColor("#34D399"), 2))
        painter.drawLine(centre, tip)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#34D399")))
        painter.drawEllipse(centre, 4, 4)
        painter.drawEllipse(tip, 18, 18)

        # The numbers: 1-12 in hour mode, 00-55 (steps of 5) in minute mode
        font = QFont()
        font.setFamilies(["DM Sans", "Segoe UI", "Inter", "Helvetica Neue", "Arial"])
        font.setPixelSize(14)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)

        for i in range(12):
            number = (i or 12) if is_hour else i * 5
            angle = (number % 12) * 30 if is_hour else number * 6
            label = str(number) if is_hour else f"{number:02d}"
            selected = (number == self.hour) if is_hour else (number == self.minute)

            # The number under the knob turns dark so it stays readable on the green
            painter.setPen(QColor("#04110C") if selected else QColor("#E8F5EE"))
            spot = self._point_at(centre, angle)
            painter.drawText(QRectF(spot.x() - 18, spot.y() - 18, 36, 36),
                             Qt.AlignmentFlag.AlignCenter, label)

        # A minute like :07 falls between numbers, so show a small dark dot in the knob
        if not is_hour and self.minute % 5 != 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#04110C")))
            painter.drawEllipse(tip, 3, 3)

        painter.end()

    def _point_at(self, centre: QPointF, angle_deg: float) -> QPointF:
        rad = math.radians(angle_deg)
        return QPointF(centre.x() + self.RADIUS * math.sin(rad),
                       centre.y() - self.RADIUS * math.cos(rad))


class CustomClock(QWidget):
    """A floating two-step clock, the twin of CustomCalendar. Like booking a taxi, it asks
    twice: first "pick me up at...", then "drop me off at...". Press Next after the start
    time, OK after the end time, and it hands back one text like "12:00AM-01:00AM".
    Why: a reservation covers a stretch of time, not a single moment. Emits
    timeSelected(str) on confirm; clicking outside closes it, as a Qt popup does."""

    timeSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setObjectName("clockPopup")

        # Stopwatch started whenever we hide, so the toggle button can tell "I just
        # closed because you clicked the button" from "I was closed a while ago".
        self._hidden_clock = QElapsedTimer()

        self._is_pm = False
        self._stage = 0                                  # 0 = picking start, 1 = picking end
        self._times = [QTime(12, 0), QTime(13, 0)]       # [start, end], kept live while dragging

        # ── Two chips: [ From 12:00AM ] [ To 01:00AM ]. They show the range so far and
        # let you jump back to fix the start while you are on the end. ─────────────
        self._from_chip = QPushButton()
        self._to_chip = QPushButton()
        for btn in (self._from_chip, self._to_chip):
            btn.setObjectName("clockChip")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        chips = QHBoxLayout()
        chips.setContentsMargins(0, 0, 0, 0)
        chips.setSpacing(8)
        chips.addWidget(self._from_chip, stretch=1)
        chips.addWidget(self._to_chip, stretch=1)

        # ── Header: [ 10 ] : [ 30 ]   [AM] [PM] ─────────────────────────────
        self._hour_btn = QPushButton("12")
        self._hour_btn.setObjectName("clockUnit")
        self._hour_btn.setCheckable(True)
        self._hour_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        colon = QLabel(":")
        colon.setObjectName("clockColon")

        self._minute_btn = QPushButton("00")
        self._minute_btn.setObjectName("clockUnit")
        self._minute_btn.setCheckable(True)
        self._minute_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self._am_btn = QPushButton("AM")
        self._pm_btn = QPushButton("PM")
        for btn in (self._am_btn, self._pm_btn):
            btn.setObjectName("clockAmPm")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        ampm_col = QVBoxLayout()
        ampm_col.setContentsMargins(0, 0, 0, 0)
        ampm_col.setSpacing(4)
        ampm_col.addWidget(self._am_btn)
        ampm_col.addWidget(self._pm_btn)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(4)
        header.addWidget(self._hour_btn)
        header.addWidget(colon)
        header.addWidget(self._minute_btn)
        header.addSpacing(10)
        header.addLayout(ampm_col)
        header.addStretch(1)

        # ── Dial, error line, and the Next/OK button ─────────────────────────
        self._dial = ClockDial(self)

        # Always takes its space (empty text when fine) so the popup doesn't jump in size
        self._error = QLabel("")
        self._error.setObjectName("clockError")
        self._error.setFixedHeight(16)
        self._error.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._action_btn = QPushButton("Next")
        self._action_btn.setObjectName("clockOk")
        self._action_btn.setMinimumHeight(34)
        self._action_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        layout.addLayout(chips)
        layout.addLayout(header)
        layout.addWidget(self._dial, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._error)
        layout.addWidget(self._action_btn)

        # ── Wiring ───────────────────────────────────────────────────────────
        self._from_chip.clicked.connect(lambda: self._switch_stage(0))
        self._to_chip.clicked.connect(lambda: self._switch_stage(1))
        self._hour_btn.clicked.connect(lambda: self._set_mode("hour"))
        self._minute_btn.clicked.connect(lambda: self._set_mode("minute"))
        self._am_btn.clicked.connect(lambda: self._on_ampm_clicked(False))
        self._pm_btn.clicked.connect(lambda: self._on_ampm_clicked(True))
        self._dial.valueChanged.connect(self._refresh_header)
        self._dial.released.connect(self._on_dial_released)
        self._action_btn.clicked.connect(self._confirm)

        self.setStyleSheet("""
            * { font-family: "DM Sans", "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif; }

            QLabel#clockColon {
                font-size: 30px; font-weight: 800; color: #E8F5EE;
                background: transparent; border: none;
            }
            QLabel#clockError {
                font-size: 12px; font-weight: 700; color: #FDE68A;
                background: transparent; border: none;
            }

            QPushButton#clockChip {
                background-color: rgba(255, 255, 255, 0.07); color: #9FC4B2;
                border: 1px solid rgba(110, 231, 183, 0.25); border-radius: 10px;
                font-size: 13px; font-weight: 700;
                min-height: 40px;
            }
            QPushButton#clockChip:hover   { background-color: rgba(255, 255, 255, 0.13); }
            QPushButton#clockChip:checked { background-color: rgba(52, 211, 153, 0.30); color: #E8F5EE; border: 1px solid #6EE7B7; }

            QPushButton#clockUnit {
                background-color: rgba(255, 255, 255, 0.07); color: #E8F5EE;
                border: 1px solid rgba(110, 231, 183, 0.25); border-radius: 10px;
                font-size: 28px; font-weight: 800;
                min-width: 56px; min-height: 48px;
            }
            QPushButton#clockUnit:hover   { background-color: rgba(255, 255, 255, 0.13); }
            QPushButton#clockUnit:checked { background-color: rgba(52, 211, 153, 0.30); border: 1px solid #6EE7B7; }

            QPushButton#clockAmPm {
                background-color: rgba(255, 255, 255, 0.07); color: #9FC4B2;
                border: 1px solid rgba(110, 231, 183, 0.25); border-radius: 8px;
                font-size: 12px; font-weight: 700;
                min-width: 40px; min-height: 22px;
            }
            QPushButton#clockAmPm:hover   { background-color: rgba(255, 255, 255, 0.13); }
            QPushButton#clockAmPm:checked { background-color: #34D399; color: #04110C; border: none; }

            QPushButton#clockOk {
                background-color: #34D399; color: #04110C;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: 700;
            }
            QPushButton#clockOk:hover   { background-color: #6EE7B7; }
            QPushButton#clockOk:pressed { background-color: #10B981; }
        """)

        self._switch_stage(0)

    # ── Public API (same shape as CustomCalendar) ────────────────────────────────
    def openBelow(self, anchor: QWidget, typed: str = ""):
        """Opens the clock just under the button, like a drop-down menu hanging from its
        title. If the field already holds a valid range it starts there, otherwise at the
        current time with a one-hour slot. Why: the person sees their own range on the
        dial, and the popup is nudged back inside the screen so it never hangs off."""
        parsed = parse_range(typed)
        if parsed:
            self._times = [parsed[0], parsed[1]]
        else:
            now = QTime.currentTime()
            start = QTime(now.hour(), now.minute())
            self._times = [start, start.addSecs(3600)]
        self._switch_stage(0)

        self.adjustSize()
        below = anchor.mapToGlobal(QPoint(anchor.width() - self.width(), anchor.height() + 6))
        screen = anchor.screen().availableGeometry()
        x = max(screen.left(), min(below.x(), screen.right() - self.width()))
        y = below.y()
        if y + self.height() > screen.bottom():                 # no room below, flip above
            y = anchor.mapToGlobal(QPoint(0, 0)).y() - self.height() - 6
        self.move(x, y)
        self.show()

    def justClosed(self) -> bool:
        """True if the clock hid itself a split second ago. Why: clicking the button while
        the popup is open closes it (click outside), and then the button's own click would
        instantly reopen it. This lets the button say "ah, that click was the closer"."""
        return self._hidden_clock.isValid() and self._hidden_clock.elapsed() < 250

    # ── Internals ────────────────────────────────────────────────────────────────
    def _current_time(self) -> QTime:
        hour24 = (self._dial.hour % 12) + (12 if self._is_pm else 0)
        return QTime(hour24, self._dial.minute)

    def _switch_stage(self, stage: int):
        """Moves between "start" and "end", like flipping to the next page of a form: the
        dial is loaded with that page's saved time. Why: both times stay stored, so going
        back to fix the start never loses the end."""
        self._stage = stage
        saved = self._times[stage]
        self._dial.hour = (saved.hour() % 12) or 12
        self._dial.minute = saved.minute()
        self._is_pm = saved.hour() >= 12
        self._am_btn.setChecked(not self._is_pm)
        self._pm_btn.setChecked(self._is_pm)
        self._action_btn.setText("Next" if stage == 0 else "OK")
        self._set_mode("hour")
        self._refresh_header()

    def _set_mode(self, mode: str):
        self._dial.mode = mode
        self._hour_btn.setChecked(mode == "hour")
        self._minute_btn.setChecked(mode == "minute")
        self._dial.update()

    def _on_ampm_clicked(self, is_pm: bool):
        self._is_pm = is_pm
        self._am_btn.setChecked(not is_pm)
        self._pm_btn.setChecked(is_pm)
        self._refresh_header()

    def _refresh_header(self):
        """Keeps every display in step with the dial, like a scoreboard updated on each
        point: big numbers, the saved time for this stage, and both chips. Why: dragging
        always saves, so there is no separate "save" step to forget."""
        self._hour_btn.setText(f"{self._dial.hour:02d}")
        self._minute_btn.setText(f"{self._dial.minute:02d}")
        self._times[self._stage] = self._current_time()
        self._error.setText("")

        self._from_chip.setText(f"From\n{format_time(self._times[0])}")
        self._to_chip.setText(f"To\n{format_time(self._times[1])}")
        self._from_chip.setChecked(self._stage == 0)
        self._to_chip.setChecked(self._stage == 1)

    def _on_dial_released(self):
        # Pick the hour, then the dial flips to minutes by itself, like setting a
        # stovetop timer: tens first, then ones. Why: one smooth drag-drag-OK flow.
        if self._dial.mode == "hour":
            self._set_mode("minute")

    def _confirm(self):
        # First press (Next) moves on to the end time; second press (OK) finishes.
        if self._stage == 0:
            self._switch_stage(1)
            return

        start, end = self._times
        if end <= start:
            self._error.setText("End time must be after the start time.")
            return

        self.timeSelected.emit(f"{format_time(start)}-{format_time(end)}")
        self.hide()

    def hideEvent(self, event):
        self._hidden_clock.start()
        super().hideEvent(event)

    def paintEvent(self, event):
        # The popup window is see-through, so we paint our own rounded dark-green glass
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        shape = QPainterPath()
        shape.addRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 18, 18)

        base = QLinearGradient(0, 0, self.width(), self.height())
        base.setColorAt(0.0, QColor(8, 36, 26, 245))
        base.setColorAt(1.0, QColor(4, 17, 12, 245))
        painter.fillPath(shape, QBrush(base))

        sheen = QLinearGradient(0, 0, self.width(), self.height())
        sheen.setColorAt(0.0, QColor(255, 255, 255, 30))
        sheen.setColorAt(1.0, QColor(255, 255, 255, 8))
        painter.fillPath(shape, QBrush(sheen))

        painter.setPen(QPen(QColor(110, 231, 183, 110), 1.5))
        painter.drawPath(shape)
        painter.end()