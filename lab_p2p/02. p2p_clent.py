import socket

send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
send_socket.connect(('127.0.0.1', 6000))

while True:
    data = input('=> ')
    if data == 'q':
        send_socket.close()
        break
    send_socket.sendall(data.encode())