# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT
import binascii
import glob
import json
import struct

try:
    import hashlib
    _have_sha512 = True
except:
    _have_sha512 = False

# Local modules
import BinReader
import BinWriter
import PBMImage
import Valheim
import WBitMatrix

from LocalUtil import *
from JDataAdaptor import JDataAdaptor
from PrettyPrinter import PrettyPrinter, PPWrap

class FCH_InvItem(BinIFace, JSONIFace):
    def __init__(self):
        self.clear()

    def clear(self):
        self.name = ""
        self.count = 0
        self.durability = 0.0
        self.slot = [ 0, 0 ]
        self.equipped = False
        self.level = 0
        self.style = 0
        self.crafter_id = 0 # i64
        self.crafter_name = ""

    def fromBinary(self, binrdr, inv_version):
        self.clear()
        self.name = binrdr.read_str()
        self.count = binrdr.read_i32()
        self.durability = binrdr.read_float()
        self.slot = binrdr.read_i32(count=2)
        self.equipped = binrdr.read_bool()
        if inv_version >= 101:
            self.level = binrdr.read_i32()
        if inv_version >= 102:
            self.style = binrdr.read_i32()
        if inv_version >= 103:
            self.crafter_id = binrdr.read_i64()
            self.crafter_name = binrdr.read_str()
        return

    def fromJSON(self, data):
        self.clear()
        with JDataAdaptor(data) as j:
            self.name = j.get_str('Name', '')
            self.count = j.get_int('Count', 0)
            self.durability = j.get_float('Durability', 100.0)
            self.slot = j.get_list('SlotXY', int, [0,0], count=2)
            self.equipped = j.get_bool('Equipped', False)
            self.level = j.get_int('Level', 0)
            self.style = j.get_int('Style', 0)
            self.crafter_id = j.get_int('CrafterID', 0)
            self.crafter_name = j.get_str('CrafterName', '')
        return

    def toBinary(self, binwr):
        binwr.write(self.name)
        binwr.write(self.count)
        binwr.write(self.durability)
        binwr.write_list(self.slot)
        binwr.write(self.equipped)
        binwr.write(self.level)
        binwr.write(self.style)
        binwr.write_i64(self.crafter_id)
        binwr.write(self.crafter_name)

    def toJSON(self):
        data = {
            'Name': self.name,
            'Count': self.count,
            'Durability': self.durability,
            'SlotXY': self.slot,
            'Equipped': self.equipped,
            'Level': self.level,
            'Style': self.style,
            'CrafterID': self.crafter_id,
            'CrafterName': self.crafter_name,
        }
        return data

    def printInfo(self, pp):
        pp.println("Name:", self.name)
        pp.println("Count:", self.count)
        pp.println("Durability:", self.durability)
        pp.println("Slot (X,Y):", self.slot)
        pp.println("Equipped:", self.equipped)
        pp.println("Level:", self.level)
        pp.println("Style:", self.style)
        pp.println("Crafter ID:", self.crafter_id)
        pp.println("Crafter Name:", self.crafter_name)
        return


class FCH_Inventory(BinIFace, JSONIFace):
    CURRENT_VERSION = 103

    def __init__(self):
        self.clear()

    def clear(self):
        self.version = 0
        self.items = [] # FCH_InvItem
        return

    def fromBinary(self, binrdr):
        self.clear()
        self.version = binrdr.read_i32()
        if (self.version > self.CURRENT_VERSION):
            die("Unknown FCH Inventory Version:", self.version)
        info("Inventory Version:", self.version)

        count = binrdr.read_i32()
        for i in range(count):
            v = FCH_InvItem()
            v.fromBinary(binrdr, self.version)
            self.items.append(v)
        return

    def fromJSON(self, data):
        self.clear()
        self.version = self.CURRENT_VERSION
        for i in data:
            v = FCH_InvItem()
            v.fromJSON(i)
            self.items.append(v)
        return

    def toBinary(self, binwr):
        binwr.write(self.CURRENT_VERSION)
        binwr.write(len(self.items))
        for v in self.items:
            v.toBinary(binwr)
        return

    def toJSON(self):
        data = []
        for v in self.items:
            data.append(v.toJSON())
        return data

    def printInfo(self, pp):
        pp.println("Count:", len(self.items))
        for i in range(len(self.items)):
            pp.println("{}:".format(i))
            with PPWrap(pp):
                self.items[i].printInfo(pp)
        return


class FCH_CraftingStation(BinIFace, JSONIFace):
    def __init__(self):
        self.clear()

    def clear(self):
        self.name = ""
        self.level = 0

    def fromBinary(self, binrdr):
        self.clear()
        self.name = binrdr.read_str()
        self.level = binrdr.read_i32()
        return

    def fromJSON(self, data):
        self.clear()
        with JDataAdaptor(data) as j:
            self.name = j.get_str('Name', '')
            self.level = j.get_int('Level', 0)
        return

    def toBinary(self, binwr):
        binwr.write(self.name)
        binwr.write(self.level)
        return

    def toJSON(self):
        data = {
            'Name': self.name,
            'Level': self.level,
        }
        return data

    def printInfo(self, pp):
        pp.println("Name:", self.name)
        pp.println("Level:", self.level)
        return


