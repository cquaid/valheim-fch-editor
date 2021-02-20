# FCH File Format

The FCH format uses only a few data types, which is why some of the unknown
blocks are broken up as they are.

The following data types have been observed:
* *u8* - 1-byte value, occasionally seen for booleans
* *u32* - 4 byte integers are stored in little-endian
* *float* - 4 byte floating point value
* *str* - A u8 length followed by the string data (excluding a NUL-terminator)

## Header

The header data is currently unknown, it's always 24 bytes long, likely broken up into 4-byte chunks.

| Type | Name | Description |
| ---- | ---- | ----------- |
| u8[4] | Unknown 1 | Unknown |
| u8[4] | Unknown 2 | Unknown |
| u8[4] | Unknown 3 | Unknown |
| u8[4] | Unknown 4 | Unknown |
| u8[4] | Unknown 5 | Unknown |
| u8[4] | Unknown 6 | Unknown |

## Minimap Block

This block is comprised of a Minimap Count followed by the minimap data for each entry.
Each minimap in the block has a header, visibility data, and a list of map markers

| Type | Name | Description |
| ---- | ---- | ----------- |
| u32  | Count | Number of minimaps stored in the file |

### Minimap Header

68 bytes of unknown data; part, of which, might be the map seed or some form of identifier to pair the map data with an actual map file.

| Type | Name | Description |
| ---- | ---- | ----------- |
| u[68] | Unknown | Unknown |

### Minimap Visibility

The visibility section starts with an Edge Length. Squaring this value gives the number of bytes used by the visibility data.

Each byte has one of two values:
- 0: hidden/fog
- 1: visible

The map is stored as a series of EdgeLength rows with EdgeLength columns each.
The first row represents the bottom of the minimap, as seen on screen.
Thus the rows are numbered: [EdgeLen-1, 0]

| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | EdgeLen | Number of bytes for each edge of the minimap |
| u8[EdgeLen*EdgeLen] | Visibility | Minimap visibility data |

### Minimap Markers

A list of the markers (mostly player-defined) on the minimap.
A u32 count preceeds the marker entries.

*Header:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | Count | Number of minimap markers in the list |

*Entries:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| string | Text | Marker text |
| float | Coord1 | One of the coordinates for marker placement |
| float | Unknown | Only populated for boss markers? |
| float | Coord2 | One of the coordinates for marker placement |
| u32 | Symbol | Which symbol is used (see below) |
| u8 | Strike | Boolean, if True: the symbol is Xed out |

*Known Symbol Values:*
- 0x00: Campfire
- 0x01: House
- 0x02: The T thing
- 0x03: Dot
- 0x04: Gate/Portal
- 0x09: Boss marker

## Player Block

The player data is pretty extensive and is broken up into several sections.

### Header

| Type | Name | Description |
| ---- | ---- | ----------- |
| string | Name | Player name |
| u8[8] | ID | Some form of per-player ID. This, paired with the name, uniquely identifies a player |
| u8[27] | Unknown | Unknown data |

### Giant Power

The currently "equipped" big-boss power.

| Type | Name | Description |
| ---- | ---- | ----------- |
| string | Name | Which power is active, see below |
| u8[4] | Unknown 1 | Related to the cooldown after use |
| u8[4] | Unknown 2 | Unknown |

*Known Power Names:*
- GP_Eikthyr
- GP_GDKing
- GP_Bonemass

### Inventory

Cautions:
- Inventory item names are the keys used in-game, so the must be correct
- Ensure all items are in unique slots (Row, Column) pairs
- Ensure all items are in valid slots (Row: 0-3, Column: 0-7)


*Header:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | Count | Number of inventory items |

