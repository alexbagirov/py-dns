import socket
import struct


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 12345))

while True:
    data, addr = sock.recvfrom(1024)
    print(data)
    print(struct.unpack('>H', data[0:2]))
    print(struct.unpack('>H', data[2:4]))
    print(struct.unpack('>H', data[4:6]))
    print(struct.unpack('>H', data[6:8]))
    print(struct.unpack('>H', data[8:10]))
    print(struct.unpack('>H', data[10:12]))
    print(struct.unpack('B', data[12:13]))
    print(struct.unpack('cccccc', data[13:19]))
    print(struct.unpack('B', data[19:20]))
    print(struct.unpack('>H', data[20:22]))
    print(struct.unpack('>H', data[22:24]))



