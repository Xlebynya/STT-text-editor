from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QStatusBar,
    QFileDialog,
    QToolBar,
    QToolButton,
)
from PyQt5.QtGui import QFont
import pyaudio
from threading import Lock
from voice_recognition import VoiceRecognitionThread
from toggle_switch import ToggleSwitch
from theme_manager import ThemeManager


class VoiceTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.recorded_audio = []
        self.audio_lock = Lock()
        self.is_recording = False
        self.is_processing = False

    def initUI(self):
        """Создает основной интерфейс приложения"""
        self.setWindowTitle("VoiceText Editor")
        self.setMinimumSize(500, 300)
        self.setGeometry(100, 100, 1000, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Текстовое поле
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Times New Roman", 14))
        layout.addWidget(self.text_edit)

        # Панель инструментов
        self.create_toolbar()

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Установка темы
        self.setup_theme("dark")

    def create_toolbar(self):
        """Создание панели инструментов"""
        self.toolbar = QToolBar("Tools")
        self.addToolBar(self.toolbar)
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)

        # Кнопка "Сохранить"
        self.save_btn = QToolButton()
        self.save_btn.setText("Сохранить")
        self.style_button(self.save_btn)
        self.save_btn.clicked.connect(self.save_file)
        self.toolbar.addWidget(self.save_btn)

        # Кнопка "Открыть"
        self.open_btn = QToolButton()
        self.open_btn.setText("Открыть")
        self.style_button(self.open_btn)
        self.open_btn.clicked.connect(self.open_file)
        self.toolbar.addWidget(self.open_btn)

        # Переключатель темы
        self.theme_switch = ToggleSwitch()
        self.toolbar.addWidget(self.theme_switch)
        self.theme_switch.mousePressEvent = self.handle_theme_toggle

        # **Голосовой ввод (исправлено)**
        self.voice_btn = (
            QToolButton()
        )  # Теперь это `self.voice_btn`, а не просто `voice_btn`
        self.voice_btn.setText("Голосовой ввод")
        self.style_button(self.voice_btn)
        self.voice_btn.clicked.connect(self.start_voice_input)
        self.toolbar.addWidget(self.voice_btn)

    def handle_theme_toggle(self, event):
        """Меняет состояние темы"""
        self.theme_switch._checked = not self.theme_switch._checked
        self.theme_switch.animate_thumb()
        self.theme_switch.update()
        self.toggle_theme()

    def start_voice_input(self):
        """Управляет процессом записи и распознавания"""
        if self.is_processing:
            return  # Игнорируем нажатия во время обработки

        if self.is_recording:
            # Останавливаем запись и начинаем обработку
            self.stop_recording()
        else:
            # Начинаем новую запись
            self.start_recording()

    def start_recording(self):
        """Начинает запись аудио"""
        self.is_recording = True
        self.recorded_audio = []
        self.voice_btn.setText("Запись... (стоп)")
        ThemeManager.update_voice_button_style(self.voice_btn, self.is_recording)
        self.text_edit.setEnabled(False)
        self.cursor = self.text_edit.textCursor()

        # Инициализируем поток
        self.recognition_thread = VoiceRecognitionThread()
        self.recognition_thread.finished.connect(self.handle_recognition_result)
        self.recognition_thread.processing.connect(self.show_processing_status)
        self.recognition_thread.error.connect(self.on_recognition_error)

        # Настраиваем аудиопоток
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4096,
            stream_callback=self.audio_callback,
            start=False,
        )
        self.stream.start_stream()

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback для получения аудиоданных"""
        with self.audio_lock:
            if self.is_recording and hasattr(self, "recognition_thread"):
                self.recognition_thread.add_audio_data(in_data)
        return (in_data, pyaudio.paContinue)

    def stop_recording(self):
        """Останавливает запись и запускает обработку"""
        if not self.is_recording:
            return

        self.is_recording = False
        ThemeManager.update_voice_button_style(self.voice_btn, self.is_recording)

        # Останавливаем аудиопоток
        if hasattr(self, "stream"):
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

        # Запускаем обработку
        self.recognition_thread.start()
        self.recognition_thread.stop_processing()  # Даем команду на завершение обработки

    def show_processing_status(self):
        """Показывает статус обработки"""
        self.voice_btn.setText("Обработка...")
        self.status_bar.showMessage("Обработка записи...", 2000)

    def handle_recognition_result(self, text):
        """Обрабатывает результат распознавания"""
        self.is_processing = False
        self.voice_btn.setText("Голосовой ввод")
        self.text_edit.setEnabled(True)

        if text:
            self.cursor.insertText(text + " ")
            self.status_bar.showMessage("Текст распознан", 2000)
        else:
            self.status_bar.showMessage("Речь не распознана", 2000)

    def insert_recorded_text(self, text):
        """Вставляет распознанный текст"""
        self.is_processing = False
        self.voice_btn.setText("Голосовой ввод")
        self.text_edit.setEnabled(True)

        if text:
            self.cursor.insertText(text + " ")
            self.status_bar.showMessage("Текст распознан", 100000)
        else:
            self.status_bar.showMessage("Речь не распознана", 2000)

    def on_recognition_error(self, message):
        """Обрабатывает ошибки распознавания"""
        self.is_recording = False
        self.is_processing = False
        self.voice_btn.setText("Голосовой ввод")
        self.text_edit.setEnabled(True)
        self.status_bar.showMessage(message, 3000)

    def save_file(self):
        """Сохраняет текстовый файл"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Текстовые файлы (*.txt);;Все файлы ()"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
                self.status_bar.showMessage(f"Файл сохранен: {filename}", 3000)
            except Exception as e:
                self.status_bar.showMessage(f"Ошибка сохранения: {str(e)}", 3000)

    def open_file(self):
        """Открывает текстовый файл"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    self.text_edit.setPlainText(f.read())
                self.status_bar.showMessage(f"Файл открыт: {filename}", 3000)
            except Exception as e:
                self.status_bar.showMessage(f"Ошибка открытия: {str(e)}", 3000)

    def style_button(self, button):
        """Применяет стиль к кнопкам"""
        button.setStyleSheet(
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
        )

    def toggle_theme(self):
        """Переключает тему приложения"""
        mode = "light" if self.theme_switch._checked else "dark"
        self.setup_theme(mode)

    def setup_theme(self, mode):
        """Настраивает тему интерфейса"""
        toolbar_style = ThemeManager.setup_theme(self, mode)
        self.findChild(QToolBar).setStyleSheet(toolbar_style)
