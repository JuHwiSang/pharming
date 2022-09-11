from typing import Callable

import gzip


str2compress: dict[bytes, Callable[[bytes], bytes]] = {
    b"gzip": gzip.compress,
    b"identity": lambda x:x
}

str2decompress: dict[bytes, Callable[[bytes], bytes]] = {
    b"gzip": gzip.decompress,
    b"identity": lambda x:x
}


def compress(data: bytes, encoding: str) -> bytes:
    return str2compress[encoding](data)

def decompress(data: bytes, encoding: str) -> bytes:
    return str2decompress[encoding](data)