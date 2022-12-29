import socket
import threading
import time

command = 0


def server1_receiver(connection, address):
    while True:
        message = connection.recv(1024)
        if len(message) == 0:
            print('서버1 연결 종료')
            break
        print("서버1 데이터 수신: ", message.decode())


def server1_listener():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('127.0.0.1', 6000))
    listen_socket.listen(1)

    while True:
        connection, address = listen_socket.accept()
        print("서버1 연결 됨: ", address)
        receive_thread = threading.Thread(target=server1_receiver, args=(connection, address))
        receive_thread.daemon = True
        receive_thread.start()


def server2_receiver(connection, address):
    while True:
        message = connection.recv(1024)
        if len(message) == 0:
            print('서버2 연결 종료')
            break
        print("서버2 데이터 수신: ", message.decode())


def server2_listener():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('127.0.0.1', 6001))
    listen_socket.listen(1)

    while True:
        connection, address = listen_socket.accept()
        print("서버2 연결 됨: ", address)
        receive_thread = threading.Thread(target=server2_receiver, args=(connection, address))
        receive_thread.daemon = True
        receive_thread.start()

def client1():
    send_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_socket1.connect(('127.0.0.1', 6000))

    send_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_socket2.connect(('127.0.0.1', 6001))

    print('클라이언트1 연결')

    global command
    while True:
        if command == 1:
            send_socket1.sendall('클라이언트1'.encode())
            send_socket2.sendall('클라이언트1'.encode())
        elif command == 2:
            break
        time.sleep(1)

    send_socket1.close()
    send_socket2.close()

def client2():
    send_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_socket1.connect(('127.0.0.1', 6000))

    send_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_socket2.connect(('127.0.0.1', 6001))

    print('클라이언트2 연결')

    global command
    while True:
        if command == 1:
            send_socket1.sendall('클라이언트2'.encode())
            send_socket2.sendall('클라이언트2'.encode())
        elif command == 2:
            break
        time.sleep(1)

    send_socket1.close()
    send_socket2.close()


server1_thread = threading.Thread(target=server1_listener)
server1_thread.daemon = True
server1_thread.start()

server2_thread = threading.Thread(target=server2_listener)
server2_thread.daemon = True
server2_thread.start()

time.sleep(10)

client1_thread = threading.Thread(target=client1)
client1_thread.daemon = True
client1_thread.start()

client2_thread = threading.Thread(target=client2)
client2_thread.daemon = True
client2_thread.start()

while True:
    a = input('=> ')
    if a == '1':
        command = 1
    elif a == '2':
        command = 2
    else:
        command = 0