class FCH_JournalEntry(BinIFace, JSONIFace):
    def __init__(self):
        self.clear()

    def clear(self):
        self.label = ""
        self.text = ""

    def fromBinary(self, binrdr):
        self.clear()
        self.label = binrdr.read_str()
        self.text = binrdr.read_str()

    def fromJSON(self, data):
        self.clear()
        with JDataAdaptor(data) as j:
            self.label = j.get_str('Label', '')
            self.text = j.get_str('Text', '')
        return

    def toBinary(self, binwr):
        binwr.write(self.label)
        binwr.write(self.text)

    def toJSON(self):
        data = {
            'Label': self.label,
            'Text': self.text,
        }
        return data

    def printInfo(self, pp):
        pp.println("Label:", self.label)
        pp.println("Text:", self.text)
        return


class FCH_Appearance(BinIFace, JSONIFace):
    def __init__(self):
        self.clear()

    def clear(self):
        self.beard = ""
        self.hair = ""
        self.complexion = [ 0.0, 0.0, 0.0 ]
        self.hair_color = [ 0.0, 0.0, 0.0 ]
        self.body_type = 0

    def fromBinary(self, binrdr):
        self.clear()
        self.beard = binrdr.read_str()
        self.hair = binrdr.read_str()
        self.complexion = binrdr.read_float(count=3)
        self.hair_color = binrdr.read_float(count=3)
        self.body_type = binrdr.read_i32()

    def fromJSON(self, data):
        self.clear()
        with JDataAdaptor(data) as j:
            self.beard = j.get_str('Beard', '')
            self.hair = j.get_str('Hair', '')
            self.complexion = j.get_list('ComplexionRGB', float,
                                         [0.0, 0.0, 0.0], count=3)
            self.hair_color = j.get_list('HairColorRGB', float,
                                         [0.0, 0.0, 0.0], count=3)
            self.body_type = j.get_int('BodyType', 0)
        return

    def toBinary(self, binwr):
        binwr.write(self.beard)
        binwr.write(self.hair)
        binwr.write_list(self.complexion)
        binwr.write_list(self.hair_color)
        binwr.write(self.body_type)

    def toJSON(self):
        data = {
            'Beard': self.beard,
            'Hair': self.hair,
            'ComplexionRGB': self.complexion,
            'HairColorRGB': self.hair_color,
            'BodyType': self.body_type,
        }
        return data

    def printInfo(self, pp):
        if len(self.beard) != 0:
            pp.println("Beard:", self.beard)
        else:
            pp.println("Beard: <None>")
        if len(self.hair) != 0:
            pp.println("Hair:", self.hair)
        else:
            pp.println("Beard: <None>")
        pp.println("Complexion (R,G,B):", self.complexion)
        pp.println("Hair Color (R,G,B):", self.hair_color)
        if self.body_type == 0:
            pp.println("Body Type: Male")
        elif self.body_type == 1:
            pp.println("Body Type: Female")
        else:
            pp.println("Body Type:", self.body_type)
        return


class FCH_ActiveFood(BinIFace, JSONIFace):
    def __init__(self):
        self.clear()

    def clear(self):
        self.name = ""
        self.health = 0.0
        self.stamina = 0.0

    def fromBinary(self, binrdr):
        self.clear()
        self.name = binrdr.read_str()
        self.health = binrdr.read_float()
        self.stamina = binrdr.read_float()

    def fromJSON(self, data):
        self.clear()
        with JDataAdaptor(data) as j:
            self.name = j.get_str('Name', '')
            self.health = j.get_float('Health', 0.0)
            self.stamina = j.get_float('Stamina', 0.0)
        return

    def toBinary(self, binwr):
        binwr.write(self.name)
        binwr.write(self.health)
        binwr.write(self.stamina)

    def toJSON(self):
        data = {
            'Name': self.name,
            'Health': self.health,
            'Stamina': self.stamina,
        }
        return data

    def printInfo(self, pp):
        pp.println("Name:", self.name)
        pp.println("Health Remaining:", self.health)
        pp.println("Stamina Remaining:", self.stamina)
        return


class FCH_Skill(BinIFace, JSONIFace):
    def __init__(self):
       self.clear()

    def clear(self):
       self.skill = "0x00"
       self.level = 0.0
       self.exp = 0.0

    def fromBinary(self, binrdr, skill_version):
        self.clear()
        skill_int = binrdr.read_i32()
        self.skill = Valheim.SkillType_i2a(skill_int)
        self.level = binrdr.read_float()
        if skill_version >= 2:
            self.exp = binrdr.read_float()
        return

    def fromJSON(self, data):
        self.clear()
        with JDataAdaptor(data) as j:
            self.skill = j.get_str("Name", "0x00")
            self.level = j.get_float("Level", 0.0)
            self.exp = j.get_float("Experience", 0.0)
        return

    def toBinary(self, binwr):
        skill_int = Valheim.SkillType_a2i(self.skill)
        binwr.write(skill_int)
        binwr.write(self.level)
        binwr.write(self.exp)
        return

    def toJSON(self):
        data = {
            'Name': self.skill,
            'Level': self.level,
            'Experience': self.exp,
        }
        return data

    def printInfo(self, pp):
        pp.println("Name:", self.skill)
        pp.println("Level:", self.level)
        pp.println("Experience:", self.exp)
        return

