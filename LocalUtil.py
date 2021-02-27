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


# vim:ts=4:sw=4:et
