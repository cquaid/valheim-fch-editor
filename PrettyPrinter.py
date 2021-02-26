# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import binascii
import struct

class PPWrap:
    def __init__(self, pp, label=None):
        self.label = label
        self.pp = pp

    def __enter__(self):
        self.pp.block(self.label)
        return self.pp

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.pp.end_block()


class PrettyPrinter:
    def __init__(self):
        self.indent_lvl = 0
        self.s_u32 = struct.Struct("<I")
        self.s_float = struct.Struct("<f")

    def block(self, s = None):
        if (s is not None):
            l = 78 - len(s) - (2 * self.indent_lvl)
            if (l <= 0):
                l = 6
            self.println("{} {}".format(s, "-" *  l))
        self.indent_lvl += 1

    def end_block(self):
        if self.indent_lvl != 0:
            self.indent_lvl -= 1

    def indent(self):
        print("  " * self.indent_lvl, end='')

    def println(self, first, *args):
        self.indent()
        print(first, end='')
        for a in args:
            print(' ', a, sep='', end='')
        print('')

    def small_bytes(self, prefix, b):
        if (len(b) > 4):
            self.bytes(prefix, b)
            return
        s = binascii.hexlify(b).decode('ascii')
        self.indent()
        print(prefix, ": {", sep='', end='')
        i = 0;
        while (i < len(b)):
            print(" ", s[i*2:(i*2)+2], sep='', end='')
            i += 1
        print(" }")

    def bytes(self, prefix, b):
        if (len(b) <= 4):
            self.small_bytes(prefix, b)
            return
        self.indent()
        print(prefix, ":", sep='')
        self.block()
        i = 0
        offset = 0
        s = binascii.hexlify(b).decode('ascii')
        chunks = (len(s) & ~15)
        while (i < chunks):
            self.indent()
            print("{0:06x}: ".format(offset), end='')
            print(s[i+0:i+2], s[i+2:i+4], s[i+4:i+6], s[i+6:i+8], end='')
            print('', s[i+8:i+10], s[i+10:i+12], s[i+12:i+14], s[i+14:i+16])
            i += 16
            offset += 8
        if (i < len(s)):
            self.indent()
            print("{0:06x}:".format(offset), end='')
            o = 0
            while (i < len(s)):
                print(' ', s[i:i+2], sep='', end='')
                i += 2
            print('')
        self.end_block()

    def print_a4(self, prefix, b):
        i = self.s_u32.unpack(b)[0]
        f = self.s_float.unpack(b)[0]
        s = binascii.hexlify(b).decode('ascii')
        self.indent()
        print(prefix, ": { ", sep='', end='')
        print(s[0:2], s[2:4], s[4:6], s[6:8], "}", end='')
        print(" i:({}) f:({})".format(i, f))

# vim:ts=4:sw=4:et