class FCH_SkillList(BinIFace, JSONIFace):
    CURRENT_VERSION = 2

    def __init__(self):
        self.clear()

    def clear(self):
        self.version = 0
        self.skills = []

    def fromBinary(self, binrdr):
        self.clear()
        self.version = binrdr.read_i32()
        if self.version > self.CURRENT_VERSION:
            die("Unknown Skills Version:", self.version)
        info("Skills Version:", self.version)
        count = binrdr.read_i32()
        for i in range(count):
            v = FCH_Skill()
            v.fromBinary(binrdr, self.version)
            self.skills.append(v)
        return

    def fromJSON(self, data):
        self.clear()
        for i in data:
            v = FCH_Skill()
            v.fromJSON(i)
            self.skills.append(v)
        return

    def toBinary(self, binwr):
        binwr.write(self.CURRENT_VERSION)
        binwr.write(len(self.skills))
        for v in self.skills:
            v.toBinary(binwr)
        return

    def toJSON(self):
        data = []
        for v in self.skills:
            data.append( v.toJSON() )
        return data

    def printInfo(self, pp):
        pp.println("Count:", len(self.skills))
        for i in range(len(self.skills)):
            pp.println("{}:".format(i))
            with PPWrap(pp):
                self.skills[i].printInfo(pp)
        return

class FCH_Biome(BinIFace, JSONIFace):
    def __init__(self):
        self.clear()

    def clear(self):
        self.biome_str = ""

    def fromBinary(self, binrdr):
        self.clear()
        v = binrdr.read_i32()
        self.biome_str = Valheim.BiomeType_i2a(v)
        return

    def fromJSON(self, data):
        self.clear()
        if not isinstance(data, str):
            raise TypeError("Invalid data type for Biome. Expected: 'str',",
                            "Got:", type(data))
        self.biome_str = data
        return

    def toBinary(self, binwr):
        v = Valheim.BiomeType_a2i(self.biome_str)
        binwr.write(v)
        return

    def toJSON(self):
        return self.biome_str

    def printInfo(self, pp):
        pp.println("{} ({})".format(self.biome_str,
                                    Valheim.BiomeType_a2i(self.biome_str)))
        return


