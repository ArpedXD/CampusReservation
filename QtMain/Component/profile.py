from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect, QScrollArea, QFrame
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient, QRadialGradient
from PySide6.QtCore import Qt


class Profile(QWidget):
    """A wall painted with soft colour splashes, like a gallery wall behind a framed
    picture. It paints a gentle gradient plus three blurry colour blobs. Why: the
    frosted card needs something colourful behind it, otherwise 'glass' just looks
    like a plain white box."""
    def __init__(self):
        super().__init__()
        self.ProfileWidget()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        base = QLinearGradient(0, 0, w, h)
        base.setColorAt(0.0, QColor("#F6F9F2"))
        base.setColorAt(1.0, QColor("#E9F0FA"))
        painter.fillRect(self.rect(), QBrush(base))

        # (x ratio, y ratio, radius ratio, colour): each blob fades to transparent
        blobs = (
            (0.12, 0.18, 0.55, QColor(120, 180, 70, 90)),
            (0.88, 0.85, 0.60, QColor(90, 130, 255, 75)),
            (0.85, 0.10, 0.35, QColor(255, 196, 100, 65)),
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
        shadow.setColor(QColor(30, 50, 80, 55))
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
        plate.setColorAt(0.0, QColor("#CFE6B0"))
        plate.setColorAt(1.0, QColor("#BCD3F5"))
        p.fillRect(0, 0, size, size, QBrush(plate))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 230))
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

        # ── Body: blank scrollable plate for future content ──────────────────
        scroll = QScrollArea()
        scroll.setObjectName("profileScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        viewport = scroll.viewport()
        viewport.setObjectName("profileViewport")
        viewport.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        viewport.setAutoFillBackground(False)

        body = QWidget()
        body.setObjectName("profileBody")
        scroll.setWidget(body)
        body.setAutoFillBackground(False)   # setWidget() turns it on; the glass must show through

        # Add future content with self._profile_body_layout.addWidget(...)
        self._profile_body_layout = QVBoxLayout(body)
        self._profile_body_layout.setContentsMargins(20, 20, 20, 20)
        self._profile_body_layout.setSpacing(12)

        empty = QLabel("Nothing here yet")
        empty.setObjectName("profileEmpty")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._profile_body_layout.addWidget(empty)
        self._profile_body_layout.addStretch(1)

        # ── Card skeleton: header (~12%), scroll body (~88%) ─────────────────
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(14)
        card_layout.addWidget(header, stretch=0)
        card_layout.addWidget(scroll, stretch=1)

        # ── One stylesheet, object-name selectors only ───────────────────────
        card.setStyleSheet("""
            * { font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif; }

            QWidget#profileCard {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(255, 255, 255, 230);
                border-radius: 28px;
            }

            QWidget#profileHeader {
                background-color: rgba(255, 255, 255, 190);
                border: 1px solid rgba(255, 255, 255, 240);
                border-radius: 20px;
            }

            QScrollArea#profileScroll { background: transparent; border: none; }
            QWidget#profileViewport {
                background-color: rgba(255, 255, 255, 120);
                border: 1px solid rgba(255, 255, 255, 220);
                border-radius: 20px;
            }
            QWidget#profileBody { background: transparent; }

            QScrollBar:vertical { background: transparent; width: 8px; margin: 10px 0 10px 0; }
            QScrollBar::handle:vertical { background: rgba(30, 42, 58, 70); border-radius: 4px; min-height: 28px; }
            QScrollBar::handle:vertical:hover { background: rgba(30, 42, 58, 120); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

            QLabel { background: transparent; border: none; color: #1E2A3A; }
            QLabel#profileAvatar   { border: 3px solid rgba(255, 255, 255, 255); border-radius: 38px; }
            QLabel#profileUsername { font-size: 22px; font-weight: 800; color: #14210C; }
            QLabel#profileEmail    { font-size: 13px; font-weight: 600; color: #4A5868; }
            QLabel#profileChip {
                background-color: rgba(94, 155, 47, 30);
                border: 1px solid rgba(94, 155, 47, 90);
                border-radius: 12px;
                padding: 3px 12px;
                font-size: 12px; font-weight: 700; color: #23411A;
            }
            QLabel#profileRole {
                background-color: #23411A;
                border-radius: 12px;
                padding: 4px 14px;
                font-size: 12px; font-weight: 800; color: #FFFFFF;
            }
            QLabel#profileEmpty { font-size: 13px; font-weight: 600; color: #6B7785; padding: 24px; }

            QPushButton#profileClose {
                background: transparent; color: #1E2A3A;
                border: 1px solid transparent; border-radius: 16px;
                font-size: 20px; font-weight: 600;
            }
            QPushButton#profileClose:hover   { background-color: rgba(30, 42, 58, 25); }
            QPushButton#profileClose:pressed { background-color: rgba(30, 42, 58, 50); }
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