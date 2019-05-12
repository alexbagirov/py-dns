import socket
import logging
import sys
from argparse import ArgumentParser
from parser.parser import PackerParser
from parser.builder import PacketBuilder


logger = logging.getLogger('Server')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

parser = ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=53)
group = parser.add_mutually_exclusive_group()
group.add_argument('-i', '--ip', type=str, default='1.1.1.1')
group.add_argument('--use-authoritative', action='store_true')

args = parser.parse_args()
if args.use_authoritative:
    ns_host = '199.7.83.42'
else:
    ns_host = args.ip
port = args.port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
logger.info(f'Starting the server on port {port}')
try:
    sock.bind(('127.0.0.1', port))
except PermissionError:
    logger.error(f'Permission error when opening socket on port, exiting')
    exit(0)

try:
    while True:
        data, addr = sock.recvfrom(1024)

        ns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ns_sock.connect((ns_host, 53))
        ns_sock.sendall(data)
        answer = ns_sock.recv(1024)
        ns_sock.close()

        (header, queries, answers,
         authorities, additional) = PackerParser.parse_response(answer)

        response = PacketBuilder.build(header, queries, answers, authorities,
                                       additional)
        sock.sendto(response, addr)
except KeyboardInterrupt:
    logger.info('Stopping the server')
finally:
    sock.close()
