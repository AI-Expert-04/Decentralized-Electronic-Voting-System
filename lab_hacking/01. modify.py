from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys

import json
import socket
import uuid


class Tab1(QWidget):
    def __init__(self, devs):
        super().__init__()
        self.devs = devs
        self.current_vote_id = -1

        self.vote_list_group_box = QGroupBox('투표 목록')
        self.vote_list = dict()
        self.vote_list_widget = QListWidget()
        self.vote_list_widget.clicked.connect(self.select_vote)
        self.vote_list_layout = QVBoxLayout()
        self.vote_list_layout.addWidget(self.vote_list_widget)
        self.vote_list_group_box.setLayout(self.vote_list_layout)

        self.vote_group_box = QGroupBox('투표')
        self.question_label = QLabel(self)
        self.option1_button = QPushButton()
        self.option1_button.clicked.connect(self.vote1)
        self.option2_button = QPushButton()
        self.option2_button.clicked.connect(self.vote2)
        self.option3_button = QPushButton()
        self.option3_button.clicked.connect(self.vote3)
        self.vote_layout = QVBoxLayout()
        self.vote_layout.addWidget(self.question_label)
        self.vote_layout.addWidget(self.option1_button)
        self.vote_layout.addWidget(self.option2_button)
        self.vote_layout.addWidget(self.option3_button)
        self.vote_group_box.setLayout(self.vote_layout)

        self.vote_result_group_box = QGroupBox('투표 결과')
        self.option1_progressbar = QProgressBar()
        self.option2_progressbar = QProgressBar()
        self.option3_progressbar = QProgressBar()
        self.vote_result_layout = QVBoxLayout()
        self.vote_result_layout.addWidget(self.option1_progressbar)
        self.vote_result_layout.addWidget(self.option2_progressbar)
        self.vote_result_layout.addWidget(self.option3_progressbar)
        self.vote_result_group_box.setLayout(self.vote_result_layout)

        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.vote_list_group_box, 0, 0, 1, 1)
        self.main_layout.addWidget(self.vote_group_box, 0, 1, 1, 1)
        self.main_layout.addWidget(self.vote_result_group_box, 1, 0, 1, 2)

        self.setLayout(self.main_layout)

        self.update_vote_list()

    def update_vote_list(self):
        self.vote_list.clear()
        self.vote_list_widget.clear()
        for block in self.devs.chain:
            if block['type'] == 'open':
                vote_id = block['data']['id']
                self.vote_list_widget.addItem(vote_id)
                self.vote_list[vote_id] = block['data']
                self.vote_list[vote_id]['total_vote'] = 0
                self.vote_list[vote_id]['vote_count'] = dict()
                for option in block['data']['options']:
                    self.vote_list[vote_id]['vote_count'][option] = 0
            elif block['type'] == 'vote':
                vote_id = block['data']['id']
                self.vote_list[vote_id]['total_vote'] += 1
                self.vote_list[vote_id]['vote_count'][block['data']['vote']] += 1
        self.update_vote()

    def select_vote(self):
        self.current_vote_id = self.vote_list_widget.currentItem().text()
        self.update_vote()

    def update_vote(self):
        if self.current_vote_id not in self.vote_list:
            return

        self.question_label.setText(self.vote_list[self.current_vote_id]['question'])

        self.option1_button.setText(self.vote_list[self.current_vote_id]['options'][0])
        self.option1_progressbar.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        option1_text = self.vote_list[self.current_vote_id]['options'][0]
        self.option1_progressbar.setValue(self.vote_list[self.current_vote_id]['vote_count'][option1_text])

        self.option2_button.setText(self.vote_list[self.current_vote_id]['options'][1])
        self.option2_progressbar.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        option2_text = self.vote_list[self.current_vote_id]['options'][1]
        self.option2_progressbar.setValue(self.vote_list[self.current_vote_id]['vote_count'][option2_text])

        self.option3_button.setText(self.vote_list[self.current_vote_id]['options'][2])
        self.option3_progressbar.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        option3_text = self.vote_list[self.current_vote_id]['options'][2]
        self.option3_progressbar.setValue(self.vote_list[self.current_vote_id]['vote_count'][option3_text])

    def vote1(self):
        block = {
            'type': 'vote',
            'data': {
                'id': self.current_vote_id,
                'vote': self.option1_button.text()
            }
        }
        self.devs.chain.append(block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(block).encode())
            except:
                self.devs.nodes.remove(node)
        self.update_vote_list()

    def vote2(self):
        block = {
            'type': 'vote',
            'data': {
                'id': self.current_vote_id,
                'vote': self.option2_button.text()
            }
        }
        self.devs.chain.append(block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(block).encode())
            except:
                self.devs.nodes.remove(node)
        self.update_vote_list()

    def vote3(self):
        block = {
            'type': 'vote',
            'data': {
                'id': self.current_vote_id,
                'vote': self.option3_button.text()
            }
        }
        self.devs.chain.append(block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(block).encode())
            except:
                self.devs.nodes.remove(node)
        self.update_vote_list()


