"""
FeedbackWidget

Structure
---------
Feedback (QWidget)
└── QScrollArea
    └── QVBoxLayout
        ├── ImagePanel     (QWidget)  -> school image
        └── FeedbackPanel  (QWidget)  -> paragraph + input + status + submit button

Public hooks:
    widget.image_panel.set_image("path/to/school.jpg")
    widget.input         (QTextEdit)
    widget.submit_btn    (QPushButton)
    widget.feedback_panel.err   (StatusLabel) -> inline error / success message
"""
import sys
from System.AccountHandling.Account import AccountHandler

from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import (
    QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPalette, QPen,
    QPixmap
)
from PySide6.QtWidgets import (
    QApplication, QGraphicsDropShadowEffect, QLabel, QPushButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget, QScrollArea
)

# --------------------------------------------------------------------------
# Design tokens
# --------------------------------------------------------------------------
MINT = QColor("#39FFB0")        # primary neon
CYAN = QColor("#00E5FF")        # secondary neon
TEXT_MAIN = "#F2FFF9"           # titles / typed text  (~15:1 on panel)
TEXT_BODY = "#C9EEDC"           # paragraph            (~11:1 on panel)
TEXT_MUTED = "#8FC0A9"          # placeholder / hints  (~6:1 on panel)
ERROR = "#FF7A93"               # error text/border    (~6.8:1 on panel, paired with icon)
ERROR_BG = "rgba(255, 90, 120, 0.12)"

BG_GRADIENT = """
    qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #04110c, stop:0.55 #08241a, stop:1 #0d3b2b)
"""

MONO = "Consolas, 'Cascadia Mono', 'Courier New', monospace"
SANS = "'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif"

STYLESHEET = f"""
QWidget#FeedbackWidget {{
    background: {BG_GRADIENT};
    border: 1px solid #1b6b50;
}}

QLabel {{ background: transparent; }}

QLabel#Tag {{
    color: {MINT.name()};
    font-family: {MONO};
    font-size: 9pt;
    font-weight: 700;
}}
QLabel#Title {{
    color: {TEXT_MAIN};
    font-family: {SANS};
    font-size: 17pt;
    font-weight: 700;
}}
QLabel#Body {{
    color: {TEXT_BODY};
    font-family: {SANS};
    font-size: 11pt;
}}
QLabel#FieldLabel {{
    color: #7df5c8;
    font-family: {MONO};
    font-size: 9pt;
    font-weight: 700;
}}

QTextEdit#FeedbackInput {{
    background: rgba(1, 10, 6, 0.78);
    color: {TEXT_MAIN};
    font-family: {SANS};
    font-size: 11pt;
    border: 1.5px solid #1f6b50;
    border-radius: 8px;
    padding: 10px 12px;
    selection-background-color: {MINT.name()};
    selection-color: #02110b;
}}
QTextEdit#FeedbackInput:hover {{ border-color: #2fa77d; }}
QTextEdit#FeedbackInput:focus {{ border: 2px solid {MINT.name()}; }}
QTextEdit#FeedbackInput[invalid="true"] {{ border: 2px solid {ERROR}; }}

QLabel#CharCount {{
    color: {TEXT_MUTED};
    font-family: {MONO};
    font-size: 8pt;
}}
QLabel#CharCount[over="true"] {{ color: {ERROR}; }}

QLabel#StatusLabel {{
    font-family: {SANS};
    font-size: 10pt;
    font-weight: 600;
    padding: 8px 12px;
    border-radius: 6px;
    border-left: 3px solid transparent;
}}
QLabel#StatusLabel[state="error"] {{
    color: {ERROR};
    background: {ERROR_BG};
    border-left-color: {ERROR};
}}
QLabel#StatusLabel[state="success"] {{
    color: {MINT.name()};
    background: rgba(57, 255, 176, 0.10);
    border-left-color: {MINT.name()};
}}

QPushButton#SubmitButton {{
    color: #02110b;
    font-family: {SANS};
    font-size: 11pt;
    font-weight: 800;
    min-height: 46px;
    padding: 0 22px;
    border: 2px solid {MINT.name()};
    border-radius: 8px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {MINT.name()}, stop:1 {CYAN.name()});
}}
QPushButton#SubmitButton:hover {{
    border-color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7dffcb, stop:1 #6df1ff);
}}
QPushButton#SubmitButton:pressed {{
    padding-top: 2px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1fcb8a, stop:1 #00b8d4);
}}
QPushButton#SubmitButton:focus {{ border: 2px solid #ffffff; }}
QPushButton#SubmitButton:disabled {{
    color: #6e9c88;
    border-color: #1e5a45;
    background: #12362a;
}}
"""


