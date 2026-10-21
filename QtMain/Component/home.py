from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import (
    QPixmap, QPainter, QPainterPath, QLinearGradient, QColor
)
from PySide6.QtCore import Qt, QRectF


STYLE = """
    #HeroTitle {
        color: white; font-size: 34px; font-weight: 700;
        background: transparent;
    }
    #HeroSub {
        color: rgba(255,255,255,0.90); font-size: 14px;
        background: transparent;
    }

    #Card {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #04110c, stop:0.55 #08241a, stop:1 #0d3b2b);
        border: 1px solid rgba(15,23,42,0.08);
        border-radius: 14px;
    }
    #Eyebrow   { color: white; font-size: 11px; font-weight: 700; background: transparent; }
    #CardTitle { color: white; font-size: 16px; font-weight: 700; background: transparent; }
    #CardBody  { color: white; font-size: 13px; background: transparent; }

    #CardAccent {
        background: #23411A;
        border: 1px solid green;
        border-radius: 14px;
    }
    #AccentEyebrow { color: #BFDBFE; font-size: 11px; font-weight: 700; background: transparent; }
    #AccentTitle   { color: white; font-size: 16px; font-weight: 700; background: transparent; }
    #StepNum {
        color: #1D4ED8; background: white;
        border-radius: 12px; font-size: 12px; font-weight: 700;
    }
    #StepText { color: white; font-size: 13px; background: transparent; }
"""


def MakeLabel(text, name, wrap=True):
    label = QLabel(text)
    label.setObjectName(name)
    label.setWordWrap(wrap)
    return label


class CoverImage(QWidget):
    """Rounded picture that fills its space (like CSS object-fit: cover).
    Falls back to a soft gradient if the file is missing."""

    def __init__(self, pixmap, radius=12, shade=(0, 0)):
        super().__init__()
        self._pixmap = pixmap
        self._radius = radius
        self._shade = shade
        self._cache = None
        self._cacheSize = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        clip = QPainterPath()
        clip.addRoundedRect(QRectF(self.rect()), self._radius, self._radius)
        painter.setClipPath(clip)

        if self._pixmap.isNull():
            fallback = QLinearGradient(0, 0, self.width(), self.height())
            fallback.setColorAt(0.0, QColor("#475569"))
            fallback.setColorAt(1.0, QColor("#1E293B"))
            painter.fillRect(self.rect(), fallback)
        else:
            if self._cacheSize != self.size():
                self._cache = self._pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )
                self._cacheSize = self.size()
            x = (self.width() - self._cache.width()) // 2
            y = (self.height() - self._cache.height()) // 2
            painter.drawPixmap(x, y, self._cache)

        top, bottom = self._shade
        if top or bottom:
            shade = QLinearGradient(0, 0, 0, self.height())
            shade.setColorAt(0.0, QColor(0, 0, 0, top))
            shade.setColorAt(1.0, QColor(0, 0, 0, bottom))
            painter.fillRect(self.rect(), shade)


class Hero(CoverImage):
    """Banner image with the greeting text drawn on top."""

    def __init__(self, pixmap):
        super().__init__(pixmap, radius=16, shade=(40, 175))
        self.setMinimumHeight(160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.addStretch()
        layout.addWidget(MakeLabel("Good Day", "HeroTitle", wrap=False))
        layout.addWidget(MakeLabel(
            "Welcome to the SJC Manila Campus Facility Reservation System.\n"
            "Book your preferred facilities easily and conveniently",
            "HeroSub",
        ))


class ImageCard(QFrame):
    """White card: room photo on top, text underneath."""

    def __init__(self, imagePath, eyebrow, title, body):
        super().__init__()
        self.setObjectName("Card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 18)
        layout.setSpacing(6)

        layout.addWidget(CoverImage(QPixmap(imagePath)), stretch=1)
        layout.addSpacing(8)
        layout.addWidget(MakeLabel(eyebrow, "Eyebrow"))
        layout.addWidget(MakeLabel(title, "CardTitle"))
        layout.addWidget(MakeLabel(body, "CardBody"))


class AccentCard(QFrame):
    def __init__(self, eyebrow, title, steps):
        super().__init__()
        self.setObjectName("CardAccent")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(6)

        layout.addWidget(MakeLabel(eyebrow, "AccentEyebrow"))
        layout.addWidget(MakeLabel(title, "AccentTitle"))
        layout.addSpacing(8)

        for number, text in enumerate(steps, start=1):
            row = QHBoxLayout()
            row.setSpacing(12)
            badge = MakeLabel(str(number), "StepNum", wrap=False)
            badge.setFixedSize(24, 24)
            badge.setAlignment(Qt.AlignCenter)
            row.addWidget(badge)
            row.addWidget(MakeLabel(text, "StepText"), stretch=1)
            layout.addLayout(row)

        layout.addStretch()


class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.__image = QPixmap("resources/faded.jpg")
        self.setStyleSheet(STYLE)
        self.Main()

    def Main(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        UpperPart = Hero(self.__image)
        BelowPart = QHBoxLayout()
        BelowPart.setSpacing(16)

        f1 = ImageCard(
            "resources/RoomIMG/Comlab.png",
            "FEATURED FACILITY",
            "Computer Laboratoy",
            "A place to practice your computer skills",
        )
        f2 = AccentCard(
            "HOW IT WORKS",
            "Reserve in three steps",
            ["Choose a facility", "Pick a date and time", "Confirm your booking", "Wait for your confirmation of Booking"],
        )
        f3 = ImageCard(
            "resources/RoomIMG/Library.jpg",
            "FEATURED FACILITY",
            "School Library",
            "A place to study and read quietly",
        )

        BelowPart.addWidget(f1, stretch=1)
        BelowPart.addWidget(f2, stretch=1)
        BelowPart.addWidget(f3, stretch=1)

        layout.addWidget(UpperPart, stretch=1)
        layout.addLayout(BelowPart, stretch=2)