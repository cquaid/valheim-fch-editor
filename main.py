# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import argparse
import binascii
import struct
import os
import sys

# Local modules
import BinReader
import BinWriter
import FCHReader
import FCHWriter

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

args = argsp.parse_args()

if args.construct and args.destruct:
    print("--construct and --destruct are mutually exclusive!")
    argsp.print_help()
    sys.exit(1)

# When destructing, we need to make the directory if it doesn't exist
if args.destruct:
    if not os.path.exists(args.destruct):
        os.makedirs(args.destruct)
    br = BinReader.BinReader(args.path)
    fchr = FCHReader.FCHReader(br, outdir = args.destruct,
                               overwrite = args.overwrite)
    fchr.parse()
    br.close()
elif args.construct:
    bw = BinWriter.BinWriter(args.path, overwrite = args.overwrite)
    fchw = FCHWriter.FCHWriter(bw, args.construct)
    fchw.build()
    bw.close()
    # Sanity read it again!
    br = BinReader.BinReader(args.path)
    fchr = FCHReader.FCHReader(br)
    fchr.parse()
    br.close()
else:
    # Default is read the file and print info
    br = BinReader.BinReader(args.path)
    fchr = FCHReader.FCHReader(br)
    fchr.parse()
    br.close()

# vim:ts=4:sw=4:et
