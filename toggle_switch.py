from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QBrush

class ToggleSwitch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 24)
        self._checked = False
        self._thumb_position = 3

        # Анимация движения переключателя
        self.animation = QPropertyAnimation(self, b"thumb_position")
        self.animation.setDuration(200)

    @pyqtProperty(int)
    def thumb_position(self):
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos):
        self._thumb_position = pos
        self.update()

    def paintEvent(self, event):
        """Отрисовка кастомного переключателя"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Фон переключателя
        bg_color = QColor("#5d5dff" if self._checked else "#555")
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)

        # Сам переключатель (белая кнопка)
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(self.thumb_position, 3, 18, 18)

    def mousePressEvent(self, event):
        """Обработка клика для изменения состояния"""
        self._checked = not self._checked
        self.animate_thumb()
        self.update()
        super().mousePressEvent(event)

    def animate_thumb(self):
        """Запуск анимации движения переключателя"""
        self.animation.stop()
        self.animation.setStartValue(self.thumb_position)
        self.animation.setEndValue(29 if self._checked else 3)
        self.animation.setEasingCurve(QEasingCurve.OutBack)
        self.animation.start()