class FCH_PlayerData(JSONIFace):
    CURRENT_VERSION = 24

    def __init__(self):
        self.clear()

    def clear(self):
        self.name = ""
        self.player_id = 0 # i64
        self.start_seed = b''
        self.version = 0
        self.health_max = 0.0
        self.health = 0.0
        self.stamina_max = 0.0
        self.first_spawn = False
        self.time_since_death = 0.0
        self.gp_name = ""
        self.gp_cooldown = 0.0
        self.inventory = FCH_Inventory()
        self.known_recipes = CountedList(str)
        self.known_stations = CountedList(FCH_CraftingStation)
        self.discovered_materials = CountedList(str)
        self.shown_tutorials = CountedList(str)
        self.discovered_uniques = CountedList(str)
        self.trophies = CountedList(str)
        self.known_biomes = CountedList(FCH_Biome)
        self.journal = CountedList(FCH_JournalEntry)
        self.appearance = FCH_Appearance()
        self.active_food = CountedList(FCH_ActiveFood)
        self.skill_list = FCH_SkillList()

    def fromBinary(self, binrdr, file_version):
        self.clear()
        self.name = binrdr.read_str()
        self.player_id = binrdr.read_i64()
        self.start_seed = binrdr.read_binstr()

        # No player data? Just eturn
        have_player_data = binrdr.read_bool()
        if not have_player_data:
            info("No PlayerData in FCH file.")
            return
        
        # XXX: We don't actually use this
        player_data_byte_count = binrdr.read_i32()

        # Due to complexity, we don't support version <= 20
        self.version = binrdr.read_i32()
        if (self.version > self.CURRENT_VERSION) or (self.version <= 20):
            die("Unhandled player version:", self.version)
        info("PlayerData Version:", self.version)

        self.health_max = binrdr.read_float()
        self.health = binrdr.read_float()
        self.stamina_max = binrdr.read_float()
        self.first_spawn = binrdr.read_bool()
        self.time_since_death = binrdr.read_float()
        if self.version >= 23:
            self.gp_name = binrdr.read_str()
        if self.version >= 24:
            self.gp_cooldown = binrdr.read_float()

        self.inventory.fromBinary(binrdr)
        self.known_recipes.fromBinary(binrdr)
        self.known_stations.fromBinary(binrdr)
        self.discovered_materials.fromBinary(binrdr)
        self.shown_tutorials.fromBinary(binrdr)
        self.discovered_uniques.fromBinary(binrdr)
        self.trophies.fromBinary(binrdr)
        self.known_biomes.fromBinary(binrdr)

        # Journal entries
        if self.version >= 22:
            self.journal.fromBinary(binrdr)

        self.appearance.fromBinary(binrdr)
        self.active_food.fromBinary(binrdr)
        self.skill_list.fromBinary(binrdr)
        return

    def fromJSON(self, data):
        self.clear()
        self.version = self.CURRENT_VERSION

        with JDataAdaptor(data) as j:
            self.name = j.get_str('PlayerName', '')
            self.player_id = j.get_int('PlayerID', 0)
            self.start_seed = j.get_hexstr('StartSeed', b'')
            self.health = j.get_float('Health', 1.0)
            self.health_max = j.get_float('HealthMax', self.health)
            self.stamina_max = j.get_float('StaminaMax', 1.0)
            self.first_spawn = j.get_bool('FirstSpawn', False)
            self.time_since_death = j.get_float('TimeSinceDeath', 0.0)

        tmp = {
            'ActiveFood': self.active_food,
            'Appearance': self.appearance,
            'CraftingStations': self.known_stations,
            'DiscoveredMaterials': self.discovered_materials,
            'Inventory': self.inventory,
            'Journal': self.journal,
            'KnownBiomes': self.known_biomes,
            'KnownRecipes': self.known_recipes,
            'ShownTutorials': self.shown_tutorials,
            'Skills': self.skill_list,
            'Trophies': self.trophies,
        }

        for (k,v) in tmp.items():
            if k in data:
                v.fromJSON(data[k])

        if 'GuardianPower' in data:
            with JDataAdaptor(data['GuardianPower']) as j:
                self.gp_name = j.get_str('Name', '')
                self.gp_cooldown = j.get_float('Cooldown', 0.0)
        return

    def toBinary(self, binwr):
        binwr.write(self.name)
        binwr.write_i64(self.player_id)
        binwr.write_binstr(self.start_seed)
        binwr.write(True) # HavePlayerData

        # Player Data byte count (temporary)
        byte_count_pos = binwr.tell()
        binwr.write(0)
        start_pos = binwr.tell()

        binwr.write(self.CURRENT_VERSION)
        binwr.write(self.health_max)
        binwr.write(self.health)
        binwr.write(self.stamina_max)
        binwr.write(self.first_spawn)
        binwr.write(self.time_since_death)
        binwr.write(self.gp_name)
        binwr.write(self.gp_cooldown)

        self.inventory.toBinary(binwr)
        self.known_recipes.toBinary(binwr)
        self.known_stations.toBinary(binwr)
        self.discovered_materials.toBinary(binwr)
        self.shown_tutorials.toBinary(binwr)
        self.discovered_uniques.toBinary(binwr)
        self.trophies.toBinary(binwr)
        self.known_biomes.toBinary(binwr)
        self.journal.toBinary(binwr)
        self.appearance.toBinary(binwr)
        self.active_food.toBinary(binwr)
        self.skill_list.toBinary(binwr)

        # Ending player data position
        end_pos = binwr.tell()
        byte_count = end_pos - start_pos
        # Fixup the count
        binwr.write(byte_count, pos=byte_count_pos)
        return

    def toJSON(self):
        data = {
            'PlayerName': self.name,
            'PlayerID': self.player_id,
            'StartSeed': binascii.hexlify(self.start_seed).decode('ascii'),
            'Health': self.health,
            'HealthMax': self.health_max,
            'StaminaMax': self.stamina_max,
            'FirstSpawn': self.first_spawn,
            'TimeSinceDeath': self.time_since_death,
            'GuardianPower': {
                'Name': self.gp_name,
                'Cooldown': self.gp_cooldown,
            },
            'ActiveFood': self.active_food.toJSON(),
            'Appearance': self.appearance.toJSON(),
            'Inventory': self.inventory.toJSON(),
            'Skills': self.skill_list.toJSON(),
            'KnownBiomes': self.known_biomes.toJSON(),
            'CraftingStations': self.known_stations.toJSON(),
            'KnownRecipes': self.known_recipes.toJSON(),
            'DiscoveredMaterials': self.discovered_materials.toJSON(),
            'ShownTutorials': self.shown_tutorials.toJSON(),
            'DiscoveredUniques': self.discovered_uniques.toJSON(),
            'Trophies': self.trophies.toJSON(),
            'Journal': self.journal.toJSON(),
        }
        return data

    def printInfo(self, pp):
        def pr_list_raw(pp, prefix, a):
            pp.println(prefix)
            with PPWrap(pp):
                pp.println("Count:", len(a))
                for i in range(len(a)):
                    pp.println("{}:".format(i), a[i])
            return
        def pr_list(pp, prefix, a):
            pp.println(prefix)
            with PPWrap(pp):
                pp.println("Count:", len(a))
                for i in range(len(a)):
                    pp.println("{}:".format(i))
                    with PPWrap(pp):
                        a[i].printInfo(pp)
            return
        pp.println("Player Version:", self.version)
        pp.println("Player Name:", self.name)
        pp.println("Player ID:", self.player_id)
        pp.bytes("Starting Seed", self.start_seed)
        pp.println("Health:", self.health)
        pp.println("Max Health:", self.health_max)
        pp.println("Max Stamina:", self.stamina_max)
        pp.println("First Spawn:", self.first_spawn)
        pp.println("Time Since Death:", self.time_since_death)
        pp.println("Guardian Power:")
        with PPWrap(pp):
            pp.println("Name:", self.gp_name)
            pp.println("Cooldown:", self.gp_cooldown)
        pr_list(pp, "Active Food:", self.active_food)
        pp.println("Appearance:")
        with PPWrap(pp):
            self.appearance.printInfo(pp)
        pp.println("Inventory:")
        with PPWrap(pp):
            self.inventory.printInfo(pp)
        pp.println("Skills:")
        with PPWrap(pp):
           self.skill_list.printInfo(pp)
        pr_list(pp, "Known Biomes:", self.known_biomes)
        pr_list(pp, "Crafting Stations:", self.known_stations)
        pr_list_raw(pp, "Known Recipes:", self.known_recipes)
        pr_list_raw(pp, "Discovered Materials:", self.discovered_materials)
        pr_list_raw(pp, "Trophies:", self.trophies)
        pr_list_raw(pp, "Discovered Uniques:", self.discovered_uniques)
        pr_list(pp, "Journal:", self.journal)
        return