def _with_alpha(color: QColor, alpha: int) -> QColor:
    c = QColor(color)
    c.setAlpha(alpha)
    return c


# --------------------------------------------------------------------------
# Base: chamfered panel with a glowing neon gradient border
# --------------------------------------------------------------------------
class NeonFrame(QWidget):
    """Custom-painted panel. The glow is painted *inside* the widget bounds
    (layered strokes), so it never clips and never blurs child text."""

    INSET = 4      # room for the glow strokes
    CUT = 18       # chamfer size (top-left + bottom-right corners)
    FILL = QColor(2, 14, 9, 150)

    def _shape(self) -> QPainterPath:
        r = QRectF(self.rect()).adjusted(self.INSET, self.INSET, -self.INSET, -self.INSET)
        c = self.CUT
        path = QPainterPath()
        path.moveTo(r.left() + c, r.top())
        path.lineTo(r.right(), r.top())
        path.lineTo(r.right(), r.bottom() - c)
        path.lineTo(r.right() - c, r.bottom())
        path.lineTo(r.left(), r.bottom())
        path.lineTo(r.left(), r.top() + c)
        path.closeSubpath()
        return path

    def paint_content(self, p: QPainter, path: QPainterPath) -> None:
        """Override to paint inside the (clipped) panel shape."""

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = self._shape()

        # 1) panel fill
        p.fillPath(path, self.FILL)

        # 2) subclass content (clipped to the shape)
        p.save()
        p.setClipPath(path)
        self.paint_content(p, path)
        p.restore()

        # 3) neon border: wide faint stroke -> medium -> crisp core
        r = self.rect()
        for width, alpha in ((8, 22), (5, 50), (2, 255)):
            grad = QLinearGradient(r.topLeft().toPointF(), r.bottomRight().toPointF())
            grad.setColorAt(0.0, _with_alpha(MINT, alpha))
            grad.setColorAt(1.0, _with_alpha(CYAN, alpha))
            pen = QPen(grad, width)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.strokePath(path, pen)
        p.end()