*Entries:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| string | Name | Item name/type |
| u32 | Count | Stack count. Always 1 for equipment |
| float | Durability | Item Durability. Always 100.0 for non-equips. Often > 100 for equips. |
| u32 | Column | Which colomn the item is in. Range: [0, 7] |
| u32 | Row | Which row the item is in. Range: [0, 3] |
| u8 | Equipped | Boolean: 1 if item is equipped, 0 otherwise |
| u32 | Level | Item level. Always 1 for non-equips |
| u32 | Style | Paint style. Only used for shields, always 0 for non-shields |
| u8[8] | CrafterID | ID of the player who crafted the item |
| string | CrafterName | Name of the player who crafted the item |

### Known Recipes

Recipes you've discovered.

This is just a string table. It starts with a u32 count followed by a series of string entries.

### Crafting Stations

Highest level discovered/built for the upgradable crafting stations:
- Workbench
- Forge
- Cauldron

*Header:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | Count | Number of entries in this list |

*Entries:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| string | Name | Station name |
| u32 | Level | Highest level |

### Discovered Items

Items you've made or picked up.

This is just a string table. It starts with a u32 count followed by a series of string entries.

### Milestones (?)

I'm uncertain of what this is. I'm calling them "milestones", but they may be event names.

This is just a string table. It starts with a u32 count followed by a series of string entries.

### Player Unknown 1

I have no clue what this is. It might be another string table, but I've only seen the count be 0.

| Type | Name | Description |
| ---- | ---- | ----------- |
| u8[4] | Unknown | Always [ 0, 0, 0, 0 ]? |

### Trophies

List of trophies you've picked up.

This is just a string table. It starts with a u32 count followed by a series of string entries.

### Player Unknown 2

### Journal

List of journal entries.

This is a fancier string table, each entry is two strings each.

*Header:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | Count | Number of entries in this list |

*Entries:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| string | Label | Name of the label variable |
| string | Text | Name of the text variable |

### Appearance

Notes:
- c1, c2, and c3 always seem to be the same value?

| Type | Name | Description |
| ---- | ---- | ----------- |
| string | Beard | Beard type name |
| string | Hair | Hair type name |
| float | c1 | Unknown, seems to be related to complexion |
| float | c2 | Unknown, seems to be related to complexion |
| float | c3 | Unknown, seems to be related to complexion |
| float | u1 | Unknown |
| float | u2 | Unknown |
| float | u3 | Unknown, possibly the hair color |
| u32 | Body Type | 0 for the male body, 1 for the female body |

### Active Food

Eaten/Active food.

Notes:
- The count likely caps at 3, though I haven't tested

*Header:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | Count | Number of entries in this list |

*Entries:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| string | Name | Food name |
| float | Unknown 1 | Unknown, likely related to remaining time |
| float | Unknown 2 | Unknown, likely related to remaining time |

### Player Unknown 3

4-byte value. Not sure what this is, Always has the value 2? [ 0x02, 0x00, 0x00, 0x00 ]

### SKills

Skill data.

*Header:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | Count | Number of entries in this list |

*Entries:*
| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | Type | Skill type/ID, see below |
| float | Level | Whole number part: level; fractional part: experience percentage |
| float | Unknown | Unknown |

*Known Skill Types:*
- 0x01: Sword
- 0x02: Knives
- 0x03: Clubs
- 0x04: Polearms
- 0x05: Spears
- 0x06: Blocking
- 0x07: Axes
- 0x08: Bows
- 0x0b: Unarmed
- 0x0c: Pickaxes
- 0x0d: Woodcutting
- 0x65: Sneaking
- 0x66: Jumping
- 0x67: Swimming

### Checksum (?)

This looks like a checksum to me, just because it's 64-bytes long. But I haven't been able to calculate a SHA-512 checksum that matches this value and I've sliced the file a few different ways. This chunk ALWAYS updates it seems and I can't get a stable load of a character that doesn't modify some value yet. It's worth noting that if this *is* a checksum, they don't actual validate anything with it since modifying the file works fine.

| Type | Name | Description |
| ---- | ---- | ----------- |
| u32 | Count | Number of bytes following |
| u8[Count] | Checksum | The supposed checksum value |

