import socket

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.bind(('127.0.0.1', 6000))
listen_socket.listen(1)

connection, address = listen_socket.accept()
print('연결 됨:', address)

while True:
    message = connection.recv(1024)
    if len(message) == 0:
        print('연결 종료')
        listen_socket.close()
        break
    print('데이터 수신:', message)