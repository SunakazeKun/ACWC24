import struct


def align8(val: int) -> int:
    return val + (8 - val & 7)


def align16(val: int) -> int:
    return val + (16 - val & 15)


def align32(val: int) -> int:
    return val + (32 - val & 31)


def align64(val: int) -> int:
    return val + (64 - val & 63)


def get_int8(data, off: int) -> int:
    return data[off]


def get_uint8(data, off: int) -> int:
    return data[off] & 0xFF


def get_int16(data, off: int) -> int:
    return struct.unpack_from(">h", data, off)[0]


def get_uint16(data, off: int) -> int:
    return struct.unpack_from(">H", data, off)[0]


def get_int24(data, off: int) -> int:
    orbits = ~0xFFFFFF if data[off] & 0x80 else 0
    return get_uint24(data, off) | orbits


def get_uint24(data, off: int) -> int:
    return (data[off] & 0xFF) << 16 | (data[off+1] & 0xFF) << 8 | (data[off+2] & 0xFF)


def get_int32(data, off: int) -> int:
    return struct.unpack_from(">i", data, off)[0]


def get_uint32(data, off: int) -> int:
    return struct.unpack_from(">I", data, off)[0]


def get_int64(data, off: int) -> int:
    return struct.unpack_from(">q", data, off)[0]


def get_uint64(data, off: int) -> int:
    return struct.unpack_from(">Q", data, off)[0]


def get_float32(data, off: int) -> int:
    return struct.unpack_from(">f", data, off)[0]


def get_float64(data, off: int) -> int:
    return struct.unpack_from(">d", data, off)[0]


def get_bool(data, off: int) -> bool:
    return data[off] != 0


def get_bytes(data, off: int, size: int) -> bytes:
    return data[off:off+size]


def get_string(data, off: int, charset: str = "ascii") -> str:
    return data[off:data.find(0x00, off)].decode(charset)


def put_int8(data, off: int, val: int):
    data[off] = val


def put_uint8(data, off: int, val: int):
    data[off] = val & 0xFF


def put_int16(data, off: int, val: int):
    struct.pack_into(">h", data, off, val)


def put_uint16(data, off: int, val: int):
    struct.pack_into(">H", data, off, val)


def put_int24(data, off: int, val: int):
    put_bytes(data, off, struct.pack(">i", val)[1:])


def put_uint24(data, off: int, val: int):
    put_bytes(data, off, struct.pack(">I", val)[1:])


def put_int32(data, off: int, val: int):
    struct.pack_into(">i", data, off, val)


def put_uint32(data, off: int, val: int):
    struct.pack_into(">I", data, off, val)


def put_int64(data, off: int, val: int):
    struct.pack_into(">q", data, off, val)


def put_uint64(data, off: int, val: int):
    struct.pack_into(">Q", data, off, val)


def put_float32(data, off: int, val: int):
    struct.pack_into(">f", data, off, val)


def put_float64(data, off: int, val: int):
    struct.pack_into(">d", data, off, val)


def put_bool(data, off: int, val: bool):
    data[off] = 1 if val else 0


def put_bytes(data, off: int, val):
    for i in range(len(val)):
        data[off + i] = val[i]
