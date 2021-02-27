# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import binascii
from LocalUtil import die

class JDataAdaptor:
    """
    Helps get/set json data.
    """
    def __init__(self, data_root):
        self.d = data_root

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return

    def get(self, key, type_, default):
        ret = self.d.get(key, default)
        if not isinstance(ret, type_):
            die("JSON key '{}'".format(key),
                "has type '{}',".format(type(ret)),
                "but expects type '{}'".format(type_))
        return ret

    def get_str(self, key, default):
        return self.get(key, str, default)

    def get_int(self, key, default):
        return self.get(key, int, default)

    def get_float(self, key, default):
        return self.get(key, float, default)

    def get_bool(self, key, default):
        return self.get(key, bool, default)

    def get_list(self, key, mem_type, default, count=None):
        ret = self.get(key, list, default)
        # If no members, and that's okay, then return
        if (len(ret) == 0) and ((count is None) or (count == 0)):
            return ret
        # Validate member type
        if not isinstance(ret[0], mem_type):
            die("JSON key '{}'".format(key),
                "has type 'list({})',".format(type(ret[0])),
                "but expects type 'list({})'".format(mem_type))
        if count is None:
            return ret
        # Validate length
        if len(ret) != count:
            die("JSON key '{}'".format(key),
                "expects a list of {} elements,".format(count),
                "but got a count of {}". format(len(ret)))
        return ret

    def get_hexstr(self, key, default):
        s = self.get_str(key, default)
        return binascii.unhexlify(s)

# vim:ts=4:sw=4:et
