import os


def read_file(filepath: str):
    if not os.path.isfile(filepath):
        return None

    with open(filepath, "rb") as f:
        return f.read()


def write_file(filepath: str, data):
    with open(filepath, "wb") as f:
        f.write(data)
        f.flush()