class FCH_WorldMarker(JSONIFace):
    def __init__(self):
        self.clear()

    def clear(self):
        self.text = ""
        self.point = [ 0.0, 0.0, 0.0 ]
        self.symbol = "0x00"
        self.crossed = False

    def fromBinary(self, binrdr, world_version):
        self.clear()
        self.text = binrdr.read_str()
        self.point = binrdr.read_float(3)
        symbol_val = binrdr.read_i32()
        self.symbol = Valheim.WorldMarkerType_i2a(symbol_val)
        if world_version >= 3:
            self.crossed = binrdr.read_bool()
        return

    def fromJSON(self, data):
        self.clear()
        with JDataAdaptor(data) as j:
            self.text = j.get_str('Text', '')
            self.point = j.get_list('PointXYZ', float, [0.0, 0.0, 0.0])
            self.symbol = j.get_str('Symbol', "0x00")
            self.crossed = j.get_bool('Crossed', False)
        return

    def toBinary(self, binwr):
        binwr.write(self.text)
        binwr.write_list(self.point)
        symbol_val = Valheim.WorldMarkerType_a2i(self.symbol)
        binwr.write(symbol_val)
        binwr.write(self.crossed)
        return

    def toJSON(self):
        data = {
            'Text': self.text,
            'PointXYZ': self.point,
            'Symbol': self.symbol,
            'Crossed':  self.crossed,
        }
        return data

    def printInfo(self, pp):
        pp.println("Text:", self.text)
        pp.println("Point (X,Y,Z):", self.point)
        pp.println("Symbol:", self.symbol)
        pp.println("Crossed:", self.crossed)


class FCH_WorldMarkerList(JSONIFace):
    def __init__(self):
        self.clear()

    def clear(self):
        self.markers = [] # FCH_WorldMarker

    def fromBinary(self, binrdr, world_version):
        self.clear()
        if world_version >= 2:
            count = binrdr.read_i32()
            for i in range(count):
                v = FCH_WorldMarker()
                v.fromBinary(binrdr, world_version)
                self.markers.append(v)
        return

    def fromJSON(self, data):
        self.clear()
        for item in data:
            v = FCH_WorldMarker()
            v.fromJSON(item)
            self.markers.append(v)
        return

    def toBinary(self, binwr):
        binwr.write(len(self.markers))
        for v in self.markers:
            v.toBinary(binwr)
        return

    def toJSON(self):
        data = []
        for v in self.markers:
            j = v.toJSON()
            data.append(j)
        return data

    def printInfo(self, pp):
        pp.println("Count:", len(self.markers))
        for i in range(len(self.markers)):
            pp.println("{}:".format(i))
            with PPWrap(pp):
                self.markers[i].printInfo(pp)
        return


