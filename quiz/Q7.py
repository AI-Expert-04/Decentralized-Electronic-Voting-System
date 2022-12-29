import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import sys

import requests
import json
import socket
import uuid
from ecdsa import SigningKey, VerifyingKey
import hashlib
import base64


def get_block_hash(block):
    difficulty = 4
    nonce = 0

    data = dict()
    data['type'] = block['transaction']['type']
    data['data'] = sorted(block['transaction']['data'].copy().items())
    data['author'] = block['transaction']['author']
    data['previous_hash'] = block['previous_hash']
    data = sorted(data.items())

    while True:
        data_with_nonce = (str(data) + str(nonce)).encode()
        data_hash = hashlib.sha256(str(data_with_nonce).encode()).hexdigest()
        if data_hash[:difficulty] == '0' * difficulty:
            return data_hash
        else:
            nonce += 1


def get_block_signature(block, key):
    data = dict()
    data['type'] = block['transaction']['type']
    data['data'] = sorted(block['transaction']['data'].copy().items())
    data['author'] = block['transaction']['author']
    data = sorted(data.items())
    signature = key.sign(str(data).encode())
    return base64.b64encode(signature).decode()


def verify_block_hash(block):
    block_hash = get_block_hash(block)
    if block_hash != block['hash']:
        return False
    return True


def verify_block_signature(block):
    key = VerifyingKey.from_pem(block['transaction']['author'].encode())
    data = dict()
    data['type'] = block['transaction']['type']
    data['data'] = sorted(block['transaction']['data'].copy().items())
    data['author'] = block['transaction']['author']
    data = sorted(data.items())
    try:
        key.verify(base64.b64decode(block['signature'].encode()), str(data).encode())
    except:
        return False
    return True


def verify_block_chain(chain):
    if (not verify_block_hash(chain[0])) or chain[0]['transaction']['type'] != 'genesis':
        return False
    for i in range(1, len(chain)):
        if not verify_block_signature(chain[i]):
            return False
        if not verify_block_hash(chain[i]):
            return False
        if chain[i]['previous_hash'] != chain[i - 1]['hash']:
            return False
    return True


