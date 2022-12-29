from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import json
import socket
import uuid
import hashlib


def get_block_hash(block):
    data = dict()
    data['type'] = block['transaction']['type']
    data['data'] = sorted(block['transaction']['data'].copy().items())
    data = sorted(data.items())
    return hashlib.sha256(str(data).encode()).hexdigest()


class Tab1(QWidget):
    def __init__(self, devs):
        super().__init__()
        self.devs = devs
        self.current_vote_id = -1

        self.vote_list_group_box =  QGroupBox('투표 목록')
        self.vote_list = dict()
        self.vote_list_widget = QListWidget()
        self.vote_list_widget.clicked.connect(self.select_vote)
        self.vote_list_layout = QVBoxLayout()
        self.vote_list_layout.addWidget(self.vote_list_widget)
        self.vote_list_group_box.setLayout(self.vote_list_layout)

        self.vote_group_box = QGroupBox('투표')
        self.question_label = QLabel(self)
        self.option1_button = QPushButton()
        self.option2_button = QPushButton()
        self.option3_button = QPushButton()
        self.option1_button.clicked.connect(self.vote1)
        self.option2_button.clicked.connect(self.vote2)
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
            if block['transaction']['type'] == 'open':
                id = block['transaction']['data']['id']
                self.vote_list_widget.addItem(id)
                self.vote_list[id] = block['transaction']['data'].copy()
                self.vote_list[id]['total_vote'] = 0
                self.vote_list[id]['vote_count'] = dict()
                for option in block['transaction']['data']['options']:
                    self.vote_list[id]['vote_count'][option] = 0
            elif block['transaction']['type'] == 'vote':
                id = block['transaction']['data']['id']
                self.vote_list[id]['total_vote'] += 1
                self.vote_list[id]['vote_count'][block['transaction']['data']['vote']] += 1
        self.update_vote()

    def select_vote(self):
        self.current_vote_id = self.vote_list_widget.currentItem().text()
        self.update_vote()

    def update_vote(self):
        if self.current_vote_id not in self.vote_list:
            return
        self.question_label.setText(self.vote_list[self.current_vote_id]['question'])

        option1 = self.vote_list[self.current_vote_id]['options'][0]
        self.option1_button.setText(option1)
        self.option1_progressbar.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        self.option1_progressbar.setValue(self.vote_list[self.current_vote_id]['vote_count'][option1])

        option2 = self.vote_list[self.current_vote_id]['options'][1]
        self.option2_button.setText(option2)
        self.option2_progressbar.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        self.option2_progressbar.setValue(self.vote_list[self.current_vote_id]['vote_count'][option2])

        option3 = self.vote_list[self.current_vote_id]['options'][2]
        self.option3_button.setText(option3)
        self.option3_progressbar.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        self.option3_progressbar.setValue(self.vote_list[self.current_vote_id]['vote_count'][option3])

    def vote1(self):
        block = {
            'transaction': {
                'type': 'vote',
                'data': {
                    'id': self.current_vote_id,
                    'vote': self.option1_button.text()
                }
            }
        }
        block['hash'] = get_block_hash(block)
        self.devs.chain.append(block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(block).encode())
            except:
                self.devs.nodes.remove(node)
        self.update_vote_list()

    def vote2(self):
        block = {
            'transaction': {
                'type': 'vote',
                'data': {
                    'id': self.current_vote_id,
                    'vote': self.option2_button.text()
                }
            }
        }
        block['hash'] = get_block_hash(block)
        self.devs.chain.append(block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(block).encode())
            except:
                self.devs.nodes.remove(node)
        self.update_vote_list()

    def vote3(self):
        block = {
            'transaction': {
                'type': 'vote',
                'data': {
                    'id': self.current_vote_id,
                    'vote': self.option3_button.text()
                }
            }
        }
        block['hash'] = get_block_hash(block)
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
        self.publish_button.clicked.connect(self.publish_form)
        self.clear_button = QPushButton('초기화')
        self.clear_button.clicked.connect(self.clear_form)

        self.publish_clear_layout.addWidget(self.publish_button)
        self.publish_clear_layout.addWidget(self.clear_button)

        self.form_layout.addRow('질문:', self.question_line_edit)
        self.form_layout.addRow('선택지:', self.option1_line_edit)
        self.form_layout.addRow('', self.option2_line_edit)
        self.form_layout.addRow('', self.option3_line_edit)
        self.form_layout.addRow('', self.publish_clear_layout)

        self.setLayout(self.form_layout)

    def publish_form(self):
        block = {
            'transaction': {
                'type': 'open',
                'data': {
                    'id': str(uuid.uuid4()),
                    'question': self.question_line_edit.text(),
                    'options': [self.option1_line_edit.text(), self.option2_line_edit.text(), self.option3_line_edit.text()]
                }
            }
        }
        block['hash'] = get_block_hash(block)
        self.devs.chain.append(block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(block).encode())
            except:
                self.devs.nodes.remove(node)
        self.devs.tab1.update_vote_list()
        self.clear_form()

    def clear_form(self):
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
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.modify_button)
        self.setLayout(self.layout)

    def modify(self):
        self.devs.chain[-1]['transaction']['type'] = 'open'
        self.devs.chain[-1]['transaction']['data']['id'] = 'hack'
        self.devs.chain[-1]['transaction']['data']['question'] = 'hack'
        self.devs.chain[-1]['transaction']['data']['options'] = ['hack1', 'hack2', 'hack3']
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
            if data['transaction']['type'] == 'connect':
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', data['transaction']['data']['port']))
                block = {
                    'transaction': {
                        'type': 'list',
                        'data': {
                            'chain': self.devs.chain
                        }
                    }
                }
                s.sendall(json.dumps(block).encode())
                self.devs.nodes.append((s, f'127.0.0.1:{data["transaction"]["data"]["port"]}'))
            elif data['transaction']['type'] == 'list':
                valid_chain = True
                for block in data['transaction']['data']['chain']:
                    block_hash = get_block_hash(block)
                    if block_hash != block['hash']:
                        print('변조 감지')
                        valid_chain = False
                        break
                if valid_chain:
                    self.devs.chain = data['transaction']['data']['chain']
                self.update_vote_list_signal.emit()
            elif data['transaction']['type'] == 'open':
                self.devs.chain.append(data)
                self.update_vote_list_signal.emit()
            elif data['transaction']['type'] == 'vote':
                self.devs.chain.append(data)
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
            print(f'연결 됨: {address}')
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

        self.setWindowTitle('탈중앙 블록체인 투표 시스템')

        self.tab1 = Tab1(self)
        self.tab2 = Tab2(self)
        self.tab3 = Tab3(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tab1, '투표')
        self.tabs.addTab(self.tab2, '투표 생성')
        self.tabs.addTab(self.tab3, 'hack')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

        self.port = 6000
        while True:
            try:
                self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.listen_socket.bind(('127.0.0.1', self.port))
                self.listen_socket.listen(1)
                print(f'{self.port}포트 연결 대기')
                break
            except:
                self.port += 1

        self.listen_thread = SocketListener(self)
        self.listen_thread.update_vote_list_signal.connect(self.update_vote_list)
        self.listen_thread.start()

        for p in range(6000, 6005):
            if p == self.port:
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', p))
                block = {
                    'transaction': {
                        'type': 'connect',
                        'data': {
                            'port': self.port
                        }
                    }
                }
                s.sendall(json.dumps(block).encode())
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