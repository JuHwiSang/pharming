from network.endpoint import Client, Server
from utils.debug_save import debug_save

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

    def connect_to(self, host: tuple) -> Server:
        try:
            return Server(default_context.wrap_socket(socket.create_connection((host, 443)), server_hostname=host))
        except ConnectionRefusedError:
            return Server(socket.create_connection((host, 80)))

    def spoof(self, client: Client) -> None:
        print(f"spoof: {client.sock.getsockname()}")
        with client:
            req = client.recv()
            host = req.header.get(b"Host").decode()

            server = self.connect_to(host)
            with server:
                server.send(req)
                res = server.recv()
                debug_save(res.body.plain_text, "ServerRecv")
            res.body_replace(b"https", b"http")
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



def main():
    Proxy(("", 80)).run()

if __name__ == "__main__":
    main()