class FCH_WorldVisibility(BinIFace, JSONIFace):
    CURRENT_VERSION = 4

    def __init__(self):
        self.clear()

    def clear(self):
        self.version = self.CURRENT_VERSION
        self.edge_length = 0
        self.pixel_data = WBitMatrix.WBitMatrix()
        self.marker_list = FCH_WorldMarkerList()
        self.public_position = False

    def fromBinary(self, binrdr):
        self.clear()
        self.version = binrdr.read_i32()
        if self.version > self.CURRENT_VERSION:
            die("Unknown FCH world version:", self.version)
        info("World Version:", self.version)
        self.edge_length = binrdr.read_i32()
        # Load the visibility matrix data
        self.pixel_data.set_dimensions(self.edge_length, self.edge_length)
        self.pixel_data.fromBinary(binrdr)
        # Load the marker list
        self.marker_list.fromBinary(binrdr, self.version)
        if self.version >= 4:
            self.public_position = binrdr.read_bool()
        return

    def fromJSON(self, data):
        self.clear()
        with JDataAdaptor(data) as j:
            self.public_position = j.get_bool('PublicPosition', False)
        if 'MapMarkers' in data:
            self.marker_list.fromJSON(data['MapMarkers'])
        return

    def toBinary(self, binwr):
        binwr.write(self.CURRENT_VERSION)
        binwr.write(self.edge_length)
        self.pixel_data.toBinary(binwr)
        self.marker_list.toBinary(binwr)
        binwr.write(self.public_position)
        return

    def toJSON(self):
        data = {
            'PublicPosition': self.public_position,
            'MapMarkers': self.marker_list.toJSON()
        }
        return data

    def readPBM(self, pbm_path):
        info("Attempting to read world data from PBM file...")
        img = PBMImage.PBMImage()
        img.load(pbm_path)

        if img.get_width() != img.get_height():
            die("Invalid World PBM file '{}':".format(pbm_path),
                "Dimensions are not square.")

        self.edge_length = img.get_width()
        # We just steal the data from the PBM, no sense copying it.
        self.pixel_data = img.get_matrix()
        info("Loading PBM succeeded.")

    def writePBM(self, pbm_path, overwrite=False):
        info("Attempting to write world data to PBM file...")
        img = PBMImage.PBMImage()
        img.set_matrix(self.pixel_data)
        img.write(pbm_path, overwrite=overwrite)
        info("Writing PBM succeeded.")

    def printInfo(self, pp):
        pp.println("Visibility Info Version:", self.version)
        pp.println("Edge Length:", self.edge_length)
        count = self.pixel_data.get_height() * self.pixel_data.get_width()
        pp.println("Visibility Byte Count:", count)
        pp.println("Public Position On Map:", self.public_position)
        pp.println("Map Markers:")
        with PPWrap(pp):
            self.marker_list.printInfo(pp)
        return


class FCH_World:
    def __init__(self):
        self.clear()

    def clear(self):
        self.uid = 0 # i64
        self.have_spawn_point = False
        self.spawn_point = [ 0.0, 0.0, 0.0 ]
        self.have_logout_point = False
        self.logout_point = [ 0.0, 0.0, 0.0 ]
        self.have_death_point = False
        self.death_point = [ 0.0, 0.0, 0.0 ]
        self.home_point = [ 0.0, 0.0, 0.0 ]
        self.have_vis_data = False
        self.vis_data = FCH_WorldVisibility()

    def fromBinary(self, binrdr, file_version):
        self.clear()
        self.uid = binrdr.read_i64()

        self.have_spawn_point = binrdr.read_bool()
        self.spawn_point = binrdr.read_float(count=3)

        self.have_logout_point = binrdr.read_bool()
        self.logout_point = binrdr.read_float(count=3)

        if file_version >= 30:
            self.have_death_point = binrdr.read_bool()
            self.death_point = binrdr.read_float(count=3)

        self.home_point = binrdr.read_float(count=3)

        if file_version >= 29:
            self.have_vis_data = binrdr.read_bool()
            if self.have_vis_data:
                world_bytes = binrdr.read_i32() # XXX we should use this...
                self.vis_data.fromBinary(binrdr)
        return

    def readJSON(self, json_path):
        self.clear()
        with open(json_path, 'r') as f:
            data = json.load(f)
        if 'SpawnPointXYZ' in data:
            self.have_spawn_point = True
        if 'LogoutPointXYZ' in data:
            self.have_logout_point = True
        if 'DeathPointXYZ' in data:
            self.have_death_point = True
        with JDataAdaptor(data) as j:
            self.uid = j.get_int('UID', 0)
            self.spawn_point = j.get_list('SpawnPointXYZ', float,
                                          [0.0, 0.0, 0.0], count=3)
            self.logout_point = j.get_list('LogoutPointXYZ', float,
                                          [0.0, 0.0, 0.0], count=3)
            self.death_point = j.get_list('DeathPointXYZ', float,
                                          [0.0, 0.0, 0.0], count=3)
            self.home_point = j.get_list('HomePointXYZ', float,
                                          [0.0, 0.0, 0.0], count=3)
        if 'VisibilityData' in data:
            self.vis_data.fromJSON(data['VisibilityData'])
            self.have_vis_data = True
        return

    def readPBM(self, pbm_path):
        try:
            self.vis_data.readPBM(pbm_path)
            self.have_vis_data = True
        except(FileNotFoundError):
            info("Missing PBM file for world:", pbm_path);
        return

    def toBinary(self, binwr):
        binwr.write_i64(self.uid)

        binwr.write(self.have_spawn_point)
        binwr.write_list(self.spawn_point)

        binwr.write(self.have_logout_point)
        binwr.write_list(self.logout_point)

        binwr.write(self.have_death_point)
        binwr.write_list(self.death_point)

        binwr.write_list(self.home_point)

        binwr.write(self.have_vis_data)
        if self.have_vis_data:
            # Temporary visibility data length
            size_pos = binwr.tell()
            binwr.write_i32(0)
            data_start = binwr.tell()
            self.vis_data.toBinary(binwr)
            data_end = binwr.tell()
            # Calculate and update the size
            size = data_end - data_start
            binwr.write_i32(size, pos=size_pos)
        return

    def writePBM(self, pbm_path, overwrite=False):
        if self.have_vis_data:
            self.vis_data.writePBM(pbm_path, overwrite=overwrite)

    def writeJSON(self, json_path, overwrite=False):
        data = {}
        data['UID'] = self.uid
        if self.have_spawn_point:
            data['SpawnPointXYZ'] = self.spawn_point
        if self.have_logout_point:
            data['LogoutPointXYZ'] = self.logout_point
        if self.have_death_point:
            data['DeathPointXYZ'] = self.death_point
        data['HomePointXYZ'] = self.home_point
        if self.have_vis_data:
            data['VisibilityData'] = self.vis_data.toJSON()
        # Write the data to disk.
        mode = 'w' if overwrite else 'x'
        with open(json_path, mode) as f:
            json.dump(data, f, indent=4)
        return

    def printInfo(self, pp):
        pp.println("UID:", self.uid)
        if self.have_spawn_point:
            pp.println("Spawn Point (X,Y,Z):", self.spawn_point)
        else:
            pp.println("Spawn Point (X,Y,Z): None")
        if self.have_logout_point:
            pp.println("Logout Point (X,Y,Z):", self.logout_point)
        else:
            pp.println("Logout Point (X,Y,Z): None")
        if self.have_death_point:
            pp.println("Death Point (X,Y,Z):", self.death_point)
        else:
            pp.println("Death Point (X,Y,Z): None")
        pp.println("Home Point (X,Y,Z):", self.home_point)
        pp.println("Visibility Data:")
        with PPWrap(pp):
            self.vis_data.printInfo(pp)
        return


