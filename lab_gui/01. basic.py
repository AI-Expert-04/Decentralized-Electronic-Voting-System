from PyQt5.QtWidgets import *
import sys


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('제목')


def exception_hook(except_type, value, traceback):
    print(except_type, value, traceback)
    exit(1)


if __name__ == '__main__':
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec())