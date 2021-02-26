# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT

WorldMarkerType_codex = {
    0: "Campfire",
    1: "House",
    2: "T",
    3: "Dot",
    4: "Grave", # Internal
    5: "Bed", # Internal
    6: "Gate",
    7: "Shout", # Internal
    # 8 = None
    9: "Boss",
    10: "Player", # Internal
    11: "RandomEvent", # Internal
    12: "Ping", # Internal
    13: "EventArea", # Internal
}

WorldMarkerType_invcodex = {}
for key, value in WorldMarkerType_codex.items():
    WorldMarkerType_invcodex[ value ] = key

SkillType_codex = {
    0x01: "Sword",
    0x02: "Knives",
    0x03: "Clubs",
    0x04: "Polearms",
    0x05: "Spears",
    0x06: "Blocking",
    0x07: "Axes",
    0x08: "Bows",
    0x09: "FireMagic",
    0x0a: "FrostMagic",
    0x0b: "Unarmed",
    0x0c: "Pickaxes",
    0x0d: "Woodcutting",
    0x64: "Jumping",
    0x65: "Sneaking",
    0x66: "Running",
    0x67: "Swimming",
}

SkillType_invcodex = {}
for key, value in SkillType_codex.items():
    SkillType_invcodex[ value ] = key

BiomeType_codex = {
    1: "Meadows",
    2: "Swamp",
    4: "Mountains",
    8: "Black Forest",
    16: "Plains",
    32: "Ashlands",
    64: "Deep North",
    256: "Ocean",
    512: "Mistlands",
}

BiomeType_invcodex = {}
for key, value in BiomeType_codex.items():
    BiomeType_invcodex[ value ] = key


def WorldMarkerType_i2a(i):
    global WorldMarkerType_codex
    return WorldMarkerType_codex.get(i, "0x{0:02x}".format(i))

def WorldMarkerType_a2i(a):
    global WorldMarkerType_invcodex
    if a in WorldMarkerType_invcodex:
        return WorldMarkerType_invcodex[a]
    return int(a, 16)

def SkillType_i2a(i):
    global SkillType_codex
    return SkillType_codex.get(i, "0x{0:02x}".format(i))

def SkillType_a2i(a):
    global SkillType_invcodex
    if a in SkillType_invcodex:
        return SkillType_invcodex[a]
    return int(a, 16)

def BiomeType_i2a(i):
    global BiomeType_codex
    return BiomeType_codex.get(i, "0x{0:02x}".format(i))

def BiomeType_a2i(a):
    global BiomeType_invcodex
    if a in BiomeType_invcodex:
        return BiomeType_invcodex[a]
    return int(a, 16)

# vim:ts=4:sw=4:autoindent