class FCH_WorldManager:
    def __init__(self):
        self.clear()

    def clear(self):
        self.worlds = [] # FCH_World

    def fromBinary(self, binrdr, file_version):
        self.clear()
        world_count = binrdr.read_i32()
        for i in range(world_count):
            w = FCH_World()
            w.fromBinary(binrdr, file_version)
            self.worlds.append(w)

    def destruct(self, outdir, overwrite=False):
        for i in range(len(self.worlds)):
            path_base = '{}/world{}'.format(outdir, i)
            self.worlds[i].writeJSON(path_base + '.json', overwrite=overwrite)
            self.worlds[i].writePBM(path_base + '.pbm', overwrite=overwrite)
        pass

    def toBinary(self, binwr):
        binwr.write_i32(len(self.worlds))
        for w in self.worlds:
            w.toBinary(binwr)

    def construct(self, indir):
        self.clear()
        world_files = glob.glob(indir + '/world*.json')
        world_files.sort()
        for wf in world_files:
            w = FCH_World()
            w.readJSON(wf)
            # Replace the 'json' suffix with 'pbm'
            w.readPBM(wf[0:-4] + 'pbm')
            self.worlds.append(w)

    def printInfo(self, pp):
        pp.println("Worlds Visited:", len(self.worlds))
        for i in range(len(self.worlds)):
            with PPWrap(pp, "World {}".format(i)):
                self.worlds[i].printInfo(pp)
        return


class FCH_PlayerStats(BinIFace, JSONIFace):
    CURRENT_VERSION = 33
    
    def __init__(self):
        self.clear()

    def clear(self):
        self.version = 0
        self.kill_count = 0
        self.death_count = 0
        self.craft_count = 0
        self.build_count = 0

    def fromBinary(self, binrdr):
        self.clear()
        self.version = binrdr.read_i32()
        if (self.version > self.CURRENT_VERSION):
            die("Unknown FCH file version:", self.version)
        info("File Version:", self.version)
        if (self.version >= 28):
            self.kill_count = binrdr.read_i32()
            self.death_count = binrdr.read_i32()
            self.craft_count = binrdr.read_i32()
            self.build_count = binrdr.read_i32()

    def fromJSON(self, data):
        self.clear()
        self.version = self.CURRENT_VERSION
        with JDataAdaptor(data) as j:
            self.kill_count = j.get_int('Kills', 0)
            self.death_count = j.get_int('Deaths', 0)
            self.craft_count = j.get_int('Crafts', 0)
            self.build_count = j.get_int('Builds', 0)

    def toBinary(self, binwr):
        binwr.write(self.CURRENT_VERSION)
        binwr.write(self.kill_count)
        binwr.write(self.death_count)
        binwr.write(self.craft_count)
        binwr.write(self.build_count)

    def toJSON(self):
        data = {
            'Kills': self.kill_count,
            'Deaths': self.death_count,
            'Crafts': self.craft_count,
            'Builds': self.build_count,
        }
        return data

    def printInfo(self, pp):
        pp.println("File Version:", self.version)
        pp.println("Kills:", self.kill_count)
        pp.println("Deaths:", self.death_count)
        pp.println("Crafts:", self.craft_count)
        pp.println("Builds:", self.build_count)


