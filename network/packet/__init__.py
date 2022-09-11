from utils.compress import compress, decompress
from utils.debug_save import debug_save
from network.packet.parse import decode_header, encode_header
from .helper import chunk_lengths_reduce

from typing import Optional


class Packet:

    class StartLine:
        version: bytes

        def __init__(self, data: bytes) -> None:
            raise NotImplementedError("Can't use Packet.Startline, use overrided method")

        def to_bytes(self) -> bytes:
            raise NotImplementedError("Can't use Packet.Startline, use overrided method")


    class Header:
        header: dict[bytes, bytes]

        def __init__(self, data: bytes) -> None:
            self.header = encode_header(data)

        def set(self, key: bytes, value: bytes) -> None:
            self.header[key] = value

        def get(self, key: bytes, default: bytes = b"") -> bytes:
            return self.header.get(key, default)

        def __contains__(self, element) -> bool:
            return element in self.header

        def items(self):
            return self.header.items()

        def to_bytes(self) -> bytes:
            return decode_header(self.header)


    class Body:
        encoding: str
        plain_text: bytes

        def __init__(self, data: bytes, encoding: str, isencoded: bool = True) -> None:
            self.encoding = encoding
            if isencoded:
                self.plain_text = decompress(data, encoding)
            else:
                self.plain_text = data

        def replace(self, befo: bytes, aft: bytes) -> "Packet.Body":
            data = self.plain_text.replace(befo, aft)
            return self.__class__(data, self.encoding, isencoded = False)

        def to_bytes(self) -> bytes:
            return compress(self.plain_text, self.encoding)


    startline: StartLine
    header: Header
    body: Body

    def __init__(self, startline, header, body) -> None:
        self.startline = startline
        self.header = header
        self.body = body

    def body_replace(self, befo: bytes, aft: bytes) -> None:
        raise NotImplementedError("Can't use Packet.Startline, use overrided method")

    def to_bytes(self) -> bytes:
        return self.startline.to_bytes() + b"\r\n" + self.header.to_bytes() + b"\r\n\r\n" + self.body.to_bytes()


class Request(Packet):

    class StartLine(Packet.StartLine):
        method: bytes
        path: bytes

        def __init__(self, data: bytes) -> None:
            self.method, _, other = data.partition(b" ")
            self.path, _, self.version = other.partition(b" ")

        def to_bytes(self) -> bytes:
            return self.method + b" " + self.path + b" " + self.version

    def body_replace(self, befo: bytes, aft: bytes) -> None:
        self.body = self.body.replace(befo, aft)
        # self.header.set(b"Content-Length", str(len(self.body.to_bytes())).encode())

    def header_replace(self, befo: bytes, aft: bytes) -> None:
        for key, value in self.header.items():
            self.header.set(key, value.replace(befo, aft))

    def to_bytes(self) -> bytes:
        body_bytes = self.body.to_bytes()
        if b"Content-Length" in self.header:
            self.header.set(b"Content-Length", str(len(body_bytes)).encode())
        return self.startline.to_bytes() + b"\r\n" + self.header.to_bytes() + b"\r\n\r\n" + body_bytes


class Response(Packet):

    class StartLine(Packet.StartLine):
        status: bytes
        msg: bytes

        def __init__(self, data: bytes) -> None:
            self.version, _, other = data.partition(b" ")
            self.status, _, self.msg = other.partition(b" ")
            
        def to_bytes(self) -> bytes:
            return self.version + b" " + self.status + b" " + self.msg


    class ChunkedBody(Packet.Body):
        chunk_lengths: None | list[int]

        def __init__(self, data: bytes, encoding: str, isencoded: bool = True, chunk_lengths: Optional[list[int]] = None) -> None:
            self.chunk_lengths = chunk_lengths
            super().__init__(data, encoding, isencoded)

        def ischunked(self) -> bool:
            return True if isinstance(self.chunk_lengths, list) else False

        def to_bytes(self) -> bytes:
            data = super().to_bytes()
            chunk_lengths = chunk_lengths_reduce(self.chunk_lengths, len(data))
            cursor = 0
            rtn = b""
            for length in chunk_lengths:
                chunk = data[cursor:cursor+length]
                cursor += length
                rtn += hex(length)[2:].encode() + b"\r\n" + chunk + b"\r\n"
            return rtn

        def replace(self, befo: bytes, aft: bytes) -> "Packet.Body":
            data = self.plain_text.replace(befo, aft)
            # chunk_lengths = chunk_lengths_reduce(self.chunk_lengths, len(data))
            # return self.__class__(data, self.encoding, False, chunk_lengths)
            debug_save(data, "chunkedreplace")
            return self.__class__(data, self.encoding, False, self.chunk_lengths)


    def body_replace(self, befo: bytes, aft: bytes) -> None:
        self.body = self.body.replace(befo, aft)

    def to_bytes(self) -> bytes:
        body_bytes = self.body.to_bytes()
        # if not is_chunk(self.startline.version, self.header.header):
        if b"Content-Length" in self.header:
            self.header.set(b"Content-Length", str(len(body_bytes)).encode())
        return self.startline.to_bytes() + b"\r\n" + self.header.to_bytes() + b"\r\n\r\n" + body_bytes



def is_chunk(version: bytes, header: Packet.Header) -> bool:
    return (((not b"Content-Length" in header) and (version != b"HTTP/1.0")) or b"Transfer-Encoding" in header)