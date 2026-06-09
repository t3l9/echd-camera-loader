"""
Современные уведомления - PyQt6
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsDropShadowEffect, QSizePolicy
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QColor, QCursor


class Toast(QWidget):
    """Минималистичное уведомление"""

    def __init__(self, message="", variant="info", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        colors = {
            "info": "#3B82F6",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444"
        }

        icons = {"info": "ℹ", "success": "✓", "warning": "!", "error": "✕"}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        # Индикатор слева
        indicator = QWidget()
        indicator.setFixedWidth(3)
        indicator.setStyleSheet(f"background-color: {colors.get(variant, colors['info'])}; border-radius: 2px;")
        layout.addWidget(indicator)

        # Иконка
        icon_label = QLabel(icons.get(variant, "ℹ"))
        icon_label.setStyleSheet(f"color: {colors.get(variant, colors['info'])}; font-weight: bold; font-size: 14px;")
        layout.addWidget(icon_label)

        # Сообщение
        msg_label = QLabel(message)
        msg_label.setStyleSheet("color: #0F172A; font-size: 13px;")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        # Кнопка закрытия
        close_btn = QLabel("✕")
        close_btn.setStyleSheet("color: #9CA3AF; font-size: 16px;")
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setFixedSize(20, 20)
        close_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        close_btn.mousePressEvent = self._on_close_click
        layout.addWidget(close_btn)

        self.setStyleSheet("""
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
        """)
        self.setFixedWidth(320)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

    def _on_close_click(self, event):
        """Обработчик клика закрытия"""
        self.close()


class ToastManager:
    """Менеджер уведомлений"""

    def __init__(self, parent=None):
        self.parent = parent
        self.toasts = []

    def show(self, message, variant="info", duration=4000):
        toast = Toast(message, variant, self.parent)

        if self.parent:
            x = self.parent.geometry().right() - 340
            y = 20 + len(self.toasts) * 65
        else:
            x = 100
            y = 20
            
        toast.move(x, y)
        toast.show()
        self.toasts.append(toast)

        if duration > 0:
            QTimer.singleShot(duration, toast.close)
        return toast

    def info(self, msg): return self.show(msg, "info")
    def success(self, msg): return self.show(msg, "success")
    def warning(self, msg): return self.show(msg, "warning")
    def error(self, msg): return self.show(msg, "error")
