# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import glob
import json
import struct
import os
import sys

# Local modules
import BinWriter
import PBMImage
import JDataHandler
import Valheim


class FCHWriter:
    wr = None
    outdir = None
    jdh = None

    def __init__(self, binwriter, outdir):
        self.wr = binwriter
        self.outdir = outdir
        self.jdh = JDataHandler.JDataHandler()

    def build_header(self):
        """
        File: dir/header.json
        24 bytes broken into 4 byte chunks.
        x_Unknown1 .. x_Unknown6
        """
        with open(self.outdir + '/header.json', 'r') as f:
            data = json.load(f)
        # Should be safe to just pass to the type decoder
        self.jdh.decode(data)
        # XXX: Should probably validate that these are 4 bytes long
        self.wr.write( data['x_Unknown1'] )
        self.wr.write( data['x_Unknown2'] )
        self.wr.write( data['x_Unknown3'] )
        self.wr.write( data['x_Unknown4'] )
        self.wr.write( data['x_Unknown5'] )
        self.wr.write( data['x_Unknown6'] )


    def build_minimap_data(self, path):
        img = PBMImage.PBMImage()
        img.load(path)

        if img.get_width() != img.get_height():
            raise RuntimeError("Minimaps must have be square!")

        # Write the edge length
        edgelen = img.get_width()
        self.wr.write_u32_le(edgelen)

        # We have to flip the rows when restoring the minimap
        for r in range(edgelen):
            for c in range(edgelen):
                val = img.get_pixel((c, (edgelen - r - 1)))
                self.wr.write_u8(val)
        # for

    def build_maps(self):
        """
        u32_le map count

        Map Entry:
          - 72 bytes of unknown data. Part of it is a signature denoting the
            map seed I think? It needs some way to tell which map file it
            belongs to. Just haven't figured it out yet.
          - I think the last 4 bytes is a u32_le denoting the minimap edge
            length. All minimap are 2048x2048 bytes and this u32_le is always
            0x00_00_08_00 which is 2048.
          --
          map data: 0x400000 bytes, or 2048x2048
          --
          u32_le Map Marker Count
          Map Marker Entries:
            u8 len, u8[len] text/name
            float coordinate1 (unsure how this works yet)
            u8[4] unknown - only set for boss markers
            float coordinate2
            u8 sumbol - what symbol is used on the map
            u8[3] unknown - always zeros, could be part of the symbol
                            number above, making it a u32_le
            u8 strike - if the symbol is Xed out on the map


        JSON structure:
          {
             Header: {
               x_Unknown0:
               ...
               x_Unknown16:
            }
            Markers: [
                { },
                { },
            ]
          }
        """
        # Enumerate map files. This is totes just based on how many are in the
        # directory.
        #
        # 2 files per map:
        #   mapN.json
        #   mapN.pbm
        # Where N is a positive integer 0-N
        #
        # Granted we don't really care so we're just searching for
        # 'map*.json' and taking whatever the * is from there.
        #
        # Sorting by name.
        #
        maps = glob.glob(self.outdir + '/map*.json')
        maps.sort()

        # First write the map count (u32)
        self.wr.write_u32_le(len(maps))

        # Next we'll be dealing with these one at a time.
        for m in maps:
            with open(m, 'r') as f:
                data = json.load(f)
            # Only dealing with the header here, so just decode that.
            self.jdh.decode(data['Header'])

            # Header is 68 bytes split as 4 byte chunks:
            # x_Header0 .. x_Header16
            for i in range(68//4):
                key = 'x_Header{}'.format(i)
                self.wr.write(data['Header'][key])

            # Suffix is '.json', we need to convert that to '.pbm' so we just
            # lazily substring it.
            self.build_minimap_data(m[0:-5] + '.pbm')

            # Now handle the map marker data from the JSON. It's an array
            self.build_map_markers(data['Markers'])
        # while

    def build_map_markers(self, json_data):
        """
        u32_le count
        Entries:
          u8,str
          float coordinate1
          u8[4] ? Looks like a float
          float coordinate2
          u32_le symbol_type
          u8 strike
        """
        # Write the marker count
        self.wr.write_u32_le(len(json_data))

        for m in json_data:
            # Each entry is a dictionary that needs decoding
            self.jdh.decode(m)

            self.wr.write_str(m['s_Name'])
            self.wr.write_float(m['f_Coord1'])
            self.wr.write_float(m['f_Unknown'])
            self.wr.write_float(m['f_Coord2'])

            # Decode the symbol string
            sidx = Valheim.MapMarkerType_a2i(m['s_Symbol'])
            self.wr.write_u32_le(sidx)
            self.wr.write_u8(m['b_Strike'])
        # while

    def build_inventory(self, json_data):
        """
        u32_le count
          string name
          u32_le stack count
          float durability
          u32_le column
          u32_le row
          u8 equipped boolean
          u32_le level
          u32_le style
          u8[8] crafter id
          string crafter name
        """
        # Inventory item count
        self.wr.write_u32_le(len(json_data))
        # Array of dictionaries
        for item in json_data:
            self.jdh.decode(item)
            self.wr.write_str(item['s_Name'])
            self.wr.write_u32_le(item['i_Count'])
            self.wr.write_float(item['f_Durability'])
            self.wr.write_u32_le(item['i_SlotX'])
            self.wr.write_u32_le(item['i_SlotY'])
            self.wr.write_u8(item['b_Equipped'])
            self.wr.write_u32_le(item['i_Level'])
            self.wr.write_u32_le(item['i_Style'])
            self.wr.write(item['x_CrafterID'])
            self.wr.write_str(item['s_CrafterName'])

    def build_strtab(self, json_data):
        # Each entry is a dictionary with 's_Value' as the key.
        self.wr.write_u32_le(len(json_data))
        for d in json_data:
            self.jdh.decode(d)
            self.wr.write_str(d['s_Value'])

    def build_journal(self, json_data):
        # Each entry is a pair
        self.wr.write_u32_le(len(json_data))
        for d in json_data:
            self.jdh.decode(d)
            self.wr.write_str(d['s_Label'])
            self.wr.write_str(d['s_Text'])

    def build_leveled_craftables(self, json_data):
        """
        u32_le count
          str name
          u32_le level
        """
        self.wr.write_u32_le(len(json_data))
        for d in json_data:
            self.jdh.decode(d)
            self.wr.write_str(d['s_Name'])
            self.wr.write_u32_le(d['i_Level'])

    def build_p_unknown1(self, json_data):
        """
        u32_le count
          Entrties: ???
        Never seen count be anything but 0
        """
        self.wr.write_u32_le(len(json_data))

        if len(json_data) != 0:
            print("WARNING: Player chunk \"Unknown 1\" has a value:",
                  len(json_data))
        # Can't do anything with the data since we don't know what it is.

    def build_p_unknown2(self, json_data):
        """
        u32_le count
          u8[4] ?? - These look like u32s.
        """
        self.wr.write_u32_le(len(json_data))
        for d in json_data:
            self.jdh.decode(d)
            self.wr.write(d['x_Value'])

    def build_appearance(self, json_data):
        """
        str beard type
        str hair type

        float c1
        float c2
        float c3
          - All the same, likely complexion?

        float u1
        float u2
        float u3 - possibly "blondness"?

        u32 BodyType: 0 = male, 1 = female
        """
        self.jdh.decode(json_data)
        self.wr.write_str(json_data['s_Beard'])
        self.wr.write_str(json_data['s_Hair'])
        self.wr.write_float(json_data['f_Complexion1'])
        self.wr.write_float(json_data['f_Complexion2'])
        self.wr.write_float(json_data['f_Complexion3'])
        self.wr.write_float(json_data['f_Unknown1'])
        self.wr.write_float(json_data['f_Unknown2'])
        self.wr.write_float(json_data['f_Unknown3'])
        self.wr.write_u32_le(json_data['i_BodyType'])

    def build_active_food(self, json_data):
        """
        u32_le count
        string name
        float ??
        float ??
        """
        self.wr.write_u32_le(len(json_data))
        for d in json_data:
            self.jdh.decode(d)
            self.wr.write_str(d['s_Name'])
            self.wr.write(d['x_Unknown1'])
            self.wr.write(d['x_Unknown2'])

    def build_p_unknown3(self, json_data):
        """
        u32_le - always 02_00_00_00
        """
        self.jdh.decode(json_data)
        self.wr.write_u32_le(json_data['i_Value'])

    def build_skill_data(self, json_data):
        """
        u32_le count
          u32_le skill ID
          float level(whole num) + xp/percent (fraction)
          float ??
        """
        self.wr.write_u32_le(len(json_data))
        for d in json_data:
            self.jdh.decode(d)
            sid = Valheim.SkillType_a2i(d['s_Type'])
            self.wr.write_u32_le(sid)
            self.wr.write_float(d['f_Level'])
            self.wr.write_float(d['f_Unknown'])

    def build_checksum(self, json_data):
        """
        Don't actually know if this is a checksum...

        u32_le byte count (always 64 bytes?)
          bytes

        json is split into multiple 8 byte chunks:
        x_Unknown0 .. x_UnknownN
        """
        self.jdh.decode(json_data)
        byte_count = 0
        for k in json_data:
            byte_count += len(json_data[k])
        self.wr.write_u32_le(byte_count)
        for i in range(byte_count // 8):
            self.wr.write(json_data['x_Unknown{}'.format(i)])

    def build_player(self):
        """
        u8,str Player Name
        u8[8] Player ID
        u8[24] ??
        u8[3] ??

        u8,str Giant Power Name
        u8[4] ?? - float, cooldown timer?
        u8[4] ?? - cooldown timer max?

        Then a bunch of blocks:
         - Inventory
         - Known Craftable Items
         - Crafting Station Levels
         - Discovered Items
         - "Milestones"
         - "Unknown1"
         - Obtained Trophies
         - "Unknown2"
         - Journal Entries
         - Appearance
         - Active Food
         - "Unknown3"
         - Skills
         - Checksum
        """
        with open(self.outdir + '/player.json', 'r') as f:
            data = json.load(f)

        self.jdh.decode(data['Header'])
        self.wr.write_str(data['Header']['s_Name'])
        self.wr.write(data['Header']['x_PlayerID'])
        for i in range((27 + 1) // 4):
            self.wr.write(data['Header']['x_Unknown{}'.format(i)])

        self.jdh.decode(data['GiantPower'])
        self.wr.write_str(data['GiantPower']['s_Name'])
        self.wr.write(data['GiantPower']['x_Unknown1'])
        self.wr.write(data['GiantPower']['x_Unknown2'])

        self.build_inventory(data['Inventory'])
        self.build_strtab(data['KnownRecipes'])
        self.build_leveled_craftables(data['CraftingStations'])
        self.build_strtab(data['DiscoveredItems'])
        self.build_strtab(data['Milestones'])
        self.build_p_unknown1(data['Unknown1'])
        self.build_strtab(data['Trophies'])
        self.build_p_unknown2(data['Unknown2'])
        self.build_journal(data['Journal'])
        self.build_appearance(data['Appearance'])
        self.build_active_food(data['ActiveFood'])
        self.build_p_unknown3(data['Unknown3'])
        self.build_skill_data(data['Skills'])
        self.build_checksum(data['Checksum'])

    def build(self):
        self.build_header()
        self.build_maps()
        self.build_player()

# vim:ts=4:sw=4:autoindent
