# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import struct
from LocalUtil import *

class BinReader:
    def __init__(self, filepath):
        self.file_handle = open(filepath, mode='rb')
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

    def close(self):
        if self.file_handle is not None:
            self.file_handle.close()
        self.file_handle = None

    def skip(self, count):
        self.file_handle.seek(count, 1)

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

    def read(self, count, pos=None):
        if pos is None:
            return self.file_handle.read(count)
        self.push_pos(pos)
        ret = self.file_handle.read(count)
        self.pop_pos()
        return ret

    def _multi_read(self, fn, count, pos):
        if pos is not None:
            self.push_pos(pos)
        ret = []
        for i in range(count):
            ret.append(fn())
        if pos is not None:
            self.pop_pos()
        return ret

    def _i32_single(self, pos=None):
        b = self.read(4, pos=pos)
        return self.s_i32.unpack(b)[0]

    def read_i32(self, count=None, pos=None):
        if count is None:
            return self._i32_single(pos=pos)
        return self._multi_read(self._i32_single, count, pos)

    def _u32_single(self, pos=None):
        b = self.read(4, pos=pos)
        return self.s_u32.unpack(b)[0]

    def read_u32(self, count=None, pos=None):
        if count is None:
            return self._u32_single(pos=pos)
        return self._multi_read(self._u32_single, count, pos)

    def _i64_single(self, pos=None):
        b = self.read(8, pos=pos)
        return self.s_i64.unpack(b)[0]

    def read_i64(self, count=None, pos=None):
        if count is None:
            return self._i64_single(pos=pos)
        return self._multi_read(self._i64_single, count, pos)

    def _u64_single(self, pos=None):
        b = self.read(8, pos=pos)
        return self.s_u64.unpack(b)[0]

    def read_u64(self, count=None, pos=None):
        if count is None:
            return self._u64_single(pos=pos)
        return self._multi_read(self._u64_single, count, pos)

    def _float_single(self, pos=None):
        b = self.read(4, pos=pos)
        return self.s_float.unpack(b)[0]

    def read_float(self, count=None, pos=None):
        if count is None:
            return self._float_single(pos)
        return self._multi_read(self._float_single, count, pos)

    def _float_double(self, pos=None):
        b = self.read(8, pos=pos)
        return self.s_double.unpack(b)[0]

    def read_double(self, count=None, pos=None):
        if count is None:
            return self._double_single(pos)
        return self._multi_read(self._double_single, count, pos)

    def _u8_single(self, pos=None):
        b = self.read(1, pos=pos)
        return b[0]

    def read_u8(self, count=None, pos=None):
        if count is None:
            return self._u8_single(pos=pos)
        return self._multi_read(self._u8_single, count, pos)

    def _bool_single(self, pos=None):
        v = self.read_u8(pos=pos)
        return bool(v)

    def read_bool(self, count=None, pos=None):
        if count is None:
            return self._bool_single(pos=pos)
        return self._multi_read(self._bool_single, count, pos)

    def _read_7bit_encoded_int(self):
        # These strings are written/read using C#'s BinaryReader and
        # BinaryWriter classes. They prefix strings using an int32
        # length that's been encoded as a series of 7-bit values with
        # the high-bit denoting if the next byte is also part of the
        # value.
        #
        # These values are encoded with a max of 5 bytes.
        count = 0
        shift = 0
        while True:
            if shift >= (5 * 7):
                die("Too many bytes (> 5) present in disk string length.")
            b = self.read_u8()
            count |= (b & 0x7f) << shift
            shift += 7
            if (b & 0x80) == 0:
                break
        return count

    def _binstr_single(self, pos=None):
        if pos is not None:
            self.push_pos(pos)
        slen = self._read_7bit_encoded_int()
        if slen == 0:
            ret = b''
        else:
            ret = self.read(slen)
        if pos is not None:
            self.pop_pos()
        return ret

    def read_binstr(self, count=None, pos=None):
        if count is None:
            return self._binstr_single(pos=pos)
        return self._multi_read(self._binstr_single, count, pos)

    def _str_single(self, pos=None):
        return self._binstr_single(pos=pos).decode('ascii')

    def read_str(self, count=None, pos=None):
        if count is None:
            return self._str_single(pos=pos)
        return self._multi_read(self._str_single, count, pos)

# vim:ts=4:sw=4:et