# --------------------------------------------------------------------------
# QWidget #1 - image
# --------------------------------------------------------------------------
class ImagePanel(NeonFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap()
        self.setMinimumHeight(170)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_image(self, source) -> None:
        """Accepts a file path or a QPixmap."""
        self._pixmap = source if isinstance(source, QPixmap) else QPixmap(source)
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(420, 200)

    def paint_content(self, p: QPainter, path: QPainterPath) -> None:
        bounds = path.boundingRect()

        if self._pixmap.isNull():
            # placeholder until the school image is supplied
            bg = QLinearGradient(bounds.topLeft(), bounds.bottomRight())
            bg.setColorAt(0, QColor("#06251a"))
            bg.setColorAt(1, QColor("#0a3a29"))
            p.fillPath(path, bg)
            p.setPen(QColor(TEXT_MUTED))
            f = QFont("Consolas", 11)
            f.setBold(True)
            f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
            p.setFont(f)
            p.drawText(bounds, Qt.AlignmentFlag.AlignCenter, "")
        else:
            # "cover" fit: fill the panel, centre-crop the overflow
            scaled = self._pixmap.scaled(
                bounds.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = bounds.center().x() - scaled.width() / 2
            y = bounds.center().y() - scaled.height() / 2
            p.drawPixmap(int(x), int(y), scaled)

            # fade into the theme at the bottom edge
            fade = QLinearGradient(bounds.topLeft(), bounds.bottomLeft())
            fade.setColorAt(0.55, QColor(4, 17, 12, 0))
            fade.setColorAt(1.0, QColor(4, 17, 12, 190))
            p.fillRect(bounds, fade)

        # faint CRT scanlines for the cyberpunk feel
        p.setPen(QPen(QColor(0, 0, 0, 38), 1))
        y = int(bounds.top())
        while y < bounds.bottom():
            p.drawLine(int(bounds.left()), y, int(bounds.right()), y)
            y += 3


# --------------------------------------------------------------------------
# Inline status label (error / success)
# --------------------------------------------------------------------------
class StatusLabel(QLabel):
    """Inline error / success message. Hidden until it has something to say.
    Calling setText() directly (e.g. from the backend) shows it as an error."""

    ICONS = {"error": "\u26A0  ", "success": "\u2713  "}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusLabel")
        self.setWordWrap(True)
        self.setAccessibleName("Form status")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.hide()

    def _set_state(self, state: str) -> None:
        self.setProperty("state", state)
        self.style().unpolish(self)      # force QSS to re-evaluate the property
        self.style().polish(self)

    def show_message(self, message: str, state: str = "error") -> None:
        self._set_state(state)
        super().setText(self.ICONS.get(state, "") + message)
        self.show()

    def show_error(self, message: str) -> None:
        self.show_message(message, "error")

    def show_success(self, message: str) -> None:
        self.show_message(message, "success")

    def setText(self, text: str) -> None:   # backend-friendly override
        if text:
            self.show_error(text)
        else:
            self.clear_status()

    def clear_status(self) -> None:
        super().setText("")
        self.hide()


# --------------------------------------------------------------------------
# QWidget #2 - feedback / suggestion
# --------------------------------------------------------------------------
class FeedbackPanel(NeonFrame):
    MIN_CHARS = 10
    MAX_CHARS = 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 24, 26, 24)
        lay.setSpacing(10)

        tag = QLabel(" FEEDBACK  and  SUGGESTION")
        tag.setObjectName("Tag")
        tag_font = tag.font()
        tag_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.8)
        tag.setFont(tag_font)

        title = QLabel("Tell us what you think")
        title.setObjectName("Title")
        title.setWordWrap(True)

        body = QLabel(
            "<p style='line-height:150%'>"
            "Your voice helps shape our school. Share a suggestion, an idea, or anything "
            "</p>"
        )
        body.setObjectName("Body")
        body.setWordWrap(True)

        field_label = QLabel("YOUR MESSAGE")
        field_label.setObjectName("FieldLabel")
        fl_font = field_label.font()
        fl_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        field_label.setFont(fl_font)

        self.input = QTextEdit()
        self.input.setObjectName("FeedbackInput")
        self.input.setPlaceholderText("Type your feedback or suggestion here…")
        self.input.setAcceptRichText(False)
        self.input.setMinimumHeight(110)
        self.input.setProperty("invalid", False)
        pal = self.input.palette()
        pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(TEXT_MUTED))
        self.input.setPalette(pal)
        field_label.setBuddy(self.input)
        self.input.textChanged.connect(self._on_text_changed)

        # character counter (helper text) sits under the field
        self.char_count = QLabel(f"0 / {self.MAX_CHARS}")
        self.char_count.setObjectName("CharCount")
        self.char_count.setAlignment(Qt.AlignmentFlag.AlignRight)

        # inline status: error / success, directly below the field
        self.err = StatusLabel()

        self.submit_btn = QPushButton("SUBMIT")
        self.submit_btn.setObjectName("SubmitButton")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(lambda: self.submit())
        glow = QGraphicsDropShadowEffect(self.submit_btn)
        glow.setColor(_with_alpha(MINT, 170))
        glow.setBlurRadius(22)
        glow.setOffset(0, 0)
        self.submit_btn.setGraphicsEffect(glow)

        lay.addWidget(tag)
        lay.addWidget(title)
        lay.addWidget(body)
        lay.addSpacing(6)
        lay.addWidget(field_label)
        lay.addWidget(self.input, 1)
        lay.addWidget(self.char_count)
        lay.addWidget(self.err)
        lay.addSpacing(6)
        lay.addWidget(self.submit_btn)

        self.setTabOrder(self.input, self.submit_btn)

    # ---- helpers ---------------------------------------------------------
    def _set_invalid(self, invalid: bool) -> None:
        self.input.setProperty("invalid", invalid)
        self.input.style().unpolish(self.input)
        self.input.style().polish(self.input)

    def _set_busy(self, busy: bool) -> None:
        self.submit_btn.setEnabled(not busy)
        self.input.setReadOnly(busy)
        self.submit_btn.setText("SENDING…" if busy else "SUBMIT")
        self.submit_btn.setCursor(
            Qt.CursorShape.BusyCursor if busy else Qt.CursorShape.PointingHandCursor
        )

    def _on_text_changed(self) -> None:
        n = len(self.input.toPlainText())
        self.char_count.setText(f"{n} / {self.MAX_CHARS}")
        self.char_count.setProperty("over", n > self.MAX_CHARS)
        self.char_count.style().unpolish(self.char_count)
        self.char_count.style().polish(self.char_count)
        # the user is fixing the problem -> stop showing the error
        if self.input.property("invalid"):
            self._set_invalid(False)
            self.err.clear_status()

    def _validate(self, text: str):
        """Returns an error message, or None if the text is OK."""
        if not text:
            return "Please write something before submitting."
        if len(text) < self.MIN_CHARS:
            return f"Your message is a bit short. Please add at least {self.MIN_CHARS} characters."
        if len(text) > self.MAX_CHARS:
            return f"Your message is too long by {len(text) - self.MAX_CHARS} characters."
        return None

    def _fail(self, message: str) -> None:
        self._set_invalid(True)
        self.err.show_error(message)
        self.input.setFocus()

    # ---- main action -----------------------------------------------------
    def submit(self) -> None:
        text = self.input.toPlainText().strip()
        self.err.clear_status()

        problem = self._validate(text)
        if problem:
            self._fail(problem)
            return

        self._set_busy(True)
        QApplication.processEvents()          # repaint "SENDING…" before a blocking call
        result =  AccountHandler().sendFeedback(self.input.toPlainText(), self.err)
        self._set_busy(False)

        # the backend may have reported its own error through the label
        if result is False or self.err.isVisible():
            if not self.err.isVisible():
                self._fail("Something went wrong while sending. Please try again.")
            else:
                self._set_invalid(True)
                self.input.setFocus()
            return

        self.input.clear()
        self._set_invalid(False)
        self.err.show_success("Thank you! Your feedback has been sent.")


# --------------------------------------------------------------------------
# Root:  QWidget -> QScrollArea -> QVBoxLayout -> [ImagePanel, FeedbackPanel]
# --------------------------------------------------------------------------
class Feedback(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FeedbackWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(STYLESHEET)
        self.setMinimumSize(380, 560)

        self.image_panel = ImagePanel()
        self.image_panel.set_image("resources/School.png")
        self.feedback_panel = FeedbackPanel()
        self.input = self.feedback_panel.input
        self.submit_btn = self.feedback_panel.submit_btn

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)

        scroll_areaL = QVBoxLayout(scroll_widget)
        scroll_areaL.addWidget(self.image_panel, 2)
        scroll_areaL.addWidget(self.feedback_panel, 3)

        root.addWidget(scroll_area)