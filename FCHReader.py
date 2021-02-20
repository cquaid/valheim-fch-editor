# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import json
import struct
import os
import sys

# Local modules
import BinReader
import PBMImage
import PrettyPrinter
import JDataHandler
import Valheim


class FCHReader:
    rdr = None
    outdir = None
    overwrite = False
    pr = None
    jdh = None
    exporting = False

    def __init__(self, binreader, outdir = None, overwrite = False):
        self.rdr = binreader
        self.outdir = outdir
        self.overwrite = overwrite
        self.pr = PrettyPrinter.PrettyPrinter()
        self.jdh = JDataHandler.JDataHandler()
        self.exporting = (outdir is not None)

    def parse_header(self):
        """
        24 bytes long. Unknown data, likely seperated in 4 byte chunks
        """
        u1 = self.rdr.read(4)
        u2 = self.rdr.read(4)
        u3 = self.rdr.read(4)
        u4 = self.rdr.read(4)
        u5 = self.rdr.read(4)
        u6 = self.rdr.read(4)

        if self.exporting:
            data = {"x_Unknown1": u1,
                    "x_Unknown2": u2,
                    "x_Unknown3": u3,
                    "x_Unknown4": u4,
                    "x_Unknown5": u5,
                    "x_Unknown6": u6}
            self.jdh.encode(data)
            self.write_json("header.json", data)
        # if

        self.pr.block("Header")
        self.pr.print_a4("Unknown 1", u1)
        self.pr.print_a4("Unknown 2", u2)
        self.pr.print_a4("Unknown 3", u3)
        self.pr.print_a4("Unknown 4", u4)
        self.pr.print_a4("Unknown 5", u5)
        self.pr.print_a4("Unknown 6", u6)
        self.pr.end_block()

    def parse_maps(self):
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
        map_count = self.rdr.read_u32_le()
        for i in range(map_count):
            header = self.rdr.read(68)
            minimap_edge = self.rdr.read_u32_le()

            json_data = { 'Header': {}, 'Markers': [] }
            if self.exporting:
                # We don't store the edge length since the map file already
                # contains that information.
                for j in range(68 // 4):
                    key = 'x_Header{}'.format(j)
                    json_data['Header'][key] = header[(j*4):(j*4)+4]
                self.jdh.encode(json_data['Header'])

            self.pr.block("Map {}".format(i))
            self.pr.bytes("Header", header)
            self.pr.println("Map Size: {0}x{0}".format(minimap_edge))

            # Skipping the map data for now
            if self.exporting:
                self.parse_minimap_data(i, minimap_edge)
            else:
                self.rdr.skip(minimap_edge * minimap_edge)

            self.parse_map_markers(json_data['Markers'])
            self.pr.end_block()

            if self.exporting:
                self.write_json('map{}.json'.format(i), json_data)
        # while

    def parse_minimap_data(self, map_index, edgelen):
        # Alright so the minimap data is a bit wonky.
        # Basically it's a giant boolean array where
        #   0 = undiscovered/fog
        #   1 = discovered/visible
        # This kinda pisses me off since it means the 2048x2048 minimap
        # data takes 0x400000 bytes (4MB) to store when it could be compressed
        # with a bitmap to 0x80000 bytes (512KB). That's an insane different
        # in storage space, especially when you consider a character can have
        # multiple minimaps stored. But I digress.
        #
        # Maps are stored as EdgeLen rows of EdgeLen columns.
        #   byte[linear_index] = (X,Y)
        #   --------------------------
        #              byte[0] = (0,0)
        #        byte[EdgeLen] = (0,1)
        #
        # But what's weirder/annoying: the rows are in reverse order.
        # As stored row[0] is actually row[EdgeLen-1] so we have to
        # flip them when writing the image file.
        img = PBMImage.PBMImage(edgelen, edgelen)
        for r in range(edgelen):
            for c in range(edgelen):
                val = self.rdr.read_u8()
                img.set_pixel((c, (edgelen - r - 1)), val)
        img.write(self.outdir + '/map{}.pbm'.format(map_index),
                  overwrite = self.overwrite)

    def parse_map_markers(self, json_data):
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
        count = self.rdr.read_u32_le()
        for i in range(count):
            name = self.rdr.read_str()
            coord1 = self.rdr.read_float()
            u1 = self.rdr.read_float()
            coord2 = self.rdr.read_float()
            symbol = self.rdr.read_u32_le()
            strike = self.rdr.read_u8()
            symbol_str = Valheim.MapMarkerType_i2a(symbol)

            if self.exporting:
                data = {"s_Name": name,
                       "f_Coord1": coord1,
                       "f_Coord2": coord2,
                       "f_Unknown": u1,
                       "s_Symbol": symbol_str,
                       "b_Strike": bool(strike)}
                self.jdh.encode(data)
                json_data.append(data)

            self.pr.block("Map Marker {}".format(i))
            self.pr.println("Name: {}".format(repr(name)))
            self.pr.println("Coordinate1: {}".format(coord1))
            self.pr.println("Unknown: {}".format(u1))
            self.pr.println("Coordinate2: {}".format(coord2))
            self.pr.println("Type: {} ({})".format(symbol, symbol_str))
            self.pr.println("Strike: {}".format(strike))
            self.pr.end_block()
        # while

    def parse_inventory(self):
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
        json_data = []
        count = self.rdr.read_u32_le()
        self.pr.block("Inventory");
        for i in range(count):
            name = self.rdr.read_str()
            stack_count = self.rdr.read_u32_le()
            durability = self.rdr.read_float()
            column = self.rdr.read_u32_le()
            row = self.rdr.read_u32_le()
            equipped = self.rdr.read_u8()
            level = self.rdr.read_u32_le()
            style = self.rdr.read_u32_le()
            crafter_id = self.rdr.read(8)
            crafter_name = self.rdr.read_str()

            if self.exporting:
                data = {"s_Name": name,
                        "i_Count": stack_count,
                        "f_Durability": durability,
                        "i_SlotX": column,
                        "i_SlotY": row,
                        "b_Equipped": bool(equipped),
                        "i_Level": level,
                        "i_Style": style,
                        "x_CrafterID": crafter_id,
                        "s_CrafterName": crafter_name}
                self.jdh.encode(data)
                json_data.append(data)

            self.pr.println("Item {}:".format(i))
            self.pr.block()
            self.pr.println("Name: {}".format(repr(name)))
            self.pr.println("Count: {}".format(stack_count))
            self.pr.println("Durability: {}".format(durability))
            self.pr.println("Slot: (C:{}, R:{})".format(column, row))
            self.pr.println("Equipped?: {}".format(equipped))
            self.pr.println("Level: {}".format(level))
            self.pr.println("Style: {}".format(style))
            self.pr.bytes("Crafter ID", crafter_id)
            self.pr.println("Crafted By: {}".format(repr(crafter_name)))
            self.pr.end_block()
        self.pr.end_block()
        return json_data

    def parse_strtab(self, name):
        json_data = []
        count = self.rdr.read_u32_le()
        self.pr.block(name)
        for i in range(count):
            s = self.rdr.read_str()
            self.pr.println("{}: {}".format(i, repr(s)))
            if self.exporting:
                data = {'s_Value': s}
                self.jdh.encode(data)
                json_data.append(data)
        self.pr.end_block()
        return json_data

    def parse_journal(self):
        json_data = []
        count = self.rdr.read_u32_le()
        self.pr.block("Journal Entries")
        for i in range(count):
            s1 = self.rdr.read_str()
            s2 = self.rdr.read_str()
            self.pr.println("{}: [ {}, {} ]".format(i, repr(s1), repr(s2)))
            if self.exporting:
                data = {'s_Label': s1,
                        's_Text': s2}
                self.jdh.encode(data)
                json_data.append(data)
        self.pr.end_block()
        return json_data

    def parse_leveled_craftables(self):
        """
        u32_le count
          str name
          u32_le level
        """
        json_data = []
        count = self.rdr.read_u32_le()
        self.pr.block("Leveled Craftables")
        for i in range(count):
            s = self.rdr.read_str()
            lvl = self.rdr.read_u32_le()
            self.pr.println("{}: {}".format(repr(s), lvl))
            if self.exporting:
                data = {'s_Name': s,
                        'i_Level': lvl}
                self.jdh.encode(data)
                json_data.append(data)
        self.pr.end_block()
        return json_data

    def parse_p_unknown1(self):
        """
        u32_le count
          Entrties: ???
        Never seen count be anything but 0
        """
        count = self.rdr.read_u32_le()
        self.pr.block("Player Unknown 1")
        self.pr.println("Value: {}".format(count))
        self.pr.end_block()

        if (count != 0):
            print("WARNING: Player chunk \"Unknown 1\" has a value:", count)
        # Can't do anything with the data if we don't know what it is.
        return [] # JSON data is just empty at the moment.

    def parse_p_unknown2(self):
        """
        u32_le count
          u8[4] ?? - These look like u32s.
        """
        json_data = []
        count = self.rdr.read_u32_le()
        self.pr.block("Player Unknown 2")
        for i in range(count):
            b = self.rdr.read(4)
            self.pr.print_a4(i, b)
            if self.exporting:
                data = {'x_Value': b}
                self.jdh.encode(data)
                json_data.append(data)
        self.pr.end_block()
        return json_data

    def parse_appearance(self):
        """
        str beard type
        str hair type
        
        float c1
        float c2
        float c3
          - These are all the same, I think think they're skin complexion?

        float u1
        fl0at u2
        float u3 - possibly "blondness"?
    
        u32 BodyType: 0 = male body, 1 = female body
        """
        beard = self.rdr.read_str()
        hair = self.rdr.read_str()
        c1 = self.rdr.read_float()
        c2 = self.rdr.read_float()
        c3 = self.rdr.read_float()
        u1 = self.rdr.read_float()
        u2 = self.rdr.read_float()
        u3 = self.rdr.read_float()
        body_type = self.rdr.read_u32_le()
        self.pr.block("Appearance")
        self.pr.println("Beard: {}".format(repr(beard)))
        self.pr.println("Hair: {}".format(repr(hair)))
        self.pr.println("Complexion 1(?): {}".format(c1))
        self.pr.println("Complexion 2(?): {}".format(c2))
        self.pr.println("Complexion 3(?): {}".format(c3))
        self.pr.println("Unknown 1: {}".format(u1))
        self.pr.println("Unknown 2: {}".format(u2))
        self.pr.println("Unknown 3: {}".format(u3))
        self.pr.println("Body Type: {}".format(body_type))
        self.pr.end_block()

        json_data = {}
        if self.exporting:
            json_data['s_Beard'] = beard
            json_data['s_Hair'] = hair
            json_data['i_BodyType'] = body_type
            json_data['f_Complexion1'] = c1
            json_data['f_Complexion2'] = c2
            json_data['f_Complexion3'] = c3
            json_data['f_Unknown1'] = u1
            json_data['f_Unknown2'] = u2
            json_data['f_Unknown3'] = u3
            self.jdh.encode(json_data)
        return json_data

    def parse_active_food(self):
        """
        u32_le count
        string name
        float ??
        float ??
        """
        json_data = []
        count = self.rdr.read_u32_le()
        self.pr.block("Active Food")
        for i in range(count):
            name = self.rdr.read_str()
            u1 = self.rdr.read(4)
            u2 = self.rdr.read(4)
            self.pr.println("Name: {}".format(repr(name)))
            self.pr.print_a4("Unknown 1", u1)
            self.pr.print_a4("Unknown 2", u2)

            if self.exporting:
                data = {'s_Name': name,
                        'x_Unknown1': u1,
                        'x_Unknown2': u2}
                self.jdh.encode(data)
                json_data.append(data)
        self.pr.end_block()
        return json_data

    def parse_p_unknown3(self):
        """
        u32_le - always 02_00_00_00
        """
        value = self.rdr.read_u32_le()
        self.pr.block("Player Unknown 4")
        self.pr.println("Value: {}".format(value))
        self.pr.end_block()

        if self.exporting:
            data = {'i_Value': value}
            self.jdh.encode(data)
            return data
        return {}

    def parse_skill_data(self):
        """
        u32_le count
          u32_le skill ID
          float level(whole num) + xp/percent (fraction)
          float ??
        """
        json_data = []
        count = self.rdr.read_u32_le()
        self.pr.block("Skills")
        for i in range(count):
            sid = self.rdr.read_u32_le()
            level = self.rdr.read_float()
            u1 = self.rdr.read_float()
            sname = Valheim.SkillType_i2a(sid)
            self.pr.block("Skill {} ({})".format(sid, sname))
            self.pr.println("Lvl.Exp: {}".format(level))
            self.pr.println("Unknown: {}".format(u1))
            self.pr.end_block()

            if self.exporting:
                data = {'s_Type': sname,
                        'f_Level': level,
                        'f_Unknown': u1}
                self.jdh.encode(data)
                json_data.append(data)
        self.pr.end_block()
        return json_data

    def parse_checksum(self):
        """
        Don't actually know if this is a checksum...

        u32_le byte count (always 64 bytes?)
          bytes
        """
        count = self.rdr.read_u32_le()
        b = self.rdr.read(count)
        self.pr.block("Checksum")
        self.pr.bytes("Value", b)
        self.pr.end_block()

        if self.exporting:
            data = {}
            for i in range(count // 8):
                data['x_Unknown{}'.format(i)] = b[(i*8):(i*8)+8]
            self.jdh.encode(data)
            return data
        return {}

    def parse_player(self):
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
        player_name = self.rdr.read_str()
        player_id = self.rdr.read(8)
        phdr_u1 = self.rdr.read(27)

        gp_name = self.rdr.read_str()
        gp_u1 = self.rdr.read(4)
        gp_u2 = self.rdr.read(4)

        # Ordered so the relevant stuff it up top
        json_data = {"Header": None,
                     "GiantPower": None,
                     "Appearance": None,
                     "ActiveFood": None,
                     "Skills": None,
                     "Inventory": None,
                     "CraftingStations": None,
                     "Milestones": None,
                     "Trophies": None,
                     "Journal": None,
                     "KnownRecipes": None,
                     "DiscoveredItems": None,
                     "Unknown1": None,
                     "Unknown2": None,
                     "Unknown3": None,
                     "Checksum": None}

        self.pr.block("Player Data")
        self.pr.println("Name: {}".format(player_name))
        self.pr.bytes("ID", player_id)
        self.pr.bytes("Unknown", phdr_u1)

        self.pr.block("Giant Power")
        self.pr.println("Name: {}".format(gp_name))
        self.pr.print_a4("Unknown 1", gp_u1)
        self.pr.print_a4("Unknown 2", gp_u2)
        self.pr.end_block()

        if self.exporting:
            data = {"s_Name": player_name,
                    "x_PlayerID": player_id}
            for i in range((len(phdr_u1)+1) // 4):
                data['x_Unknown{}'.format(i)] = phdr_u1[(i*4):(i*4)+4]
            self.jdh.encode(data)
            json_data['Header'] = data

            data = {"s_Name": gp_name,
                    "x_Unknown1": gp_u1,
                    "x_Unknown2": gp_u2}
            self.jdh.encode(data)
            json_data['GiantPower'] = data
        # if

        json_data['Inventory'] = self.parse_inventory()
        json_data['KnownRecipes'] = self.parse_strtab("Known Recipes")
        json_data['CraftingStations'] = self.parse_leveled_craftables()
        json_data['DiscoveredItems'] = self.parse_strtab("Discovered Items")
        json_data['Milestones'] = self.parse_strtab("Milestones(?)")
        json_data['Unknown1'] = self.parse_p_unknown1()
        json_data['Trophies'] = self.parse_strtab("Trophies")
        json_data['Unknown2'] = self.parse_p_unknown2()
        json_data['Journal'] = self.parse_journal()
        json_data['Appearance'] = self.parse_appearance()
        json_data['ActiveFood'] = self.parse_active_food()
        json_data['Unknown3'] = self.parse_p_unknown3()
        json_data['Skills'] = self.parse_skill_data()
        json_data['Checksum'] = self.parse_checksum()
        self.pr.end_block()

        if self.exporting:
            self.write_json("player.json", json_data)

    def parse(self):
        self.parse_header()
        self.parse_maps()
        self.parse_player()

    def write_json(self, bname, data):
        path = self.outdir + '/' + bname
        mode = 'x'
        if self.overwrite:
            mode = 'w'
        with open(path, mode) as f:
            json.dump(data, f, indent=4)

# vim:ts=4:sw=4:autoindent
