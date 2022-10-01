from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QGridLayout, QGroupBox, QHBoxLayout, \
    QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog, QTabWidget, QLineEdit
from PyQt5.QtGui import QPixmap, QImage, QStaticText
import time, os, math, threading, cv2, sys
from flask import Flask, jsonify
import requests, json


class T_1(QWidget):
    def __init__(self):
        super().__init__()
        data = {
            'question': 'Q1',
            'options': ['A1', 'A2', 'A3']
        }
        A, B = data.values()
        self.A, self.B, self.C = B

        self.setWindowTitle('제목')

        self.group_box = QGroupBox('메뉴')
        self.Title = QPushButton('투표 조회')
        self.Title.clicked.connect(self.title)
        self.serve_layout1 = QGridLayout()
        self.serve_layout1.addWidget(self.Title, 0, 0, 1, 1)
        self.group_box.setLayout(self.serve_layout1)

        self.group_box2 = QGroupBox('투표 목록')
        self.text_label = QLabel(self)
        self.vbox_layout = QVBoxLayout()
        self.vbox_layout.addWidget(self.text_label)
        self.group_box.setLayout(self.vbox_layout)

        self.group_box3 = QGroupBox('투표')
        self.button2 = QPushButton(self.A)
        self.button3 = QPushButton(self.B)
        self.button4 = QPushButton(self.C)
        self.serve_layout2 = QGridLayout()
        self.serve_layout2.addWidget(self.button2, 1, 0, 1, 1)
        self.serve_layout2.addWidget(self.button3, 2, 0, 1, 1)
        self.serve_layout2.addWidget(self.button4, 3, 0, 1, 1)
        self.group_box3.setLayout(self.serve_layout2)

        self.group_box4 = QGroupBox('투표 결과')
        self.button5 = QPushButton('버튼 5')
        self.serve_layout3 = QGridLayout()
        self.serve_layout3.addWidget(self.button5, 0, 0, 1, 1)
        self.group_box4.setLayout(self.serve_layout3)

        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.group_box, 0, 0, 1, 0)
        self.main_layout.addWidget(self.group_box2, 1, 0, 1, 1)
        self.main_layout.addWidget(self.group_box3, 1, 1, 1, 1)
        self.main_layout.addWidget(self.group_box4, 2, 0, 1, 0)
        self.setLayout(self.main_layout)

    def title(self):
        res = requests.get('http://127.0.0.1:5000/list')
        data = json.loads(res.text)

    def A1(self):
        self.text_label.setText('1')

    def A2(self):
        self.text_label.setText('2')

    def A3(self):
        self.text_label.setText('3')


class T_2(QWidget):
    def __init__(self):
        super().__init__()
        self.data = {

        }
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.label = QLabel("질문: ")
        self.label2 = QLabel("선택지: ")
        self.button1 = QPushButton('게시')
        self.button1.clicked.connect(self.update)
        self.button2 = QPushButton('초기화')
        self.button2.clicked.connect(self.reset)
        self.lineEdit = QLineEdit()
        self.lineEdit2 = QLineEdit()
        self.lineEdit3 = QLineEdit()
        self.lineEdit4 = QLineEdit()
        self.lineEdit.setPlaceholderText("질문을 입력하세요.")
        self.lineEdit2.setPlaceholderText("선택지를 입력하세요.")
        self.lineEdit3.setPlaceholderText("선택지를 입력하세요.")
        self.lineEdit4.setPlaceholderText("선택지를 입력하세요.")
        self.lineEdit.setMaxLength(10)
        self.lineEdit2.setMaxLength(10)
        self.lineEdit3.setMaxLength(10)
        self.lineEdit4.setMaxLength(10)
        self.layout.addWidget(self.label, 0, 0, 1, 1)
        self.layout.addWidget(self.label2, 0, 0, 2, 1)
        self.layout.addWidget(self.lineEdit, 0, 1, 1, 2)
        self.layout.addWidget(self.lineEdit2, 0, 1, 2, 2)
        self.layout.addWidget(self.lineEdit3, 0, 1, 3, 2)
        self.layout.addWidget(self.lineEdit4, 0, 1, 4, 2)
        self.layout.addWidget(self.button1, 0, 1, 5, 1)
        self.layout.addWidget(self.button2, 0, 2, 5, 1)

    def update(self):
        data = {
        }
        text = self.lineEdit.text()
        data.update({'question': text})
        text2 = self.lineEdit2.text()
        data.update({'options': [text2]})
        text3 = self.lineEdit3.text()
        data['options'].append(text3)
        text4 = self.lineEdit4.text()
        data['options'].append(text4)
        print(data)
        res = requests.post('http://127.0.0.1:5000/open', data=json.dumps(data), headers=headers)
        print(res.text)

    def reset(self):
        self.label = QLabel("질문: ")
        self.label2 = QLabel("선택지: ")
        self.lineEdit = QLineEdit()
        self.lineEdit2 = QLineEdit()
        self.lineEdit3 = QLineEdit()
        self.lineEdit4 = QLineEdit()
        self.lineEdit.setPlaceholderText("질문을 입력하세요.")
        self.lineEdit2.setPlaceholderText("선택지를 입력하세요.")
        self.lineEdit3.setPlaceholderText("선택지를 입력하세요.")
        self.lineEdit4.setPlaceholderText("선택지를 입력하세요.")
        self.lineEdit.setMaxLength(10)
        self.lineEdit2.setMaxLength(10)
        self.lineEdit3.setMaxLength(10)
        self.lineEdit4.setMaxLength(10)
        self.layout.addWidget(self.label, 0, 0, 1, 1)
        self.layout.addWidget(self.label2, 0, 0, 2, 1)
        self.layout.addWidget(self.lineEdit, 0, 1, 1, 2)
        self.layout.addWidget(self.lineEdit2, 0, 1, 2, 2)
        self.layout.addWidget(self.lineEdit3, 0, 1, 3, 2)
        self.layout.addWidget(self.lineEdit4, 0, 1, 4, 2)


class tab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('오야')
        T1 = T_1()
        T2 = T_2()

        tabs = QTabWidget()
        tabs.addTab(T1, ' 투표')
        tabs.addTab(T2, ' 투표 생성')

        vbox = QVBoxLayout()
        vbox.addWidget(tabs)

        self.setLayout(vbox)


if __name__ == '__main__':
    headers = {'Content-Type': 'application/json'}
    Chain = []
    app = QApplication(sys.argv)
    tab = tab()
    tab.show()
    sys.exit(app.exec_())