class Tab2(QWidget):
    def __init__(self, devs):
        super().__init__()
        self.devs = devs

        self.form_layout = QFormLayout()

        self.question_line_edit = QLineEdit()

        self.option1_line_edit = QLineEdit()
        self.option2_line_edit = QLineEdit()
        self.option3_line_edit = QLineEdit()

        self.publish_clear_layout = QHBoxLayout()
        self.publish_button = QPushButton('게시')
        self.publish_button.clicked.connect(self.publish_vote)
        self.clear_button = QPushButton('초기화')
        self.clear_button.clicked.connect(self.clear_vote)
        self.publish_clear_layout.addWidget(self.publish_button)
        self.publish_clear_layout.addWidget(self.clear_button)

        self.form_layout.addRow('질문:', self.question_line_edit)
        self.form_layout.addRow('선택지:', self.option1_line_edit)
        self.form_layout.addRow('', self.option2_line_edit)
        self.form_layout.addRow('', self.option3_line_edit)
        self.form_layout.addRow('', self.publish_clear_layout)

        self.setLayout(self.form_layout)

    def publish_vote(self):
        block = {
            'type': 'open',
            'data': {
                'id': str(uuid.uuid4()),
                'question': self.question_line_edit.text(),
                'options': [
                    self.option1_line_edit.text(),
                    self.option2_line_edit.text(),
                    self.option3_line_edit.text()
                ]
            }
        }
        self.devs.chain.append(block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(block).encode())
            except:
                self.devs.nodes.remove(node)
        self.devs.tab1.update_vote_list()
        self.clear_vote()

    def clear_vote(self):
        self.question_line_edit.setText('')
        self.option1_line_edit.setText('')
        self.option2_line_edit.setText('')
        self.option3_line_edit.setText('')


class Tab3(QWidget):
    def __init__(self, devs):
        super().__init__()
        self.devs = devs

        self.modify_button = QPushButton('변조')
        self.modify_button.clicked.connect(self.modify)

        self.vbox_layout = QVBoxLayout()
        self.vbox_layout.addWidget(self.modify_button)

        self.setLayout(self.vbox_layout)

    def modify(self):
        self.devs.chain[-1]['type'] = 'open'
        self.devs.chain[-1]['data']['id'] = 'hack'
        self.devs.chain[-1]['data']['question'] = 'hack'
        self.devs.chain[-1]['data']['options'] = ['hack1', 'hack2', 'hack3']
        self.devs.tab1.update_vote_list()


class SocketReceiver(QThread):
    update_vote_list_signal = pyqtSignal()

    def __init__(self, devs, connection, address):
        super().__init__()
        self.devs = devs
        self.connection = connection
        self.address = address

    def run(self):
        while True:
            try:
                message = self.connection.recv(10000)
            except:
                print(f'{self.address} 연결 종료')
                break
            if len(message) == 0:
                print(f'{self.address} 연결 종료')
                break
            print(f'{self.address} 데이터 수신: {message}')
            data = json.loads(message)
            if data['type'] == 'connect':
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', data['data']['port']))
                block = {
                    'type': 'list',
                    'data': {
                        'chain': self.devs.chain
                    }
                }
                s.sendall(json.dumps(block).encode())
                self.devs.nodes.append((s, f'127.0.0.1:{data["data"]["port"]}'))
            elif data['type'] == 'list':
                self.devs.chain = data['data']['chain']
                self.update_vote_list_signal.emit()
            elif data['type'] == 'open':
                block = {
                    'type': 'open',
                    'data': {
                        'id': data['data']['id'],
                        'question': data['data']['question'],
                        'options': data['data']['options']
                    }
                }
                self.devs.chain.append(block)
                self.update_vote_list_signal.emit()
            elif data['type'] == 'vote':
                block = {
                    'type': 'vote',
                    'data': {
                        'id': data['data']['id'],
                        'vote': data['data']['vote']
                    }
                }
                self.devs.chain.append(block)
                self.update_vote_list_signal.emit()


class SocketListener(QThread):
    update_vote_list_signal = pyqtSignal()

    def __init__(self, devs):
        super().__init__()
        self.devs = devs

    def run(self):
        while True:
            connection, address = self.devs.listen_socket.accept()
            self.devs.nodes.append((connection, address))
            print('연결 됨:', address)
            self.receive_thread = SocketReceiver(self.devs, connection, address)
            self.receive_thread.update_vote_list_signal.connect(self.update_vote_list)
            self.receive_thread.start()

    @pyqtSlot()
    def update_vote_list(self):
        self.update_vote_list_signal.emit()


class DecentralizedElectronicVotingSystem(QWidget):
    def __init__(self):
        super().__init__()

        self.chain = []
        self.nodes = []

        self.setWindowTitle('탈중앙 전자 투표 시스템')

        self.tab1 = Tab1(self)
        self.tab2 = Tab2(self)
        self.tab3 = Tab3(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tab1, '투표')
        self.tabs.addTab(self.tab2, '투표 생성')
        self.tabs.addTab(self.tab3, 'Hack')

        self.vbox_layout = QVBoxLayout()
        self.vbox_layout.addWidget(self.tabs)

        self.setLayout(self.vbox_layout)

        port = 6000
        while True:
            try:
                self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.listen_socket.bind(('127.0.0.1', port))
                self.listen_socket.listen(1)
                print(f'{port}포트 연결 대기')
                break
            except:
                port += 1

        self.listen_thread = SocketListener(self)
        self.listen_thread.update_vote_list_signal.connect(self.update_vote_list)
        self.listen_thread.start()

        for p in range(6000, 6005):
            if p == port:
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', p))
                s.sendall(json.dumps({
                    'type': 'connect',
                    'data': {
                        'port': port
                    }
                }).encode())
                self.nodes.append((s, f'127.0.0.1:{p}'))
            except:
                pass

    @pyqtSlot()
    def update_vote_list(self):
        self.tab1.update_vote_list()


def exception_hook(except_type, value, traceback):
    print(except_type, value, traceback)
    exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = exception_hook
    devs = DecentralizedElectronicVotingSystem()
    devs.show()
    sys.exit(app.exec_())