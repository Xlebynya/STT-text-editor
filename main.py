from PyQt5.QtWidgets import QApplication
import sys
from editor import VoiceTextEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    editor = VoiceTextEditor()
    editor.show()
    sys.exit(app.exec_())
