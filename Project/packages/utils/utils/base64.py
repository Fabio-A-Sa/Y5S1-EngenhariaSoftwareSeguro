import base64

ENCODING = "utf-8"

def to_base64(b: bytes | str) -> bytes:
    data = b.encode(ENCODING) if isinstance(b, str) else b
    return base64.b64encode(data)

def to_base64_as_str(b: bytes | str) -> str:
    return to_base64(b).decode(ENCODING)

def from_base64(b64: bytes | str) -> bytes:
    data = b64.encode(ENCODING) if isinstance(b64, str) else b64
    return base64.b64decode(data)

def from_base64_as_str(b64: bytes | str) -> str:
    return from_base64(b64).decode(ENCODING)