class Tab1(QWidget):
    def __init__(self, devs):
        super().__init__()

        self.devs = devs

        self.current_vote_id = -1

        wallet_group_box = QGroupBox("지갑")

        self.wallet_info_label = QLabel()
        self.wallet_info_label.setText('')

        wallet_generate_button = QPushButton("지갑 생성")
        wallet_generate_button.clicked.connect(self.generate_wallet)

        wallet_select_button = QPushButton("지갑 선택")
        wallet_select_button.clicked.connect(self.select_wallet)

        wallet_layout = QHBoxLayout()
        wallet_layout.addWidget(self.wallet_info_label)
        wallet_layout.addWidget(wallet_generate_button)
        wallet_layout.addWidget(wallet_select_button)
        wallet_layout.addStretch(1)
        wallet_group_box.setLayout(wallet_layout)

        vote_list_group_box = QGroupBox("투표 목록")

        self.vote_list = dict()
        self.vote_list_widget = QListWidget()
        self.vote_list_widget.clicked.connect(self.select_vote)

        vote_list_layout = QVBoxLayout()
        vote_list_layout.addWidget(self.vote_list_widget)
        vote_list_layout.addStretch(1)

        vote_list_group_box.setLayout(vote_list_layout)

        vote_group_box = QGroupBox("투표")

        self.question_label = QLabel(self)

        self.option_button1 = QPushButton()
        self.option_button2 = QPushButton()
        self.option_button3 = QPushButton()

        self.option_button1.clicked.connect(self.vote1)
        self.option_button2.clicked.connect(self.vote2)
        self.option_button3.clicked.connect(self.vote3)

        vote_layout = QVBoxLayout()
        vote_layout.addWidget(self.question_label)
        vote_layout.addWidget(self.option_button1)
        vote_layout.addWidget(self.option_button2)
        vote_layout.addWidget(self.option_button3)
        vote_layout.addStretch(1)

        vote_group_box.setLayout(vote_layout)

        vote_result_group_box = QGroupBox("투표 결과")

        self.option_progress1 = QProgressBar()
        self.option_progress2 = QProgressBar()
        self.option_progress3 = QProgressBar()

        vote_result_layout = QVBoxLayout()
        vote_result_layout.addWidget(self.option_progress1)
        vote_result_layout.addWidget(self.option_progress2)
        vote_result_layout.addWidget(self.option_progress3)
        vote_result_layout.addStretch(1)

        vote_result_group_box.setLayout(vote_result_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(wallet_group_box, 0, 0, 1, 2)
        main_layout.addWidget(vote_list_group_box, 1, 0)
        main_layout.addWidget(vote_group_box, 1, 1)
        main_layout.addWidget(vote_result_group_box, 2, 0, 1, 2)
        main_layout.setRowStretch(1, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        self.setLayout(main_layout)

        self.update_wallet_info()
        self.update_vote_list()

    def generate_wallet(self):
        self.devs.private_key = SigningKey.generate()
        self.devs.public_key = self.devs.private_key.get_verifying_key()
        self.devs.wallet_address = hashlib.sha256(self.devs.public_key.to_string()).hexdigest()

        if not os.path.exists('../wallets'):
            os.mkdir('../wallets')

        f = open(f'../wallets/{self.devs.wallet_address}.pem', 'wb')
        f.write(self.devs.private_key.to_pem())
        f.close()

        self.update_wallet_info()

    def select_wallet(self):
        path, _ = QFileDialog.getOpenFileName(self, '지갑 선택', '../wallets', 'PEM Files (*.pem)')
        if path == '':
            return

        f = open(path, 'rb')
        pem = f.read()
        f.close()

        self.devs.private_key = SigningKey.from_pem(pem)
        self.devs.public_key = self.devs.private_key.get_verifying_key()
        self.devs.wallet_address = hashlib.sha256(self.devs.public_key.to_string()).hexdigest()

        self.update_wallet_info()

    def update_wallet_info(self):
        self.wallet_info_label.setText(f'지갑 주소: {self.devs.wallet_address}')

    def update_vote_list(self):
        self.vote_list.clear()
        self.vote_list_widget.clear()
        for block in self.devs.chain:
            if block['transaction']['type'] == 'open':
                self.vote_list_widget.addItem(block['transaction']['data']['id'])
                self.vote_list[block['transaction']['data']['id']] = block['transaction']['data'].copy()
                self.vote_list[block['transaction']['data']['id']]['total_vote'] = 0
                self.vote_list[block['transaction']['data']['id']]['vote_count'] = dict()
                for option in block['transaction']['data']['options']:
                    self.vote_list[block['transaction']['data']['id']]['vote_count'][option] = 0
            elif block['transaction']['type'] == 'vote':
                self.vote_list[block['transaction']['data']['id']]['total_vote'] += 1
                self.vote_list[block['transaction']['data']['id']]['vote_count'][block['transaction']['data']['vote']] += 1
        self.update_vote()

    def select_vote(self):
        self.current_vote_id = self.vote_list_widget.currentItem().text()
        self.update_vote()

    def update_vote(self):
        if self.current_vote_id not in self.vote_list:
            return
        self.question_label.setText(self.vote_list[self.current_vote_id]['question'])

        self.option_button1.setText(self.vote_list[self.current_vote_id]['options'][0])
        self.option_progress1.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        self.option_progress1.setValue(self.vote_list[self.current_vote_id]['vote_count'][self.vote_list[self.current_vote_id]['options'][0]])

        self.option_button2.setText(self.vote_list[self.current_vote_id]['options'][1])
        self.option_progress2.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        self.option_progress2.setValue(self.vote_list[self.current_vote_id]['vote_count'][self.vote_list[self.current_vote_id]['options'][1]])

        self.option_button3.setText(self.vote_list[self.current_vote_id]['options'][2])
        self.option_progress3.setRange(0, self.vote_list[self.current_vote_id]['total_vote'])
        self.option_progress3.setValue(self.vote_list[self.current_vote_id]['vote_count'][self.vote_list[self.current_vote_id]['options'][2]])

    def vote1(self):
        unconfirmed_block = {
            'transaction': {
                'author': self.devs.public_key.to_pem().decode(),
                'type': 'vote',
                'data': {
                    'id': self.current_vote_id,
                    'vote': self.option_button1.text()
                }
            }
        }
        unconfirmed_block['signature'] = get_block_signature(unconfirmed_block, self.devs.private_key)
        self.devs.unconfirmed_blocks.append(unconfirmed_block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(unconfirmed_block).encode())
            except:
                self.devs.nodes.remove(node)
        self.devs.mining_tab.update_unconfirmed_block_list()

    def vote2(self):
        unconfirmed_block = {
            'transaction': {
                'author': self.devs.public_key.to_pem().decode(),
                'type': 'vote',
                'data': {
                    'id': self.current_vote_id,
                    'vote': self.option_button2.text()
                }
            }
        }
        unconfirmed_block['signature'] = get_block_signature(unconfirmed_block, self.devs.private_key)
        self.devs.unconfirmed_blocks.append(unconfirmed_block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(unconfirmed_block).encode())
            except:
                self.devs.nodes.remove(node)
        self.devs.mining_tab.update_unconfirmed_block_list()

    def vote3(self):
        unconfirmed_block = {
            'transaction': {
                'author': self.devs.public_key.to_pem().decode(),
                'type': 'vote',
                'data': {
                    'id': self.current_vote_id,
                    'vote': self.option_button3.text()
                }
            }
        }
        unconfirmed_block['signature'] = get_block_signature(unconfirmed_block, self.devs.private_key)
        self.devs.unconfirmed_blocks.append(unconfirmed_block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(unconfirmed_block).encode())
            except:
                self.devs.nodes.remove(node)
        self.devs.mining_tab.update_unconfirmed_block_list()


class Tab2(QWidget):
    def __init__(self, devs):
        super().__init__()

        self.devs = devs

        form_layout = QFormLayout()

        self.question_line_edit = QLineEdit()

        options_layout = QVBoxLayout()
        self.option_line_edits = [QLineEdit() for _ in range(3)]
        for option_line_edit in self.option_line_edits:
            options_layout.addWidget(option_line_edit)

        publish_clear_layout = QHBoxLayout()
        publish_button = QPushButton("게시")
        publish_button.clicked.connect(self.publish_form)
        clear_button = QPushButton("초기화")
        clear_button.clicked.connect(self.clear_form)
        publish_clear_layout.addWidget(publish_button)
        publish_clear_layout.addWidget(clear_button)

        form_layout.addRow("질문: ", self.question_line_edit)
        form_layout.addRow("선택지: ", options_layout)
        form_layout.addRow("", publish_clear_layout)

        self.setLayout(form_layout)

    def publish_form(self):
        unconfirmed_block = {
            'transaction': {
                'author': self.devs.public_key.to_pem().decode(),
                'type': 'open',
                'data': {
                    'id': str(uuid.uuid4()),
                    'question': self.question_line_edit.text(),
                    'options': [option_line_edit.text() for option_line_edit in self.option_line_edits]
                }
            }
        }
        unconfirmed_block['signature'] = get_block_signature(unconfirmed_block, self.devs.private_key)
        self.devs.unconfirmed_blocks.append(unconfirmed_block)
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(unconfirmed_block).encode())
            except:
                self.devs.nodes.remove(node)
        self.devs.mining_tab.update_unconfirmed_block_list()
        self.clear_form()

    def clear_form(self):
        self.question_line_edit.setText('')

        for option_line_edit in self.option_line_edits:
            option_line_edit.setText('')


class Tab3(QWidget):
    def __init__(self, devs):
        super().__init__()

        self.devs = devs

        mining_button = QPushButton("채굴")
        mining_button.clicked.connect(self.mine)

        self.unconfirmed_block_list_widget = QListWidget()
        self.unconfirmed_block_list_widget.clicked.connect(self.select_unconfirmed_block)

        self.unconfirmed_block_info_label = QLabel()
        self.unconfirmed_block_info_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(mining_button)
        layout.addWidget(self.unconfirmed_block_list_widget)
        layout.addWidget(self.unconfirmed_block_info_label)
        layout.addStretch(1)

        self.setLayout(layout)

    def update_unconfirmed_block_list(self):
        self.unconfirmed_block_list_widget.clear()
        for unconfirmed_block in self.devs.unconfirmed_blocks:
            self.unconfirmed_block_list_widget.addItem(str(unconfirmed_block))

    def select_unconfirmed_block(self):
        self.unconfirmed_block_info_label.setText(self.unconfirmed_block_list_widget.currentItem().text())

    def mine(self):
        for unconfirmed_block in self.devs.unconfirmed_blocks:
            if not verify_block_signature(unconfirmed_block):
                print('블록 위변조 감지')
                continue
            block = {
                'transaction': unconfirmed_block['transaction'],
                'signature': unconfirmed_block['signature'],
                'previous_hash': self.devs.chain[-1]['hash']
            }
            block['hash'] = get_block_hash(block)
            self.devs.chain.append(block)

        self.devs.unconfirmed_blocks.clear()
        self.unconfirmed_block_list_widget.clear()
        self.devs.vote_list_tab.update_vote_list()
        block = {
            'transaction': {
                'type': 'mine',
                'data': {
                    'chain': self.devs.chain
                }
            }
        }
        for node in self.devs.nodes.copy():
            try:
                node[0].sendall(json.dumps(block).encode())
            except:
                self.devs.nodes.remove(node)


class SocketReceiver(QThread):
    update_vote_list_signal = pyqtSignal()
    update_unconfirmed_block_list_signal = pyqtSignal()

    def __init__(self, devs, connection, address):
        super().__init__()
        self.devs = devs
        self.connection = connection
        self.address = address

    def run(self):
        while True:
            try:
                message = self.connection.recv(10240)
            except:
                print(f'{self.address} 연결 종료')
                break
            if len(message) == 0:
                print(f'{self.address} 연결 종료')
                break
            print(f"{self.address} 데이터 수신: {message}")
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
                if verify_block_chain(data['transaction']['data']['chain']):
                    self.devs.chain = data['transaction']['data']['chain']
                    self.update_vote_list_signal.emit()
                else:
                    print('블록체인 위변조 감지')
            elif data['transaction']['type'] == 'open':
                self.devs.unconfirmed_blocks.append(data)
                self.update_unconfirmed_block_list_signal.emit()
            elif data['transaction']['type'] == 'vote':
                self.devs.unconfirmed_blocks.append(data)
                self.update_unconfirmed_block_list_signal.emit()
            elif data['transaction']['type'] == 'mine':
                if verify_block_chain(data['transaction']['data']['chain']):
                    self.devs.chain = data['transaction']['data']['chain']
                    self.devs.unconfirmed_blocks.clear()
                    self.update_vote_list_signal.emit()
                    self.update_unconfirmed_block_list_signal.emit()
                else:
                    print('블록체인 위변조 감지')


class SocketListener(QThread):
    update_vote_list_signal = pyqtSignal()
    update_unconfirmed_block_list_signal = pyqtSignal()

    def __init__(self, devs):
        super().__init__()
        self.devs = devs

    def run(self):
        while True:
            connection, address = self.devs.listen_socket.accept()
            self.devs.nodes.append((connection, address))
            print("연결 됨: ", address)
            self.receive_thread = SocketReceiver(self.devs, connection, address)
            self.receive_thread.update_vote_list_signal.connect(self.update_vote_list)
            self.receive_thread.update_unconfirmed_block_list_signal.connect(self.update_unconfirmed_block_list)
            self.receive_thread.start()

    @pyqtSlot()
    def update_vote_list(self):
        self.update_vote_list_signal.emit()

    @pyqtSlot()
    def update_unconfirmed_block_list(self):
        self.update_unconfirmed_block_list_signal.emit()


class SocketManager(QThread):
    update_vote_list_signal = pyqtSignal()
    update_unconfirmed_block_list_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.port = 6000

    def run(self):
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
        self.listen_thread.update_unconfirmed_block_list_signal.connect(self.update_unconfirmed_block_list)
        self.listen_thread.start()

        for p in range(6000, 6100):
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
        self.update_vote_list_signal.emit()

    @pyqtSlot()
    def update_unconfirmed_block_list(self):
        self.update_unconfirmed_block_list_signal.emit()


class DecentralizedElectronicVotingSystem(QWidget):
    def __init__(self):
        super().__init__()

        f = open('../wallets/wallet.pem', 'rb')
        pem = f.read()
        f.close()

        self.private_key = SigningKey.from_pem(pem)
        self.public_key = self.private_key.get_verifying_key()
        self.wallet_address = hashlib.sha256(self.public_key.to_string()).hexdigest()

        genesis_block = {
            'transaction': {
                'author': self.public_key.to_pem().decode(),
                'type': 'genesis',
                'data': dict(),
            },
            'previous_hash': None
        }
        genesis_block['hash'] = get_block_hash(genesis_block)

        self.chain = [genesis_block]
        self.unconfirmed_blocks = []
        self.nodes = []

        self.setWindowTitle("탈중앙 블록체인 투표 시스템")

        self.vote_list_tab = Tab1(self)
        self.vote_tab = Tab2(self)
        self.mining_tab = Tab3(self)

        tabs = QTabWidget()
        tabs.addTab(self.vote_list_tab, '투표')
        tabs.addTab(self.vote_tab, '투표 생성')
        tabs.addTab(self.mining_tab, '채굴')

        vbox = QVBoxLayout()
        vbox.addWidget(tabs)

        self.setLayout(vbox)

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
        self.listen_thread.update_unconfirmed_block_list_signal.connect(self.update_unconfirmed_block_list)
        self.listen_thread.start()

        for p in range(6000, 6005):
            if p == port:
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', p))
                block = {
                    'transaction': {
                        'type': 'connect',
                        'data': {
                            'port': port
                        }
                    }
                }
                s.sendall(json.dumps(block).encode())
                self.nodes.append((s, f'127.0.0.1:{p}'))
            except:
                pass

    @pyqtSlot()
    def update_vote_list(self):
        self.vote_list_tab.update_vote_list()

    @pyqtSlot()
    def update_unconfirmed_block_list(self):
        self.mining_tab.update_unconfirmed_block_list()


def exception_hook(except_type, value, traceback):
    print(except_type, value, traceback)
    traceback.print_exc()
    exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = exception_hook
    devs = DecentralizedElectronicVotingSystem()
    devs.show()
    sys.exit(app.exec_())