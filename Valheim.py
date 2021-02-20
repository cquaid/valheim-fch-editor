# Copyright 2021-2021, cQuaid and the valheim-fch-editor contributors
# SPDX-License-Identifier: MIT

# 4-5, 7-8 are unknown
MapMarkerType_codex = {
    0: "Campfire",
    1: "House",
    2: "T",
    3: "Dot",
    6: "Gate",
    9: "Boss",
}

MapMarkerType_invcodex = {}
for key in MapMarkerType_codex:
    MapMarkerType_invcodex[ MapMarkerType_codex[key] ] = key

SkillType_codex = {
    0x01: "Sword",
    0x02: "Knives",
    0x03: "Clubs",
    0x04: "Polearms",
    0x05: "Spears",
    0x06: "Blocking",
    0x07: "Axes",
    0x08: "Bows",
    0x0b: "Unarmed",
    0x0c: "Pickaxes",
    0x0d: "Woodcutting",
    0x65: "Sneaking",
    0x66: "Jumping",
    0x67: "Swimming",
}

SkillType_invcodex = {}
for key in SkillType_codex:
    SkillType_invcodex[ SkillType_codex[key] ] = key

def MapMarkerType_i2a(i):
    global MapMarkerType_codex
    return MapMarkerType_codex.get(i, "0x{0:02x}".format(i))

def MapMarkerType_a2i(a):
    global MapMarkerType_invcodex
    if a in MapMarkerType_invcodex:
        return MapMarkerType_invcodex[a]
    return int(a, 16)

def SkillType_i2a(i):
    global SkillType_codex
    return SkillType_codex.get(i, "0x{0:02x}".format(i))

def SkillType_a2i(a):
    global SkillType_invcodex
    if a in SkillType_invcodex:
        return SkillType_invcodex[a]
    return int(a, 16)

# vim:ts=4:sw=4:autoindent
