from tools.bitconv import *

U8_MAGIC = 0x55AA382D
NODE_SIZE = 0xC
ROOT_OFFSET = 0x20


class _U8Node:
    def __init__(self):
        self.isDir = False
        self.offName = 0
        self.offData = 0
        self.lenData = 0

    @staticmethod
    def unpack(buf, off):
        e = _U8Node()
        e.isDir = get_bool(buf, off + 0x00)
        e.offName = get_uint24(buf, off + 0x01)
        e.offData = get_uint32(buf, off + 0x04)
        e.lenData = get_uint32(buf, off + 0x08)
        return e

    def pack(self) -> bytes:
        b = bytearray(NODE_SIZE)
        put_bool(b, 0x00, self.isDir)
        put_uint24(b, 0x01, self.offName)
        put_uint32(b, 0x04, self.offData)
        put_uint32(b, 0x08, self.lenData)
        return bytes(b)


class U8:
    def __init__(self):
        self._files = {}

    def load(self, buf):
        if not buf:
            return

        if get_uint32(buf, 0x00) != U8_MAGIC:
            raise Exception("Error: Buffer does not contain U8 data.")

        offroot = get_uint32(buf, 0x04)
        lennodes = get_uint32(buf, 0x08)
        offdata = get_uint32(buf, 0x0C)

        rootnode = _U8Node.unpack(buf, offroot)
        nodes = [_U8Node.unpack(buf, offroot + NODE_SIZE * (i + 1)) for i in range(rootnode.lenData - 1)]
        stringspos = offroot + rootnode.lenData * NODE_SIZE

        recursion = [rootnode.lenData]
        recursiondir = []
        counter = 0
        for node in nodes:
            counter += 1
            name = get_string(buf, stringspos + node.offName, "latin-1")

            if node.isDir:
                path = '/'.join(recursiondir + [name])
                recursion.append(node.lenData)
                recursiondir.append(name)
                self._files[path] = None
            else:
                path = '/'.join(recursiondir + [name])
                data = buf[node.offData:node.offData + node.lenData]
                self._files[path] = data

            if len(recursiondir):
                sz = recursion.pop()
                if sz != counter + 1:
                    recursion.append(sz)
                else:
                    recursiondir.pop()

    def save(self):
        buf = bytearray(0x20)
        put_uint32(buf, 0x00, U8_MAGIC)
        put_uint32(buf, 0x04, ROOT_OFFSET)

        rootnode = _U8Node()
        rootnode.isDir = True
        nodes = [rootnode]
        strings = bytearray(1)
        fulldata = bytearray()
        paths = self.get_paths()

        for path in paths:
            data = self._files[path]
            node = _U8Node()
            node.isDir = data is None
            node.offName = len(strings)

            name = path.split('/')[-1]
            strings += (name + "\0").encode("latin-1")

            recursion = path.count('/')
            if recursion < 0:
                recursion = 0

            if node.isDir:
                node.offData = recursion
                node.lenData = len(nodes)
                for subpath in paths:
                    if subpath[:len(path)] == path:
                        node.lenData += 1
            else:
                node.offData = len(fulldata)
                node.lenData = len(data)
                fulldata += data + bytearray(align32(node.lenData) - node.lenData)

            nodes.append(node)

        lennodes = NODE_SIZE * len(nodes) + len(strings)
        offdata = align32(ROOT_OFFSET + lennodes)
        rootnode.lenData = len(nodes)

        put_uint32(buf, 0x08, lennodes)
        put_uint32(buf, 0x0C, offdata)

        for node in nodes:
            if not node.isDir:
                node.offData += offdata
            buf += node.pack()

        buf += strings
        buf += bytearray(offdata - lennodes - ROOT_OFFSET)
        buf += fulldata

        return bytes(buf)

    def get_paths(self):
        return sorted(list(self._files.keys()))

    def get_file(self, path):
        if path in self._files:
            return self._files[path]
        else:
            return None

    def add_dir(self, path):
        self._files[path] = None

    def add_file(self, path, data):
        self._files[path] = data
