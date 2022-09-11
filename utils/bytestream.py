from typing import Callable


class ByteStream:
    loader: Callable[[], bytes]
    cursor: int
    buffer: bytes
    
    def __init__(self, loader) -> None:
        self.loader = loader
        self.cursor = 0
        self.buffer = b""

    def next(self, step: int = 1) -> None:
        self.cursor += step

    def load(self) -> bytes:
        loaded = self.loader()
        self.buffer += loaded
        # print(loaded)

    def loaduntil(self, until: bytes) -> bytes:
        while 1:
            idx = self.buffer.find(until, self.cursor)
            if idx == -1:
                self.load()
            else:
                break
        endidx = idx+len(until)
        rtn = self.buffer[self.cursor:endidx]
        self.cursor = endidx
        return rtn

    def loadlength(self, length: int) -> bytes:
        while len(self.buffer) < self.cursor + length:
            self.load()
        rtn = self.buffer[self.cursor:self.cursor+length]
        self.cursor += length
        return rtn