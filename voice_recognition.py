import json
import queue
from vosk import Model, KaldiRecognizer
from PyQt5.QtCore import QThread, pyqtSignal


class VoiceRecognitionThread(QThread):
    """Поток для асинхронного распознавания речи с использованием Vosk"""

    finished = pyqtSignal(str)  # Сигнал с окончательным текстом
    processing = pyqtSignal()  # Сигнал о начале обработки
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.audio_queue = queue.Queue()
        self.should_process = True
        self.model = None
        self.recognizer = None
        self.load_model()

    def load_model(self):
        """Загружает модель Vosk"""
        try:
            model_path = "model"
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
        except Exception as e:
            self.error.emit(f"Ошибка загрузки модели: {str(e)}")

    def add_audio_data(self, data):
        """Добавляет аудиоданные в очередь"""
        if self.should_process:
            self.audio_queue.put(data)


    def run(self):
        """Обрабатывает записанные аудиоданные"""
        self.processing.emit()

        try:
            while self.should_process or not self.audio_queue.empty():
                try:
                    data = self.audio_queue.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "")
                        if text:
                            self.finished.emit(text)
                except queue.Empty:
                    continue

            # Получаем финальный результат
            final_result = json.loads(self.recognizer.FinalResult())
            text = final_result.get("text", "")

            if text:
                self.finished.emit(text)
            else:
                self.error.emit(
                    "Не удалось распознать речь. Проверьте звук и попробуйте снова."
                )

        except Exception as e:
            self.error.emit(f"Ошибка распознавания: {str(e)}")
        finally:
            self.audio_queue = queue.Queue()  # Очищаем очередь

    def stop_processing(self):
        """Останавливает обработку"""
        self.should_process = False
