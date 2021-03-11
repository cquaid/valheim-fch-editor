# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import sys

def die(first, *args):
    print(first, end='', file=sys.stderr)
    for a in args:
        print(' ', a, sep='', end='', file=sys.stderr)
    print('', file=sys.stderr)
    sys.exit(1)

def info(first, *args):
    print('[INFO]', first, end='', file=sys.stderr)
    for a in args:
        print(' ', a, sep='', end='', file=sys.stderr)
    print('', file=sys.stderr)


class BinIFace:
    """
    Base class meant to implement BinReader and BinWriter compatible
    reading and writing
    """
    def toBinary(self, binrdr):
        raise RuntimeError("Missing toBinary() method in class:",
                           self.__class__.__name__)

    def fromBinary(self, binwr):
        raise RuntimeError("Missing fromBinary() method in class:",
                           self.__class__.__name__)


class JSONIFace:
    """
    Base class meant to impliment a JSON reading/writing compatible
    interface.
    """
    def toJSON(self):
        raise RuntimeError("Missing toJSON() method in class:",
                           self.__class__.__name__)

    def fromJSON(self, data):
        raise RuntimeError("Missing fromJSON() method in class:",
                           self.__class__.__name__)


class CountedList(BinIFace, JSONIFace):
    def __init__(self, type_):
        self.type = type_
        self.data = []
    
    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, v):
        self.data[index] = v

    def __iter__(self):
        return iter(self.data)

    def append(self, v):
        if not isinstance(v, self.type):
            raise TypeError("Cannot append value of type", type(v),
                            "to CountedList that expects", self.type)
        self.data.append(v)

    def fromBinary(self, binrdr):
        """
        BinIFace required method
        """
        # Read the i32 item count
        count = binrdr.read_i32()

        if self.type == bool:
            self.data = binrdr.read_u8(count=count)
        elif self.type == int:
            self.data = binrdr.read_i32(count=count)
        elif self.type == float:
            self.data = binrdr.read_float(count=count)
        elif self.type == str:
            self.data = binrdr.read_str(count=count)
        elif issubclass(self.type, BinIFace):
            # For each entry, read something of our type.
            for i in range(count):
                v = self.type()
                v.fromBinary(binrdr)
                self.data.append(v)
        else:
            raise TypeError("Unhandled type", self.type)
        return

    def toBinary(self, binwr):
        """
        BinIFace required method
        """
        # Write the i32 item count
        binwr.write_i32(len(self.data))
        for v in self.data:
            binwr.write(v)
        return

    def fromJSON(self, jdata):
        """
        JSONIFace required method
        """
        if not isinstance(jdata, list):
            raise TypeError("Incorrect data type when expecting a list!",
                            "Got:", type(jdata))
        # If JSONIFace implementer, then we process the list differently.
        if issubclass(self.type, JSONIFace):
            self.data = []
            for entry in jdata:
                v = self.type()
                v.fromJSON(entry)
                self.data.append(v)
            return
        # Not a JSONIFace implementer, so we have a basic type and need to
        # verify as such.
        if (len(jdata) > 0) and (not isinstance(jdata[0], self.type)):
            raise TypeError("Cannot consume list of incorrect type!",
                            "Got:", type(jdata[0]), "Expected:", self.type)
        self.data = jdata
        return

    def toJSON(self):
        """
        JSONIFace required method
        """
        if issubclass(self.type, JSONIFace):
            ret = []
            for v in self.data:
                ret.append(v.toJSON())
            return ret
        return self.data

# vim:ts=4:sw=4:et
