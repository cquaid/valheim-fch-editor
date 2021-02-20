# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT

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
        raise ValueError("Bad character ({}) in PBM integer".format(c))
    return int(val)

def _get_pixel(f, first=None):
    # Eat initial whitespace if we need to
    if first is None:
        t = _consume_ws(f)
        first = t[0]
    # Validate that first is a bit.
    if first in '01':
        return int(first)
    raise ValueError("Bad character ({}) in PBM pixel".format(first))


class PBMImage:
    width = 0
    height = 0
    rows = []
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height
        if self.height != 0 and self.width != 0:
            for y in range(self.height):
                self.rows.append([])
                for x in range(self.width):
                    self.rows[y].append(0)
        else:
            # If one of them is 0, lazily set both to 0. We'll raise
            # later on during a set or get operation
            self.width = 0
            self.height = 0

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def set_pixel(self, point, v):
        if v > 1:
            raise ValueError("Cannot set PBM value >1 (Got: {})".format(v))
        # This will raise if outside of bounds.
        self.rows[point[1]][point[0]] = v

    def get_pixel(self, point):
        return self.rows[point[1]][point[0]]

    def write(self, path, overwrite = False):
        mode = 'x'
        if overwrite:
            mode = 'w'
        with open(path, mode) as f:
            # Header: P1 <width> <height>
            f.write("P1\n{} {}\n".format(self.width, self.height))
            # Write each row as a new line
            for y in range(self.height):
                for x in range(self.width):
                    f.write(str(self.rows[y][x]))
                f.write("\n")
        # with

    def load(self, path):
        with open(path, 'r') as f:
            # Check magic
            d = f.read(2)
            if d != 'P1':
                raise RuntimeError('File {} is not a PBM'.format(path))
            # Expects a whitespace character
            t = _consume_ws(f)
            if not t[1]:
                raise RuntimeError('File {} is not a PBM'.format(path))
            # Get width
            self.width = _get_integer(f, first = t[0])
            # Get Height, no first character. If we get here, we know the
            # next character after the integer was a space/comment
            self.height = _get_integer(f)
            # Reset image pixel data
            self.rows = []
            # Load the pixel data (automatically handles whitespace)
            #   Pixels are top-level to bottom-right with columns flowing
            #   left-to-right
            for y in range(self.height):
                self.rows.append([])
                for x in range(self.width):
                    self.rows[y].append(_get_pixel(f))
            # PBM parsers are supposed to be lenient so we just ignore any
            # trailing data.
        # with

# vim:ts=4:sw=4:et
