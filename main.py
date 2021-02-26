# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import argparse
import binascii
import struct
import os
import sys

# Local modules
from BinReader import BinReader
from BinWriter import BinWriter
from FCH import FCH_Root

argsp = argparse.ArgumentParser(description="Valheim Character Save File Tool")
argsp.add_argument('path', type=str,
                   help=("Input or output path, this differs depending on " +
                         " the mode. If no mode is specified, then the path " +
                         "is an input valheim character file"))
argsp.add_argument('--destruct', type=str,
                   help="Export valheim character file to a directory")
argsp.add_argument('--construct', type=str,
                   help=("Construct a valheim character file from a " +
                         "'destruct' formatted directory"))
argsp.add_argument("--overwrite", action='store_true',
                   help="Replace output files if they already exist")
argsp.add_argument("--quiet", action='store_true',
                   help="Don't print file info")

args = argsp.parse_args()

if args.construct and args.destruct:
    print("--construct and --destruct are mutually exclusive!")
    argsp.print_help()
    sys.exit(1)

# When destructing, we need to make the directory if it doesn't exist
if args.destruct:
    if not os.path.exists(args.destruct):
        os.makedirs(args.destruct)
    fh = FCH_Root()
    with BinReader(args.path) as br:
        fh.fromBinary(br)
    if not args.quiet:
        fh.printInfo()
    fh.destruct(args.destruct, overwrite = args.overwrite)
elif args.construct:
    fh = FCH_Root()
    fh.construct(args.construct)
    with BinWriter(args.path, overwrite = args.overwrite) as wr:
        fh.toBinary(wr)
    # Sanity read it again!
    with BinReader(args.path) as br:
        fh.fromBinary(br)
    if not args.quiet:
        fh.printInfo()
else:
    # Default is read the file and print info
    fh = FCH_Root()
    with BinReader(args.path) as br:
        fh.fromBinary(br)
    if not args.quiet:
        fh.printInfo()

# vim:ts=4:sw=4:et
