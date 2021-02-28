# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT

import WBitMatrix
from LocalUtil import die

def _consume_ws(f):
    got_ws = False
    while True:
        c = f.read(1)
        # If it's one of the valid whitespace files for PBM, skip it
        if c in " \t\r\n":
            got_ws = True
            continue
        # If we get a comment character, eat the line
        if c == '#':
            f.readline()
            # The newline counts as whitespace
            got_ws = True
            continue
        # Non-whitespace. Return that.
        return (c, got_ws)
    # while

def _get_integer(f, first=None):
    val = ''
    # Eat initial whitespace if we need to
    if first is None:
        t = _consume_ws(f)
        first = t[0]
    val += first

    while True:
        c = f.read(1)
        if c in '0123456789':
            val += c
            continue

        if c in " \t\r\n":
            break
        if c == '#':
            f.readline()
            break
        # Anything else is an error
        die("Bad character ({}) in PBM integer".format(c))
    return int(val)

def _get_pixel(f, first=None):
    # Eat initial whitespace if we need to
    if first is None:
        t = _consume_ws(f)
        first = t[0]
    # Validate that first is a bit.
    if first in '01':
        return int(first)
    die("Bad character ({}) in PBM pixel".format(first))


class PBMImage:
    def __init__(self, width=0, height=0):
        self.data = WBitMatrix.WBitMatrix(width, height)

    def get_width(self):
        return self.data.get_width()

    def get_height(self):
        return self.data.get_height()

    def set_pixel(self, x, y, v):
        if (v < 0) or (v > 1):
            die("Cannot set PBM value <0 or >1 (Got: {})".format(v))
        # This will raise if outside of bounds.
        self.data.set(x, y, v, flipped=True)

    def get_pixel(self, x, y):
        return self.data.get(x, y, flipped=True)

    def get_matrix(self):
        return self.data

    def set_matrix(self, wbm):
        self.data = wbm

    def write(self, path, overwrite = False):
        mode = 'x'
        if overwrite:
            mode = 'w'
        with open(path, mode) as f:
            # Header: P1 <width> <height>
            width = self.get_width()
            height = self.get_height()
            f.write("P1\n{} {}\n".format(width, height))
            # Write each row as a new line
            for y in range(height):
                for x in range(width):
                    f.write(str(self.get_pixel(x, y)))
                f.write("\n")
        return

    def load(self, path):
        with open(path, 'r') as f:
            # Check magic
            d = f.read(2)
            if d != 'P1':
                die('File {} is not a PBM'.format(path))
            # Expects a whitespace character
            t = _consume_ws(f)
            if not t[1]:
                die('File {} is not a PBM'.format(path))
            # Get width
            width = _get_integer(f, first = t[0])
            # Get Height, no first character. If we get here, we know the
            # next character after the integer was a space/comment
            height = _get_integer(f)
            # Reset image pixel data
            self.data.set_dimensions(width, height)
            # Load the pixel data (automatically handles whitespace)
            #   Pixels are top-level to bottom-right with columns flowing
            #   left-to-right
            for y in range(height):
                for x in range(width):
                    self.data.set(x, y, _get_pixel(f), flipped=True)
            # PBM parsers are supposed to be lenient so we just ignore any
            # trailing data.
        return

# vim:ts=4:sw=4:et
