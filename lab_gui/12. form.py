from PyQt5.QtWidgets import *
import sys


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('제목')

        self.form_layout = QFormLayout()

        self.line_edit = QLineEdit()
        self.button = QPushButton('버튼')

        self.form_layout.addRow('텍스트: ', self.line_edit)
        self.form_layout.addRow('', self.button)

        self.setLayout(self.form_layout)


def exception_hook(except_type, value, traceback):
    print(except_type, value, traceback)
    exit(1)


if __name__ == '__main__':
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec())