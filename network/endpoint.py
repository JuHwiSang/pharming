from utils.bytestream import ByteStream
from .packet import is_chunk
from .packet import Packet, Request, Response
from .packet.save import Save

from typing_extensions import Self
import socket



save = Save()

class Endpoint:
    sock: socket.socket
    def __init__(self, sock: socket.socket) -> None:
        self.sock = sock

    def recv(self) -> Packet:
        raise NotImplementedError("Can't use Endpoint.recv, use overrided method")

    def send(self, pkt: Packet) -> None:
        raise NotImplementedError("Can't use Endpoint.recv, use overrided method")

    def close(self) -> None:
        self.sock.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *a, **k) -> None:
        self.close()


class Client(Endpoint):
    def recv(self) -> Request:
        # print("try recv")
        stream = ByteStream(lambda:self.sock.recv(1024))
        load = stream.loaduntil(b"\r\n\r\n")
        startline_bytes, _, header_bytes = load.partition(b"\r\n")
        startline = Request.StartLine(startline_bytes)
        header = Request.Header(header_bytes)
        encoding = header.get(b"Content-Encoding", b"identity")
        content_length = int(header.get(b"Content-Length", b"0"))
        body_bytes = stream.loadlength(content_length)
        body = Request.Body(body_bytes, encoding)
        request = Request(startline, header, body)
        save(stream.buffer, "ClientRecv")
        return request

    def send(self, pkt: Packet) -> None:
        # print("try send")
        data = pkt.to_bytes()
        self.sock.sendall(data)
        save(data, "ClientSend")


class Server(Endpoint):
    def recv(self) -> Response:
        # print("try recv")
        stream = ByteStream(lambda:self.sock.recv(1024))
        load = stream.loaduntil(b"\r\n\r\n")
        startline_bytes, _, header_bytes = load.partition(b"\r\n")
        # print("check2")
        startline = Response.StartLine(startline_bytes)
        header = Response.Header(header_bytes)
        encoding = header.get(b"Content-Encoding", b"identity")
        if startline.status[0] != ord('3') and is_chunk(startline.version, header):
            # print("chunk")
            # breakpoint()
            chunk_lengths: list[int] = []     # 청크의 길이를 담는 리스트. 인코딩 시 필요
            body_bytes = b""
            while 1:
                length = int(stream.loaduntil(b"\r\n"), 16)
                chunk = stream.loadlength(length)
                chunk_lengths.append(length)
                body_bytes += chunk
                if length == 0:
                    break
                stream.next(2)
            body = Response.ChunkedBody(body_bytes, encoding, chunk_lengths=chunk_lengths)
        else:
            # print("not chunk")
            # breakpoint()
            content_length = int(header.get(b"Content-Length", b"0"))
            body_bytes = stream.loadlength(content_length)
            body = Response.Body(body_bytes, encoding)

        response = Response(startline, header, body)
        save(stream.buffer, "ServerRecv")
        return response

    def send(self, pkt: Packet) -> None:
        # print("try send")
        data = pkt.to_bytes()
        self.sock.sendall(data)
        save(data, "ServerSend")