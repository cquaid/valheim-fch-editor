# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import binascii

class JDataHandler:
    """
    Builds stylized structures for JSON dumping.
    Prefixes:
      s_Foo = string
      i_Foo = integer
      f_Foo = float
      b_Foo = boolean
      x_Foo = hex string ("AABBCCDD")

    Possible extensions:
      z_Foo = base64 string
    """
    def encode(self, d):
        """
        d = dictionary
        All keys must be prefixed.

        We actually expect everything is already good when passed in
        aside from x_* since that one needs hexlifying.
        """
        for key in d:
            if (key[0:2] == "x_"):
                if not isinstance(d[key], bytes):
                    raise TypeError()
                d[key] = binascii.hexlify(d[key]).decode('ascii')
            # x_
        # for

    def decode(self, d):
        """
        d = dictionary
        All keys must be prefixed.
        """
        for key in d:
            if (key[0:2] == 's_'):
                if not isinstance(d[key], str):
                    raise TypeError("Key {} expects type 'str'".format(key))
                # Strings are good already, just leave it
            elif (key[0:2] == 'i_'):
                if not isinstance(d[key], int):
                    raise TypeError("Key {} expects type 'int'".format(key))
                # Integers are good already, just leave it
            elif (key[0:2] == 'f_'):
                if not isinstance(d[key], float):
                    raise TypeError("Key {} expects type 'float'".format(key))
                # Floats are good already, just leave it
            elif (key[0:2] == 'b_'):
                if not isinstance(d[key], bool):
                    raise TypeError("Key {} expects type 'bool'".format(key))
                # Booleans are good already, just leave it
            elif (key[0:2] == 'x_'):
                if not isinstance(d[key], str):
                    raise TypeError("Key {} expects type 'str'".format(key))
                # Decode value as a hex string and convert to a bytes()
                d[key] = binascii.unhexlify(d[key])
            else:
                raise KeyError("Unknown type for key '{}'".format(key))
        # for


# vim:ts=4:sw=4:et
