import socket
from parser.parser import PackerParser


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 12345))

while True:
    data, addr = sock.recvfrom(1024)

    ns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ns_sock.connect(('8.8.8.8', 53))
    ns_sock.sendall(data)
    answer = ns_sock.recv(1024)
    ns_sock.close()

    sock.sendto(answer, addr)

    # print(answer)
    parsed_answer = PackerParser.parse_response(answer)
    # print('Lol')
