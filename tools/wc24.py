import os
import pyaes
import rsa

from tools.bitconv import get_uint32, get_bytes, put_uint8, put_uint32, put_bytes
from tools.files import read_file

WC24_MAGIC = 0x57433234
WC24_HEADER_SIZE = 0x30
INIT_VECTOR_OFFSET = 0x30
INIT_VECTOR_SIZE = 16
SIGNATURE_OFFSET = 0x40
SIGNATURE_SIZE = 256
DATA_OFFSET = 0x140

RSA_KEY = read_file("rvforestdl.pem.bin")
AES_KEY = read_file("rvforestdl.aes.bin")


def is_wc24_keys_available() -> bool:
    return RSA_KEY and AES_KEY


def decrypt(data) -> bytes:
    if not is_wc24_keys_available():
        raise Exception("RSA-AES keys not initialized. Can't decrypt data.")
    if get_uint32(data, 0x00) != WC24_MAGIC:
        raise Exception("Error: No WC24 data given. Can't extract U8 data.")

    iv = get_bytes(data, INIT_VECTOR_OFFSET, INIT_VECTOR_SIZE)
    aes = pyaes.AESModeOfOperationOFB(AES_KEY, iv=iv)

    return aes.decrypt(data[DATA_OFFSET:])


def encrypt(data) -> bytes:
    if not is_wc24_keys_available():
        raise Exception("RSA-AES keys not initialized. Can't encrypt data.")

    privkey = rsa.PrivateKey.load_pkcs1(RSA_KEY, "PEM")
    signature = rsa.sign(data, privkey, "SHA-1")
    iv = os.urandom(INIT_VECTOR_SIZE)
    aes = pyaes.AESModeOfOperationOFB(AES_KEY, iv=iv)
    encrypted = aes.encrypt(data)

    outdata = bytearray(WC24_HEADER_SIZE + INIT_VECTOR_SIZE + SIGNATURE_SIZE + len(encrypted))
    put_uint32(outdata, 0x00, WC24_MAGIC)
    put_uint32(outdata, 0x04, 1)
    put_uint8(outdata, 0x0C, 1)
    put_bytes(outdata, INIT_VECTOR_OFFSET, iv)
    put_bytes(outdata, SIGNATURE_OFFSET, signature)
    put_bytes(outdata, DATA_OFFSET, encrypted)

    return bytes(outdata)
