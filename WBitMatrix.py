# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import array

class WBitMatrix:
    """
    World Bit Matrix: a lazy way of handling FCH world visibility data.

    Premise:
      Row: Packed 8-bit bytes in a python array, each bit being a column.
      Array of Rows: the whole matrix dealeo

    Other optimizations:
      "Reversable" to translate between top-down indexing of the rows to
      bottom-up indexing. This solves the issue of converting between the
      world data (as seen on disk) and how the PBM needs it ordered.
    """
    def __init__(self, w=0, h=0):
        self.set_dimensions(w, h)

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def set_dimensions(self, w, h):
        self.width = w
        self.height = h

        self.bytes_per_row = (w >> 3)
        if (w & 7) != 0:
            self.bytes_per_row += 1

        self.rows = []
        for r in range(h):
            a = array.array("B")
            for c in range(w):
                a.append(0)
            self.rows.append(a)
        return

    def _set(self, x, y, value):
        byte_index = (x >> 3)
        bit = (1 << (x & 7))

        if value == 0:
            self.rows[y][byte_index] &= ~bit
        else:
            self.rows[y][byte_index] |= bit
        return

    def set(self, x, y, value, flipped=False):
        if (x < 0) or (x >= self.width):
            raise ValueError("Column index", x, "is out of range")
        if (y < 0) or (y >= self.height):
            raise ValueError("Row index", y, "is out of range")
        if (value < 0) or (value > 1):
            raise ValueError("Value", value, "is not a single bit")
        if flipped:
            y = (self.height - y - 1)
        self._set(x, y, value)

    def _get(self, x, y):
        byte_index = (x >> 3)
        bit_index = (x & 7)
        bit = (1 << bit_index)
        return ((self.rows[y][byte_index] & bit) >> bit_index)

    def get(self, x, y, flipped=False):
        if (x < 0) or (x >= self.width):
            raise ValueError("Column index", x, "is out of range")
        if (y < 0) or (y >= self.height):
            raise ValueError("Row index", y, "is out of range")
        if flipped:
            y = (self.height - y - 1)
        return self._get(x, y)

    def fromBinary(self, binrdr):
        """
        1 byte per bit
        """
        # XXX: We could definitly optimize this
        for y in range(self.height):
            b = binrdr.read(self.width)
            for x in range(self.width):
                self._set(x, y, b[x])
        return

    def toBinary(self, binwr):
        """
        1 byte per bit
        """
        # XXX: We could definitly optimize this
        for y in range(self.height):
            for x in range(self.width):
                binwr.write_u8(self._get(x, y))
        return

# vim:ts=4:sw=4:et
