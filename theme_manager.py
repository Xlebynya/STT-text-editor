from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt


class ThemeManager:
    """Класс для управления темами приложения"""

    def update_voice_button_style(self, recording):
        """Меняет цвет кнопки голосового ввода"""
        if recording:
            self.setStyleSheet(
                """
                QToolButton {
                    background-color: #ff5d5d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    min-width: 80px;
                }
                QToolButton:hover {
                    background-color: #ff6d6d;
                }
                QToolButton:pressed {
                    background-color: #ff4d4d;
                }
                """
            )
        else:
            self.setStyleSheet(
                """
                QToolButton {
                    background-color: #5d5dff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    min-width: 80px;
                }
                QToolButton:hover {
                    background-color: #6d6dff;
                }
                QToolButton:pressed {
                    background-color: #4d4dff;
                }
                """
            )  # Возвращаем стандартный стиль

    @staticmethod
    def setup_theme(app, mode="dark"):
        """Применяет тему к приложению"""
        palette = app.palette()

        if mode == "dark":
            colors = {
                QPalette.Window: QColor(40, 40, 40),
                QPalette.WindowText: Qt.white,
                QPalette.Base: QColor(45, 45, 45),
                QPalette.AlternateBase: QColor(50, 50, 50),
                QPalette.ToolTipBase: Qt.white,
                QPalette.ToolTipText: Qt.white,
                QPalette.Text: Qt.white,
                QPalette.Button: QColor(60, 60, 60),
                QPalette.ButtonText: Qt.white,
                QPalette.BrightText: Qt.red,
                QPalette.Highlight: QColor(93, 93, 255),
                QPalette.HighlightedText: Qt.black,
            }
            toolbar_style = (
                "background-color: #252525; border: none; padding: 5px; spacing: 10px;"
            )
        else:
            colors = {
                QPalette.Window: QColor(240, 240, 240),
                QPalette.WindowText: Qt.black,
                QPalette.Base: Qt.white,
                QPalette.AlternateBase: QColor(245, 245, 245),
                QPalette.ToolTipBase: Qt.white,
                QPalette.ToolTipText: Qt.black,
                QPalette.Text: Qt.black,
                QPalette.Button: QColor(240, 240, 240),
                QPalette.ButtonText: Qt.black,
                QPalette.BrightText: Qt.red,
                QPalette.Highlight: QColor(100, 149, 237),
                QPalette.HighlightedText: Qt.white,
            }
            toolbar_style = (
                "background-color: #e0e0e0; border: none; padding: 5px; spacing: 10px;"
            )

        # Применяем цвета к палитре приложения
        for key, value in colors.items():
            palette.setColor(key, value)

        app.setPalette(palette)
        return toolbar_style
