# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import struct
from LocalUtil import BinIFace

class BinWriter:
    def __init__(self, filepath, overwrite = False):
        mode = 'xb'
        if overwrite:
            mode = 'wb'
        self.file_handle = open(filepath, mode)
        self.s_u8 = struct.Struct("<B")
        self.s_i32 = struct.Struct("<i")
        self.s_u32 = struct.Struct("<I")
        self.s_i64 = struct.Struct("<q")
        self.s_u64 = struct.Struct("<Q")
        self.s_float = struct.Struct("<f")
        self.s_double = struct.Struct("<d")
        self.pos_stack = []

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def get_path(self):
        return self.file_handle.name

    def flush(self):
        self.file_handle.flush()

    def close(self):
        if self.file_handle is not None:
            self.file_handle.close()
        self.file_handle = None

    def tell(self):
        return self.file_handle.tell()

    def push_pos(self, pos):
        c = self.tell()
        self.pos_stack.append(c)
        self.file_handle.seek(pos)

    def pop_pos(self):
        if len(self.pos_stack) == 0:
            return
        n = self.pos_stack.pop()
        self.file_handle.seek(n)

    def write_raw(self, bstr, pos=None):
        if pos is not None:
            self.push_pos(pos)
        self.file_handle.write(bstr)
        if pos is not None:
            self.pop_pos()

    def write(self, data, pos=None):
        # Have to test bool before int since bool is also an int
        if isinstance(data, bool):
            self.write_bool(data, pos=pos)
        elif isinstance(data, str):
            self.write_str(data, pos=pos)
        elif isinstance(data, int):
            self.write_i32(data, pos=pos)
        elif isinstance(data, float):
            self.write_float(data, pos=pos)
        elif isinstance(data, BinIFace):
            self.write_BinIFace(data, pos=pos)
        else:
            raise TypeError("Unhandled type: {}".format(type(data)))

    def write_i32(self, i, pos=None):
        b = self.s_i32.pack(int(i))
        self.write_raw(b, pos=pos)

    def write_u32(self, i, pos=None):
        b = self.s_u32.pack(int(i))
        self.write_raw(b, pos=pos)

    def write_i64(self, i, pos=None):
        b = self.s_i64.pack(int(i))
        self.write_raw(b, pos=pos)

    def write_u64(self, i, pos=None):
        b = self.s_u64.pack(int(i))
        self.write_raw(b, pos=pos)

    def write_u8(self, c, pos=None):
        v = int(c)
        if (v > 255):
            raise TypeError("Cannot encode value > 255 as a u8! " +
                            "Got: {}".format(v))
        b = self.s_u8.pack(v)
        self.write_raw(b, pos=pos)

    def write_float(self, f, pos=None):
        b = self.s_float.pack(f)
        self.write_raw(b, pos=pos)

    def write_double(self, f, pos=None):
        b = self.s_double.pack(f)
        self.write_raw(b, pos=pos)

    def write_bool(self, b, pos=None):
        self.write_u8(int(b), pos=pos)

    def _write_7bit_encoded_int(self, val):
        # These strings are written/read using C#'s BinaryReader and
        # BinaryWriter classes. They prefix strings using an int32
        # length that's been encoded as a series of 7-bit values with
        # the high-bit denoting if the next byte is also part of the
        # value.
        #
        # These values are encoded with a max of 5 bytes.
        if val < 0:
            raise ValueError('Cannot encode a negative string length!')
        while val >= 0x80:
            self.write_u8((val | 0x80) & 0xff)
            val >>= 7
        self.write_u8(val & 0xff)

    def write_binstr(self, b, pos=None):
        if pos is not None:
            self.push_pos(pos)
        self._write_7bit_encoded_int(len(b))
        self.write_raw(b)
        if pos is not None:
            self.pop_pos()

    def write_str(self, s, pos=None):
        # XXX: We're really just guessing that this is ASCII.
        self.write_binstr(s.encode('ascii'), pos=pos)

    def write_list(self, l, pos=None):
        if pos is not None:
            self.push_pos(pos)
        for i in l:
            self.write(i)
        if pos is not None:
            self.pop_pos()

    def write_BinIFace(self, bif, pos=None):
        if pos is not None:
            self.push_pos(pos)
        bif.toBinary(self)
        if pos is not None:
            self.pop_pos(pos)

# vim:ts=4:sw=4:et
