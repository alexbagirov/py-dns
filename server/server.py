import logging
import os.path
import pickle
import socket
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta
from itertools import chain
from typing import Tuple, NoReturn, Iterable

from parser import Answer, PacketParser, PacketBuilder


class DNSServer:
    def __init__(self):
        self.logger = logging.getLogger("Server")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(handler)

        self.host, self.port = self.parse_args()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logger.info(f"Starting the server on port {self.port}")
        try:
            self.sock.bind(("127.0.0.1", self.port))
        except PermissionError:
            self.logger.error(
                "Permission error when opening socket on port, " "exiting"
            )
            exit(0)

        self.ttl = {}
        self.data = {}

        if os.path.isfile("ttl.pickle") and os.path.isfile("data.pickle"):
            with open("ttl.pickle", "rb") as f:
                self.ttl = pickle.loads(f.read())
            with open("data.pickle", "rb") as f:
                self.data = pickle.loads(f.read())

    @staticmethod
    def parse_args() -> Tuple[str, int]:
        parser = ArgumentParser()
        parser.add_argument("-p", "--port", type=int, default=53)
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-i", "--ip", type=str, default="1.1.1.1")
        group.add_argument("--use-authoritative", action="store_true")

        args = parser.parse_args()
        if args.use_authoritative:
            host = "199.7.83.42"
        else:
            host = args.ip
        port = args.port
        return host, port

    def query_nameserver(self, name: str, query: bytes):
        ns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ns_sock.connect((self.host, 53))
        ns_sock.sendall(query)
        answer = ns_sock.recv(1024)
        ns_sock.close()

        (header, queries, answers, authorities, additional) = PacketParser.parse(answer)
        self.ttl[name] = self.calculate_ttl(chain(answers, authorities, additional))
        self.data[name] = (answers, authorities, additional)

    @staticmethod
    def calculate_ttl(answers: Iterable[Answer]) -> datetime:
        min_ttl = min(answers, key=lambda f: f.ttl).ttl
        return datetime.now() + timedelta(seconds=min_ttl)

    def run(self) -> NoReturn:
        try:
            while True:
                query, addr = self.sock.recvfrom(1024)

                header, queries, *other = PacketParser.parse(query)
                name = queries[0].name

                if name not in self.ttl or (
                    name in self.ttl and self.ttl[name] < datetime.now()
                ):
                    self.query_nameserver(name, query)

                answers, authorities, additional = self.data[name]
                response = PacketBuilder.build(
                    header, queries, answers, authorities, additional
                )
                self.sock.sendto(response, addr)

        except KeyboardInterrupt:
            self.logger.info("Stopping the server")
            with open("ttl.pickle", "wb") as f:
                f.write(pickle.dumps(self.ttl))
            with open("data.pickle", "wb") as f:
                f.write(pickle.dumps(self.data))
        finally:
            self.sock.close()


if __name__ == "__main__":
    server = DNSServer()
    server.run()
