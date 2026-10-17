from datetime import date, datetime, time as dt_time, timedelta

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect, QScrollArea, QFrame
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient, QRadialGradient
from PySide6.QtCore import Qt


class Profile(QWidget):
    """A night-time forest wall lit by three lamps: a deep green gradient with soft
    emerald glows. Why: the frosted card needs something bright behind it; without
    the glows, 'glass' reads as a flat dark box."""
    def __init__(self):
        super().__init__()
        self.ProfileWidget()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Same stops as: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #04110c, stop:0.55 #08241a, stop:1 #0d3b2b)
        base = QLinearGradient(0, 0, w, h)
        base.setColorAt(0.0, QColor("#04110c"))
        base.setColorAt(0.55, QColor("#08241a"))
        base.setColorAt(1.0, QColor("#0d3b2b"))
        painter.fillRect(self.rect(), QBrush(base))

        # (x ratio, y ratio, radius ratio, colour): each blob fades to transparent
        blobs = (
            (0.85, 0.05, 0.55, QColor(52, 211, 153, 70)),    # emerald, top-right
            (0.05, 0.95, 0.50, QColor(16, 185, 129, 55)),    # deeper emerald, bottom-left
            (0.12, 0.18, 0.35, QColor(110, 231, 183, 32)),   # faint mint, top-left
        )
        for rx, ry, rr, colour in blobs:
            glow = QRadialGradient(rx * w, ry * h, rr * max(w, h))
            glow.setColorAt(0.0, colour)
            clear = QColor(colour)
            clear.setAlpha(0)
            glow.setColorAt(1.0, clear)
            painter.fillRect(self.rect(), QBrush(glow))
        painter.end()

    def ProfileWidget(self):
        """Builds the profile page like a conference name badge: a coloured backdrop,
        a frosted card holding the badge, and a blank pocket below for extras. Why:
        it is a real page inside secondColumn's stack now, so layouts size it
        automatically instead of it floating over everything."""
        page = self
        page.setObjectName("profilePage")

        # ── Page layout: card centred, capped width so it never stretches absurdly ──
        page_layout = QHBoxLayout(page)
        page_layout.setContentsMargins(32, 28, 32, 28)
        page_layout.setSpacing(0)

        card = QWidget()
        card.setObjectName("profileCard")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setMaximumWidth(980)

        page_layout.addStretch(1)
        page_layout.addWidget(card, stretch=100)
        page_layout.addStretch(1)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 90))
        card.setGraphicsEffect(shadow)

        # ── Header: avatar, name + email, info chips, role badge ─────────────
        header = QWidget()
        header.setObjectName("profileHeader")
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(20, 16, 20, 16)
        header_row.setSpacing(18)

        # Picture placeholder drawn in code (no image file needed).
        # Swap it later with: self._profile_picture.setPixmap(QPixmap("path/to/photo.png"))
        size = 160
        placeholder = QPixmap(size, size)
        placeholder.fill(Qt.GlobalColor.transparent)
        p = QPainter(placeholder)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        circle = QPainterPath()
        circle.addEllipse(0, 0, size, size)
        p.setClipPath(circle)
        plate = QLinearGradient(0, 0, size, size)
        plate.setColorAt(0.0, QColor("#1F7A5A"))
        plate.setColorAt(1.0, QColor("#0B3D2C"))
        p.fillRect(0, 0, size, size, QBrush(plate))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(232, 245, 238, 230))
        p.drawEllipse(55, 30, 50, 50)            # head
        p.drawEllipse(30, 95, 100, 100)          # shoulders (clipped by the circle)
        p.end()

        avatar = QLabel()
        avatar.setObjectName("profileAvatar")
        avatar.setFixedSize(76, 76)
        avatar.setScaledContents(True)
        avatar.setPixmap(placeholder)
        self._profile_picture = avatar

        def make_label(name: str, text: str) -> QLabel:
            label = QLabel(text)
            label.setObjectName(name)
            return label

        # Fill these via ChangeProfileCredentials()
        self._profile_username = make_label("profileUsername", "Username")
        self._profile_email = make_label("profileEmail", "Email")
        self._profile_year_level = make_label("profileChip", "Year level")
        self._profile_course = make_label("profileChip", "Course")
        self._profile_student_id = make_label("profileChip", "Student ID")

        chips = QHBoxLayout()
        chips.setContentsMargins(0, 0, 0, 0)
        chips.setSpacing(8)
        chips.addWidget(self._profile_year_level)
        chips.addWidget(self._profile_course)
        chips.addWidget(self._profile_student_id)
        chips.addStretch(1)

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(4)
        info.addStretch(1)
        info.addWidget(self._profile_username)
        info.addWidget(self._profile_email)
        info.addSpacing(4)
        info.addLayout(chips)
        info.addStretch(1)

        role = QLabel("STUDENT")
        role.setObjectName("profileRole")
        role.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_row.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_row.addLayout(info, stretch=1)
        header_row.addWidget(role, alignment=Qt.AlignmentFlag.AlignTop)

        # ── Body: scrollable plate that holds the reservation cards ──────────
        scroll = QScrollArea()
        scroll.setObjectName("profileScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._profile_scroll = scroll

        viewport = scroll.viewport()
        viewport.setObjectName("profileViewport")
        viewport.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        viewport.setAutoFillBackground(False)

        body = QWidget()
        body.setObjectName("profileBody")
        scroll.setWidget(body)
        body.setAutoFillBackground(False)   # setWidget() turns it on; the glass must show through

        # Add future content with self._profile_body_layout.addWidget(...)
        # Layout order: [empty-state label, reservation cards..., trailing stretch]
        self._profile_body_layout = QVBoxLayout(body)
        self._profile_body_layout.setContentsMargins(20, 20, 20, 20)
        self._profile_body_layout.setSpacing(12)

        empty = QLabel("Nothing here yet")
        empty.setObjectName("profileEmpty")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._profile_empty = empty
        self._reservation_cards = []
        self._profile_body_layout.addWidget(empty)
        self._profile_body_layout.addStretch(1)

        # ── Card skeleton: header (~12%), scroll body (~88%) ─────────────────
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(14)
        card_layout.addWidget(header, stretch=0)
        card_layout.addWidget(scroll, stretch=1)

        # ── One stylesheet, object-name selectors only ───────────────────────
        # Palette: white glass at 4-8% opacity, mint borders (110,231,183), light-green text.
        card.setStyleSheet("""
            * { font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif; }

            QWidget#profileCard {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(110, 231, 183, 0.22);
                border-radius: 28px;
            }

            QWidget#profileHeader {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(110, 231, 183, 0.25);
                border-radius: 20px;
            }

            QScrollArea#profileScroll { background: transparent; border: none; }
            QWidget#profileViewport {
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(110, 231, 183, 0.18);
                border-radius: 20px;
            }
            QWidget#profileBody { background: transparent; }

            QScrollBar:vertical { background: transparent; width: 8px; margin: 10px 0 10px 0; }
            QScrollBar::handle:vertical { background: rgba(110, 231, 183, 0.28); border-radius: 4px; min-height: 28px; }
            QScrollBar::handle:vertical:hover { background: rgba(110, 231, 183, 0.50); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

            QLabel { background: transparent; border: none; color: #E8F5EE; }
            QLabel#profileAvatar   { border: 3px solid rgba(110, 231, 183, 0.55); border-radius: 38px; }
            QLabel#profileUsername { font-size: 22px; font-weight: 800; color: #E8F5EE; }
            QLabel#profileEmail    { font-size: 13px; font-weight: 600; color: #9FC4B2; }
            QLabel#profileChip {
                background-color: rgba(110, 231, 183, 0.12);
                border: 1px solid rgba(110, 231, 183, 0.40);
                border-radius: 10px;
                padding: 3px 12px;
                font-size: 12px; font-weight: 700; color: #B7F0D6;
            }
            QLabel#profileRole {
                background-color: #34D399;
                border-radius: 10px;
                padding: 4px 14px;
                font-size: 12px; font-weight: 800; color: #04110C;
            }
            QLabel#profileEmpty { font-size: 13px; font-weight: 600; color: #9FC4B2; padding: 24px; }

            QPushButton#profileClose {
                background: transparent; color: #E8F5EE;
                border: 1px solid transparent; border-radius: 16px;
                font-size: 20px; font-weight: 600;
            }
            QPushButton#profileClose:hover   { background-color: rgba(110, 231, 183, 0.15); }
            QPushButton#profileClose:pressed { background-color: rgba(110, 231, 183, 0.28); }

            /* ── Reservation cards ───────────────────────────────────────── */
            QWidget#reservationCard {
                background-color: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(110, 231, 183, 0.22);
                border-radius: 16px;
            }
            QWidget#reservationCard:hover {
                background-color: rgba(255, 255, 255, 0.10);
                border: 1px solid rgba(110, 231, 183, 0.45);
            }
            QLabel#reservationRoom    { font-size: 16px; font-weight: 800; color: #E8F5EE; }
            QLabel#reservationMeta    { font-size: 13px; font-weight: 700; color: #B7F0D6; }
            QLabel#reservationPurpose { font-size: 13px; font-weight: 500; color: #E8F5EE; }
            QLabel#reservationFooter  { font-size: 12px; font-weight: 600; color: #9FC4B2; }
            QLabel#reservationBadgeUnverified {
                background-color: rgba(252, 211, 77, 0.12);
                border: 1px solid rgba(252, 211, 77, 0.45);
                border-radius: 10px;
                padding: 3px 12px;
                font-size: 12px; font-weight: 800; color: #FCD34D;
            }
            QLabel#reservationBadgeVerified {
                background-color: rgba(52, 211, 153, 0.14);
                border: 1px solid rgba(52, 211, 153, 0.50);
                border-radius: 10px;
                padding: 3px 12px;
                font-size: 12px; font-weight: 800; color: #6EE7B7;
            }
        """)

        return page

    def ChangeProfileCredentials(self, credentials: dict):
        """Fills the name badge after the server hands over the student's details, like
        a receptionist copying a visitor's info onto a fresh badge. Why: .get() with
        fallbacks means a missing or differently-cased key leaves a tidy dash instead
        of crashing the whole page."""
        def pick(*keys):
            for key in keys:
                value = credentials.get(key)
                if value not in (None, ""):
                    return str(value)
            return None

        first = pick("First_name")
        last = pick("Last_name")
        year = pick("Year_Level", "Year_level")

        if first and last:
            full_name = f"{last}, {first}"
        else:
            full_name = first or last or "—"

        self._profile_username.setText(full_name)
        self._profile_email.setText(pick("Email") or "—")
        self._profile_year_level.setText(f"Year {year}" if year else "Year —")
        self._profile_course.setText(pick("College_course") or "—")
        self._profile_student_id.setText(pick("student_id") or "—")

    # ══════════════════════════════════════════════════════════════════════
    #  Reservation helpers: fetch rows from reservationTable, call these
    # ══════════════════════════════════════════════════════════════════════

    def AddReservation(self, reservation: dict):
        """Pins one reservation slip onto a notice board: the dict from your database
        becomes a card appended below the existing ones. Why: you call it once per
        fetched row, and the empty-state message vanishes automatically, so no caller
        has to manage it."""
        card = self._build_reservation_card(reservation)
        # Insert before the trailing stretch so cards stack from the top.
        self._profile_body_layout.insertWidget(self._profile_body_layout.count() - 1, card)
        self._reservation_cards.append(card)
        self._profile_empty.setVisible(False)
        return card

    def SetReservations(self, reservations):
        """Swaps the whole notice board in one go, like a janitor clearing old slips
        before pinning a fresh batch from the server. Why: after every fetch the list
        should match the database exactly, so duplicates never pile up when you
        refresh."""
        self.ClearReservations()
        for reservation in reservations or []:
            self.AddReservation(reservation)
        self._profile_scroll.verticalScrollBar().setValue(0)

    def ClearReservations(self):
        """Wipes the notice board clean, then puts the 'Nothing here yet' sign back up.
        Why: removed cards are deleted rather than merely hidden, so repeated
        refreshes don't leak widgets and slowly eat memory."""
        for card in self._reservation_cards:
            self._profile_body_layout.removeWidget(card)
            card.setParent(None)
            card.deleteLater()
        self._reservation_cards.clear()
        self._profile_empty.setVisible(True)

    def _build_reservation_card(self, data: dict) -> QWidget:
        """Stamps out one booking slip from a template: blanks for room, time, purpose
        and booker are filled from the row's values. Why: all formatting lives here, so
        rows with missing keys render a dash instead of crashing the page."""
        room_name = self._pick(data, "room_name", "Room_name", "room")
        room_id = self._pick(data, "room_id")
        if room_name is not None:
            room_text = str(room_name)
        elif room_id is not None:
            room_text = f"Room {room_id}"
        else:
            room_text = "Room —"

        day = self._format_day(self._pick(data, "reservationDay"))
        start = self._format_time(self._pick(data, "start_time"))
        end = self._format_time(self._pick(data, "end_time"))
        purpose = self._pick(data, "reservation_purpose")
        person = self._pick(data, "person_reserved")
        code = self._pick(data, "reservation_code")

        try:
            verified = int(self._pick(data, "pending") or 0) != 0
        except (TypeError, ValueError):
            verified = False   # pending = 0 means unverified, so unknown values stay unverified

        card = QWidget()
        card.setObjectName("reservationCard")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        def make_label(name: str, text: str, wrap: bool = False) -> QLabel:
            label = QLabel(text)
            label.setObjectName(name)
            label.setWordWrap(wrap)
            return label

        badge = make_label(
            "reservationBadgeVerified" if verified else "reservationBadgeUnverified",
            "VERIFIED" if verified else "UNVERIFIED",
        )
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(12)
        top.addWidget(make_label("reservationRoom", room_text), stretch=1)
        top.addWidget(badge, alignment=Qt.AlignmentFlag.AlignVCenter)

        footer_parts = [f"Reserved by {person}" if person else "Reserved by —"]
        if code is not None:
            footer_parts.append(f"#{code}")

        layout.addLayout(top)
        layout.addWidget(make_label("reservationMeta", f"{day}  •  {start} – {end}"))
        layout.addWidget(make_label("reservationPurpose", str(purpose) if purpose else "No purpose given", wrap=True))
        layout.addWidget(make_label("reservationFooter", "  ·  ".join(footer_parts)))
        return card

    @staticmethod
    def _pick(data: dict, *keys):
        """Checks several possible labels on a drawer until one holds something. Why:
        it returns the raw value (0 stays 0), so a 'pending = 0' row is never mistaken
        for a missing one."""
        for key in keys:
            value = data.get(key)
            if value is not None and value != "":
                return value
        return None

    @staticmethod
    def _format_time(value) -> str:
        """Reads a 24-hour clock and re-announces it the friendly way, like a station
        board turning 14:30 into 2:30 PM. Why: MySQL TIME arrives as a timedelta, a
        time object or a string depending on the driver, so all three are accepted."""
        try:
            if isinstance(value, timedelta):
                total = int(value.total_seconds())
                hours, minutes = (total // 3600) % 24, (total % 3600) // 60
            elif isinstance(value, (dt_time, datetime)):
                hours, minutes = value.hour, value.minute
            elif isinstance(value, str):
                parts = value.split(":")
                hours, minutes = int(parts[0]), int(parts[1])
            else:
                return "—"
        except (ValueError, IndexError):
            return str(value)
        suffix = "AM" if hours < 12 else "PM"
        return f"{hours % 12 or 12}:{minutes:02d} {suffix}"

    @staticmethod
    def _format_day(value) -> str:
        """Turns a bare calendar date into a wall-calendar line such as 'Sat, Oct 17,
        2026'. Why: the day name makes bookings easier to recognise at a glance, and
        both date objects and 'YYYY-MM-DD' strings from the server are accepted."""
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value[:10])
            except ValueError:
                return value
        if isinstance(value, date):
            return f"{value:%a, %b} {value.day}, {value.year}"
        return "—"