class FCH_Root:
    def __init__(self):
        self.player_stats = FCH_PlayerStats()
        self.worlds = FCH_WorldManager()
        self.player_data = FCH_PlayerData()

    def _calculate_checksum(self, binrdr, byte_count):
        # Attempt to calculate the SHA-512 checksum. This is absurdly slow and
        # memory intensive, but we try to make things better by only
        # reading and updating in 8KB chunks. (memory vs speed tradeoff)
        if _have_sha512:
            blocks = byte_count // 8192
            rem = byte_count % 8192
            m = hashlib.sha512()
            for i in range(blocks):
                block = binrdr.read(8192)
                m.update(block)
            if rem != 0:
                block = binrdr.read(rem)
                m.update(block)
            return m.digest()
        else:
            return b'\x00' * 64 

    def fromBinary(self, binrdr):
        """
        Load an FCH file into memory.
        """
        # Before we can load the data we have some validation to perform.
        # The file is wrapped in the following format:
        # 
        #   i32 data_byte_count
        #   u8[data_byte_count] data
        #   i32 checksum_byte_count
        #   u8[checksum_byte_count] checksum
        #
        # The checksum is a SHA-512 of "data". The checksum is not validated
        # by the Valheim engine, at the time of writing. However, we're going
        # to validate it here if we have access to a SHA-512 algorithm.
        #
        info("Reading FCH file from disk...")
        byte_count = binrdr.read_i32()
        start_pos = binrdr.tell()
        # Skip the byte data for now, we'll extract the checksum first.
        binrdr.skip(byte_count)
        checksum_size = binrdr.read_i32()
        checksum = binrdr.read(checksum_size)

        # If we get here without failures, then the file is at least big enough
        # according to the basic check.
        #
        # Now calculate the checksum and verify the data!
        if _have_sha512:
            binrdr.push_pos(start_pos)
            calc_checksum = self._calculate_checksum(binrdr, byte_count)
            binrdr.pop_pos()
            if checksum != calc_checksum:
                pp = PrettyPrinter()
                pp.bytes("Disk Checksum", checksum)
                pp.bytes("Calculated Checksum", calc_checksum)
                die("Calculated checksum does not match the one loaded from "
                    "disk!")
        # Checksum seems legit, lets go!
        binrdr.push_pos(start_pos)
        self.player_stats.fromBinary(binrdr)
        self.worlds.fromBinary(binrdr, self.player_stats.version)
        self.player_data.fromBinary(binrdr, self.player_stats.version)
        binrdr.pop_pos()
        info("Reading FCH file succeeded.")

    def destruct(self, outdir, overwrite=False):
        """
        Deconstruct an in-memory FCH file to a series of output files:
          outdir/player.json
          outdir/worldN.json
          outdir/worldN.pbm

        Where 'N' is the world index. The world files are optional and will
        not exist if there isn't any world data in the FCH.
        """
        info("Destructing FCH data...")
        path = outdir + '/player.json'
        data = {
            'PlayerStats': self.player_stats.toJSON(),
            'PlayerData': self.player_data.toJSON(),
        }
        mode = 'w' if overwrite else 'x'
        with open(path, mode) as f:
            json.dump(data, f, indent=4)
        self.worlds.destruct(outdir, overwrite=overwrite)
        info("Destructing succeeded.")

    def toBinary(self, binwr):
        """
        Write an FCH file.
        """
        info("Writing FCH file to disk...")
        byte_count_pos = binwr.tell()
        # Temporary byte count
        binwr.write_i32(0)
        data_start_pos = binwr.tell()
        # Write all the data.
        self.player_stats.toBinary(binwr)
        self.worlds.toBinary(binwr)
        self.player_data.toBinary(binwr)
        data_end_pos = binwr.tell()
        byte_count = data_end_pos - data_start_pos
        # Checksum bytes
        binwr.flush()
        with BinReader.BinReader(binwr.get_path()) as br:
            br.push_pos(data_start_pos)
            checksum = self._calculate_checksum(br, byte_count)
            br.pop_pos()
        binwr.write_i32(len(checksum))
        binwr.write_raw(checksum)
        # finally update the byte count
        binwr.write_i32(byte_count, pos=byte_count_pos)
        info("Writing FCH data succeeded.")

    def construct(self, indir):
        """
        Construct an in-memory FCH file from a series of input files:
          indir/player.json
          indir/worldN.json
          indir/worldN.pbm

        Where 'N' is the world index. The world files are optional and do not
        have to exist.
        """
        info("Constructing FCH data...")
        path = indir + '/player.json'
        with open(path, 'r') as f:
            data = json.load(f)
        if 'PlayerStats' in data:
            self.player_stats.fromJSON(data['PlayerStats'])
        if 'PlayerData' in data:
            self.player_data.fromJSON(data['PlayerData'])
        self.worlds.construct(indir)
        info("Construction succeeded.")

    def printInfo(self):
        pp = PrettyPrinter()
        with PPWrap(pp, "Player Stats"):
            self.player_stats.printInfo(pp)
        with PPWrap(pp, "World Data"):
            self.worlds.printInfo(pp)
        with PPWrap(pp, "Player Data"):
            self.player_data.printInfo(pp)

# vim:ts=4:sw=4:et
