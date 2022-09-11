


def encode_header(data: bytes) -> dict[bytes, bytes]:
    header = {}
    data = data.strip()
    for line in data.split(b"\r\n"):
        key, _, value = line.partition(b":")
        header[key.strip()] = value.strip()
    return header

def decode_header(header: dict[bytes, bytes]) -> bytes:
    return b"\r\n".join(key+b": "+value for key, value in header.items())