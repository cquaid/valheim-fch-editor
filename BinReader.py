# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import struct

class BinReader:
    file_handle = None
    s_u8 = None
    s_u32_le = None
    s_float = None

    def __init__(self, filepath):
        self.file_handle = open(filepath, mode='rb')
        self.s_u8 = struct.Struct("<B")
        self.s_u32_le = struct.Struct("<I")
        self.s_float = struct.Struct("<f")

    def __del__(self):
        self.close()

    def close(self):
        if (self.file_handle is not None):
            self.file_handle.close()
        self.file_handle = None

    def skip(self, count):
        self.file_handle.tell()
        self.file_handle.seek(count, 1)

    def read(self, count):
        return self.file_handle.read(count)

    def read_u32_le(self):
        b = self.read(4)
        return self.s_u32_le.unpack(b)[0]

    def read_u8(self):
        b = self.read(1)
        return self.s_u8.unpack(b)[0]

    def read_float(self):
        b = self.read(4)
        return self.s_float.unpack(b)[0]

    def read_str(self):
        b = self.read(1)
        count = self.s_u8.unpack(b)[0]
        if count == 0:
            return ""
        b = self.read(count)
        return b.decode('ascii')

# vim:ts=4:sw=4:et
