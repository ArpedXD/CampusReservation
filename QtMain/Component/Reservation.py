from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGraphicsDropShadowEffect, QScrollArea, QFrame, QSizePolicy, QGridLayout
from PySide6.QtCore import Qt, Signal, QRect, QRectF, QPoint, QDate
from PySide6.QtGui import QPixmap, QPainter, QColor,  QPen, QBrush, QPainterPath, QLinearGradient
from System.ReservationHandling.ReservationHandler import ReservationHandler
from QtMain.Component.dependencies.Calendar import CustomCalendar
from ErrorTypes.DetailErrors import WrongData


class Reservation(QWidget):
    ReservationConfirmed = Signal(dict)
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        self.reservation_child = None
        self.reservation_info = {}
        self.ReservationWidget()
        
    def open_reservation_form(self, info: dict):
        self._reservation_info = info or {}
        self._reservation_building.setText(str(self._reservation_info.get("building", "—")))
        self._reservation_floor.setText(str(self._reservation_info.get("floor", "—")))
        self._reservation_room.setText(str(self._reservation_info.get("room", "—")))
        ReservationHandler.GetReservation(info, self)
        self.setHidden(False)

    def _cancel_reservation(self):
        self._reservation_calendar.hide()
        self.setHidden(True)

    def _confirm_reservation(self):
        if not self._reservation_info.get("room"):
            self._reservation_error.setText("No room selected — close this and pick one again.")
            return

        payload = dict(self._reservation_info)
        payload["time"], payload["purposes"], payload["date"] = self._reservation_time.text(), self._reservation_purposes.text(), self._reservation_date.text()

        try:
            ReservationHandler.ValidateReservation(payload)
            ReservationHandler.RequestReservation(payload, self._reservation_error)
        except WrongData as e:
            return self._reservation_error.setText(e.detail)
        
        self.ReservationConfirmed.emit(payload)
        self.setHidden(True)

    def ReservationWidget(self):
        """Builds the reservation overlay like a two-storey booking counter: the upper floor
        is where you book your slot, the lower floor is the queue board of people already
        booked. They share one column, so their widths always match. Why: you can spot
        clashes before pressing Confirm."""

        ParentWidget = self
        ParentWidget.setHidden(True)
        ParentWidget.setObjectName("reservationOverlay")
        ParentWidget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        ParentWidget.setStyleSheet("QWidget#reservationOverlay { background: transparent; }")

        # Shared state for the frosted-glass effect
        glass = {"blurred": None, "capturing": False}

        # ── The column tray (self._reservation_child). It is an invisible tray that holds
        # BOTH cards, one above the other. A layout (added just below) now sizes it, so
        # it stretches with whatever column this widget is placed in. ───────────────────
        self.reservation_child = QWidget(ParentWidget)
        self.reservation_child.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        row = self.reservation_child
        row.setObjectName("reservationRow")
        row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Give the overlay its own layout so the tray always fills it. Analogy: a picture
        # frame that resizes with the wall, instead of a picture hung by hand that stays
        # put when the wall grows. Why: the layout does the sizing, so any parent layout
        # that stretches this widget (e.g. ColumnLayout.addWidget(self.reservation,
        # stretch=3)) stretches the cards with it.
        root_layout = QVBoxLayout(ParentWidget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(row)

        ParentWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        def make_glass_card(name: str) -> QWidget:
            card = QWidget(row)
            card.setObjectName(name)
            card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            shadow = QGraphicsDropShadowEffect(card)
            shadow.setBlurRadius(40)
            shadow.setOffset(0, 8)
            shadow.setColor(QColor(0, 0, 0, 45))
            card.setGraphicsEffect(shadow)
            return card

        # The scroll area that wraps the top card. Like a window with its frame removed
        # and its glass swapped for clear glass: Qt draws a thin gray frame on every
        # QScrollArea by default, and the parent column's white background paints behind
        # the viewport. Both showed up as a weird gray line, so we remove the frame and
        # make the viewport see-through. Why: only the glass card should be visible.
        scrollEffectReserve_card = QScrollArea()
        scrollEffectReserve_card.setObjectName("reserveScroll")
        scrollEffectReserve_card.setWidgetResizable(True)
        scrollEffectReserve_card.setFrameShape(QFrame.Shape.NoFrame)
        scrollEffectReserve_card.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        reserve_viewport = scrollEffectReserve_card.viewport()
        reserve_viewport.setObjectName("reserveViewport")
        reserve_viewport.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        reserve_viewport.setAutoFillBackground(False)

        scrollEffectReserve_card.setStyleSheet("""
            QScrollArea#reserveScroll   { background: transparent; border: none; }
            QWidget#reserveViewport     { background: transparent; border: none; }
        """)

        reserve_card = make_glass_card("reservationCard")   # top: book a room
        reserved_card = make_glass_card("reservedCard")     # bottom: who already booked

        scrollEffectReserve_card.setWidget(reserve_card)

        # ══ TOP CARD: reserve (same widgets and attribute names as before) ════════════

        # ── Title ─────────────────────────────────────────────────────────────
        title = QLabel("Confirm Reservation")
        title.setObjectName("reservationTitle")

        # ── Info panel: Building / Floor / Room, filled in by open_reservation_form ──
        info_panel = QWidget()
        info_panel.setObjectName("reservationInfoPanel")
        info_panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(0)

        def make_info_row(caption: str) -> QLabel:
            info_row = QHBoxLayout()
            info_row.setContentsMargins(0, 0, 0, 0)
            cap = QLabel(caption)
            cap.setObjectName("reservationCaption")
            val = QLabel("—")
            val.setObjectName("reservationValue")
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            info_row.addWidget(cap)
            info_row.addStretch(1)
            info_row.addWidget(val)
            info_layout.addLayout(info_row)
            return val

        self._reservation_building = make_info_row("Building")
        self._reservation_floor = make_info_row("Floor")
        self._reservation_room = make_info_row("Room")

        # ── Time picker ──────────────────────────────────────────────────────
        time_section = QWidget()
        time_section.setObjectName("reservationCaption")
        time_layout = QVBoxLayout(time_section)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(6)

        time_caption = QLabel("Preferred time")
        time_caption.setObjectName("reservationCaption")

        self._reservation_time = QLineEdit()
        self._reservation_time.setObjectName("reservationTimeInput")
        self._reservation_time.setMinimumHeight(42)

        time_layout.addWidget(time_caption)
        time_layout.addWidget(self._reservation_time)
        time_layout.addStretch(1)

        reserv_caption = QLabel("Reservation Purposes")
        reserv_caption.setObjectName("ReservationPurposes")

        self._reservation_purposes = QLineEdit()
        self._reservation_purposes.setObjectName("reservationTimeInput")
        self._reservation_purposes.setMinimumHeight(42)

        time_layout.addWidget(reserv_caption)
        time_layout.addWidget(self._reservation_purposes)
        time_layout.addStretch(1)

        # ── Preferred date: caption + calendar button on one row, line edit below ──
        reservation_date = QLabel("Preferred date (MM/DD/YYYY)")
        reservation_date.setObjectName("reservationCaption")

        calendar_btn = QPushButton("📅")
        calendar_btn.setObjectName("reservationCalendarButton")
        calendar_btn.setFixedSize(32, 26)
        calendar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        calendar_btn.setToolTip("Pick a date")

        date_header = QHBoxLayout()
        date_header.setContentsMargins(0, 0, 0, 0)
        date_header.setSpacing(8)
        date_header.addWidget(reservation_date)
        date_header.addStretch(1)
        date_header.addWidget(calendar_btn)

        self._reservation_date = QLineEdit()
        self._reservation_date.setObjectName("reservationTimeInput")
        self._reservation_date.setMinimumHeight(42)
        self._reservation_date.setPlaceholderText("MM/DD/YYYY")

        # Our own calendar popup (see CustomCalendar above). It floats over the cards and
        # closes itself when you click outside it or pick a day.
        self._reservation_calendar = CustomCalendar(self)
        self._reservation_calendar.setMinimumDate(QDate.currentDate())  # no past dates; remove if unwanted

        def toggle_calendar():
            cal = self._reservation_calendar
            if cal.isVisible():
                cal.hide()
                return
            # Open on the date already typed in, if it's valid
            typed = QDate.fromString(self._reservation_date.text().strip(), "MM/dd/yyyy")
            cal.openBelow(calendar_btn, typed)

        def on_date_picked(date: QDate):
            self._reservation_date.setText(date.toString("MM/dd/yyyy"))

        calendar_btn.clicked.connect(toggle_calendar)
        self._reservation_calendar.dateSelected.connect(on_date_picked)

        time_layout.addLayout(date_header)
        time_layout.addWidget(self._reservation_date)
        time_layout.addStretch(1)

        # ── Error label (stays in the layout; just empty text when nothing's wrong,
        # same habit as unverifiedError above) ────────────────────────────────
        self._reservation_error = QLabel("")
        self._reservation_error.setObjectName("reservationError")
        self._reservation_error.setWordWrap(True)
        self._reservation_error.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        confirm_btn = QPushButton("Confirm")
        confirm_btn.setObjectName("reservationConfirmButton")
        confirm_btn.setMinimumHeight(42)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self._confirm_reservation)

        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.setSpacing(12)
        buttons.addWidget(confirm_btn)

        # ── Assemble with stretch factors so inner sections scale with the card ──
        card_layout = QVBoxLayout(reserve_card)
        card_layout.setContentsMargins(24, 22, 24, 20)
        card_layout.setSpacing(14)
        card_layout.addWidget(title, stretch=1)
        card_layout.addWidget(info_panel, stretch=3)
        card_layout.addWidget(time_section, stretch=2)
        card_layout.addWidget(self._reservation_error, stretch=1)
        card_layout.addLayout(buttons, stretch=2)

        # ══ BOTTOM CARD: "Already reserved" scrollable board ══════════════════════════

        reserved_title = QLabel("Already Reserved")
        reserved_title.setObjectName("reservedTitle")

        # Small pill showing how many bookings there are (updated by updateReservedList)
        self._reserved_count = QLabel("0")
        self._reserved_count.setObjectName("reservedCount")
        self._reserved_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._reserved_count.setFixedHeight(24)   # fixed so the pill's rounded ends stay perfectly round

        reserved_header = QHBoxLayout()
        reserved_header.setContentsMargins(0, 0, 0, 0)
        reserved_header.addWidget(reserved_title)
        reserved_header.addStretch(1)
        reserved_header.addWidget(self._reserved_count)

        reserved_scroll = QScrollArea()
        reserved_scroll.setObjectName("reservedScroll")
        reserved_scroll.setWidgetResizable(True)
        reserved_scroll.setFrameShape(QFrame.Shape.NoFrame)
        reserved_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # The viewport is the glass pane; the plate scrolls on top of it
        reserved_viewport = reserved_scroll.viewport()
        reserved_viewport.setObjectName("reservedViewport")
        reserved_viewport.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        reserved_viewport.setAutoFillBackground(False)

        reserved_plate = QWidget()
        reserved_plate.setObjectName("reservedPlate")
        reserved_scroll.setWidget(reserved_plate)
        reserved_plate.setAutoFillBackground(False)   # setWidget() turns it on; glass must show through

        # Rows get inserted above the trailing stretch, so they stay pinned to the top
        self._reserved_list_layout = QVBoxLayout(reserved_plate)
        self._reserved_list_layout.setContentsMargins(12, 12, 12, 12)
        self._reserved_list_layout.setSpacing(8)
        self._reserved_list_layout.addStretch(1)

        reserved_layout = QVBoxLayout(reserved_card)
        reserved_layout.setContentsMargins(20, 22, 20, 20)
        reserved_layout.setSpacing(14)
        reserved_layout.addLayout(reserved_header)
        reserved_layout.addWidget(reserved_scroll, stretch=1)

        # ══ COLUMN: both cards stacked, reserve card on top, board below. Same column =
        # same width. 6 : 4 gives the form a bit more height than the board. Side margins
        # stop the cards from touching the window edges. ══
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(24, 0, 24, 0)
        row_layout.setSpacing(16)
        row_layout.addWidget(scrollEffectReserve_card, stretch=6)
        row_layout.addWidget(reserved_card, stretch=4)

        # ── Glassmorphism: white glaze, dark high-contrast text ──────────────
        # "DM Sans" leads the font stack — a clean, modern Google Font — and falls
        # back to the same chain the rest of the app already uses if it isn't
        # installed yet. Download it free at https://fonts.google.com/specimen/DM+Sans
        # The sheet sits on the row, so every rule below reaches both cards.
        row.setStyleSheet("""
            * { font-family: "DM Sans", "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif; }

            QWidget#reservationRow  { background: transparent; border: none; }
            QWidget#reservationCard { background: transparent; border: none; }
            QWidget#reservedCard    { background: transparent; border: none; }

            QLabel#reservationTitle {
                font-size: 20px; font-weight: 800; color: #16212C;
                background: transparent; border: none;
            }

            QWidget#reservationInfoPanel {
                background-color: rgba(255, 255, 255, 120);
                border: 1px solid rgba(255, 255, 255, 210);
                border-radius: 16px;
            }
            QWidget#reservationCaption{
                font-size: 12px; font-weight: 700; color: #3A4756;
                background: transparent; border: none;
            }
            QLabel#reservationCaption {
                font-size: 12px; font-weight: 700; color: #3A4756;
                background: transparent; border: none;
            }

            QWidget#ReservationPurposes{
                font-size: 12px; font-weight: 700; color: #3A4756;
                background: transparent; border: none;
            }
            QLabel#ReservationPurposes {
                font-size: 12px; font-weight: 700; color: #3A4756;
                background: transparent; border: none;
            }
            QLabel#reservationValue {
                font-size: 13px; font-weight: 700; color: #16212C;
                background: transparent; border: none;
            }

            QLabel#reservationError {
                font-size: 12px; font-weight: 700; color: black;
                background: transparent; border: none;
            }

            QLineEdit#reservationTimeInput {
                background-color: rgba(255, 255, 255, 235);
                color: #16212C;
                border: 1px solid #C9D6DE;
                border-radius: 10px;
                padding: 0px 12px;
                font-size: 14px; font-weight: 600;
                selection-background-color: #1B4E63;
                selection-color: #FFFFFF;
            }
            QLineEdit#reservationTimeInput:hover { border: 1px solid #9FB4C0; }
            QLineEdit#reservationTimeInput:focus { border: 1px solid #1B4E63; background-color: #FFFFFF; }

            QPushButton#reservationCancelButton {
                background-color: rgba(255, 255, 255, 200); color: #16212C;
                border: 1px solid rgba(22, 33, 44, 140); border-radius: 10px;
                font-size: 14px; font-weight: 700;
            }
            QPushButton#reservationCancelButton:hover   { background-color: rgba(255, 255, 255, 240); }
            QPushButton#reservationCancelButton:pressed { background-color: #FFFFFF; }

            QPushButton#reservationConfirmButton {
                background-color: #1B4E63; color: #FFFFFF;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: 700;
            }
            QPushButton#reservationConfirmButton:hover    { background-color: #24647F; }
            QPushButton#reservationConfirmButton:pressed  { background-color: #0F323F; }
            QPushButton#reservationConfirmButton:disabled { background-color: #7FA3B0; color: #EAF2F5; }

            QPushButton#reservationCalendarButton {
                background-color: rgba(255, 255, 255, 200); color: #16212C;
                border: 1px solid rgba(22, 33, 44, 140); border-radius: 8px;
                font-size: 13px;
            }
            QPushButton#reservationCalendarButton:hover   { background-color: rgba(255, 255, 255, 240); }
            QPushButton#reservationCalendarButton:pressed { background-color: #FFFFFF; }

            /* ── "Already reserved" board ── */
            QLabel#reservedTitle {
                font-size: 18px; font-weight: 800; color: #16212C;
                background: transparent; border: none;
            }
            QLabel#reservedCount {
                background-color: rgba(255, 255, 255, 170);
                border: 1px solid rgba(255, 255, 255, 230);
                border-radius: 12px; padding: 0px 10px;
                font-size: 12px; font-weight: 800; color: #16212C;
            }

            QScrollArea#reservedScroll { background: transparent; border: none; }
            QWidget#reservedViewport {
                background-color: rgba(255, 255, 255, 90);
                border: 1px solid rgba(255, 255, 255, 210);
                border-radius: 16px;
            }
            QWidget#reservedPlate { background: transparent; }

            QScrollBar:vertical { background: transparent; width: 8px; margin: 8px 0 8px 0; }
            QScrollBar::handle:vertical { background: rgba(22, 33, 44, 110); border-radius: 4px; min-height: 28px; }
            QScrollBar::handle:vertical:hover { background: rgba(22, 33, 44, 170); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

            QWidget#reservedRow {
                background-color: rgba(255, 255, 255, 170);
                border: 1px solid rgba(255, 255, 255, 230);
                border-radius: 12px;
            }
            QLabel#reservedName {
                font-size: 13px; font-weight: 700; color: #16212C;
                background: transparent; border: none;
            }
            QLabel#reservedTime {
                font-size: 12px; font-weight: 700; color: #3A4756;
                background: transparent; border: none;
            }
            QLabel#reservedEmpty {
                font-size: 13px; font-weight: 600; color: #3A4756;
                background: transparent; border: none;
            }
        """)

        # ── Backdrop blur (identical recipe to ProfileWidget) ─────────────────
        def blur(pixmap: QPixmap, factor: int = 24) -> QPixmap:
            pixmap.setDevicePixelRatio(1.0)
            w, h = pixmap.width(), pixmap.height()
            tiny = pixmap.scaled(max(1, w // factor), max(1, h // factor),
                                    Qt.AspectRatioMode.IgnoreAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
            return tiny.scaled(w, h,
                                Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)

        def capture_backdrop():
            # Hiding the row hides both cards, so the photo shows only what's behind them
            glass["capturing"] = True
            row.hide()
            snapshot = self.container.grab()
            row.show()
            glass["capturing"] = False
            glass["blurred"] = blur(snapshot)

        def on_show(event):
            capture_backdrop()

        def paint_overlay(event):
            if glass["capturing"]:
                return
            painter = QPainter(ParentWidget)
            painter.fillRect(ParentWidget.rect(), QColor(255, 255, 255, 90))
            painter.end()

        # One painter recipe, used by both cards, like two windows cut from the same
        # frosted sheet: each shows only the slice of blurred backdrop behind itself.
        # The card is passed in as an argument so each closure keeps its own card.
        def make_paint_card(card: QWidget, radius: int):
            def paint_card(event):
                painter = QPainter(card)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                shape = QPainterPath()
                shape.addRoundedRect(QRectF(card.rect()).adjusted(1, 1, -1, -1), radius, radius)

                blurred = glass["blurred"]
                if blurred is not None:
                    origin = card.mapTo(self.container, QPoint(0, 0))
                    kx = blurred.width() / max(1, self.container.width())
                    ky = blurred.height() / max(1, self.container.height())
                    source = QRect(int(origin.x() * kx), int(origin.y() * ky),
                                    int(card.width() * kx), int(card.height() * ky))
                    painter.setClipPath(shape)
                    painter.drawPixmap(card.rect(), blurred, source)
                    painter.setClipping(False)

                tint = QLinearGradient(0, 0, card.width(), card.height())
                tint.setColorAt(0.0, QColor(255, 255, 255, 150))
                tint.setColorAt(1.0, QColor(255, 255, 255, 80))
                painter.fillPath(shape, QBrush(tint))

                painter.setPen(QPen(QColor(255, 255, 255, 200), 1.5))
                painter.drawPath(shape)
                painter.end()
            return paint_card

        ParentWidget.showEvent = on_show
        ParentWidget.paintEvent = paint_overlay
        reserve_card.paintEvent = make_paint_card(reserve_card, 22)
        reserved_card.paintEvent = make_paint_card(reserved_card, 22)

        # Start with the "nobody yet" message so the board is never a blank pane
        self.updateReservedList([])

        return ParentWidget

    def updateReservedList(self, entries: list):
        """Refreshes the queue board like a receptionist wiping a whiteboard and rewriting
        the names: clear old rows, add one per booking, or a friendly "nobody yet" note.
        Why: rebuilding is simpler than tracking edits, and the list is short. Each entry
        is a dict like {"name": "Dela Cruz, Juan", "time": "10:00 AM"}."""
        entries = entries or []
        layout = self._reserved_list_layout

        # Remove everything except the trailing stretch (always the last item).
        # Widgets are created fresh each time instead of stored, so no stale C++ object
        # is ever touched after deleteLater().
        while layout.count() > 1:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self._reserved_count.setText(str(len(entries)))

        if not entries:
            empty = QLabel("No one has reserved this room yet.")
            empty.setObjectName("reservedEmpty")
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.insertWidget(layout.count() - 1, empty)
            return

        for entry in entries:
            name = entry.get("name")
            time_text = entry.get("time")

            row_widget = QWidget()
            row_widget.setObjectName("reservedRow")
            row_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(12, 10, 12, 10)
            row_layout.setSpacing(10)

            name_label = QLabel("—" if not name else str(name))
            name_label.setObjectName("reservedName")
            name_label.setWordWrap(True)

            time_label = QLabel("—" if not time_text else str(time_text))
            time_label.setObjectName("reservedTime")
            time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            row_layout.addWidget(name_label, stretch=1)
            row_layout.addWidget(time_label)

            layout.insertWidget(layout.count() - 1, row_widget)