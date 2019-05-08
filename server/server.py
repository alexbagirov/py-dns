import socket
import logging
import sys
from parser.parser import PackerParser


logger = logging.getLogger('Server')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
logger.info('Starting the server')
sock.bind(('127.0.0.1', 12345))

try:
    while True:
        data, addr = sock.recvfrom(1024)

        ns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ns_sock.connect(('199.7.83.42', 53))  # 199.7.83.42
        ns_sock.sendall(data)
        answer = ns_sock.recv(1024)
        ns_sock.close()

        sock.sendto(answer, addr)

        (queries, answers,
         authorities, additional) = PackerParser.parse_response(answer)

        print(queries)
        print(answers)
        print(authorities)
        print(additional)
except KeyboardInterrupt:
    logger.info('Stopping the server')
finally:
    sock.close()
