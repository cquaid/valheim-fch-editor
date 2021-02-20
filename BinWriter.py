# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import struct

class BinWriter:
    file_handle = None
    s_u8 = None
    s_u32_le = None
    s_float = None

    def __init__(self, filepath, overwrite = False):
        mode = 'xb'
        if overwrite:
            mode = 'wb'
        self.file_handle = open(filepath, mode)
        self.s_u8 = struct.Struct("<B")
        self.s_u32_le = struct.Struct("<I")
        self.s_float = struct.Struct("<f")

    def __del__(self):
        self.close()

    def close(self):
        if (self.file_handle is not None):
            self.file_handle.close()
        self.file_handle = None

    def write(self, bstr):
        self.file_handle.write(bstr)

    def write_u32_le(self, i):
        b = self.s_u32_le.pack(int(i))
        self.write(b)

    def write_u8(self, c):
        v = int(c)
        if (v > 255):
            raise TypeError("Cannot encode value > 255 as a u8! " +
                            "Got: {}".format(v))
        b = self.s_u8.pack(v)
        self.write(b)

    def write_float(self, f):
        b = self.s_float.pack(f)
        self.write(b)

    def write_str(self, s):
        # XXX: We're really just guessing that this is ascii.
        self.write_u8(len(s))
        self.write(s.encode('ascii'))

# vim:ts=4:sw=4:et
