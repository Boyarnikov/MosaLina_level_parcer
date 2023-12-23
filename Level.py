from Transform import Transform
from Item import Item
from BinHelpers import explain_bin

import json
import struct
import random


#  3b             1b             1b             1b + nb         4b              24b
# [ color      ] [ fruit type ] [ boss/scroll ] [locked items] [ items amount ] [ entrance portal position and rotation]
# 105, 105, 105,   0,             1,             0,              2, 0, 0, 0,     0, 0, 0, 0, 0, 192, 114, 64, 0, ...
class Level:
    """Stores level with all items and level specific data, such as color and locked items"""
    MAGIC_VAR = (0).to_bytes(2, "little")
    items = None
    color = (105, 105, 105)
    fruit = 0
    level_flag = 0
    locked_items = ()
    portal_transform = None

    def __init__(self, color=(105, 105, 105), fruit=0, boss_allowed=False, scroll=False, level_flag=0, locked_items=(),
                 portal_transform=None):
        self.items = []
        self.color = color
        self.fruit = fruit
        if level_flag:
            self.level_flag = level_flag
        elif scroll:
            self.level_flag = 2
        elif boss_allowed:
            self.level_flag = 1
        else:
            self.level_flag = 0
        if portal_transform is None:
            portal_transform = Transform(100, 100, 0)
        self.portal_transform = portal_transform
        self.locked_items = locked_items

    def to_byte(self):
        """Converts Level object to byte form"""
        data = bytes()
        data += self.color[0].to_bytes(1) + self.color[1].to_bytes(1) + self.color[2].to_bytes(1)
        data += self.fruit.to_bytes(1)
        data += self.level_flag.to_bytes(1)
        data += len(self.locked_items).to_bytes(1)
        for i in self.locked_items:
            data += i.to_bytes(1)
        data += (len(self.items) + 1).to_bytes(2, "little")
        data += self.MAGIC_VAR
        data += self.portal_transform.convert_to_byte()

        for i in self.items:
            data += i.to_byte()

        return data

    @staticmethod
    def from_json(j):
        pass

    def to_json(self):
        data = {'Level': {"color": self.color, "fruit": self.fruit, "flag": self.level_flag, "items": [],
                          "portal_transform": {"x": self.portal_transform.position[0],
                                               "y": self.portal_transform.position[1],
                                               "r": self.portal_transform.rotation}}}

        for i in self.items:
            data["Level"]["items"].append(json.loads(i.to_json()))
        j = json.dumps(data, sort_keys=True, indent=4)
        return j

    @staticmethod
    def from_byte(array, return_size=False):
        """
        creates Level object form file form
        :param array: byte data
        :param return_size: if is True, returns the amount of bytes used to create object
        """
        color = (array[0], array[1], array[2])
        fruit = array[3]
        flag = array[4]

        locked_amount = array[5]
        locked_items = [array[6 + i] for i in range(locked_amount)]

        items = int.from_bytes(array[6 + locked_amount:8 + locked_amount], "little")
        portal_transform = Transform.create_from_byte(array[10 + locked_amount:])

        level = Level(color=color, fruit=fruit, level_flag=flag, locked_items=locked_items,
                      portal_transform=portal_transform)

        level.MAGIC_VAR = array[8 + locked_amount:10 + locked_amount]

        print(f"Init level with: [{explain_bin(array[:34 + locked_amount])}]")
        ruined = False

        level.items = []
        array = array[34 + locked_amount:]
        items_size = 0
        for i in range(items - 1):
            new_item, item_size = Item.from_byte(array, return_size=True)
            if new_item.item_id == 0:
                print(explain_bin(array[11:11 + 8]))
                print(struct.unpack("d", array[11:11 + 8])[0])
                print(struct.unpack("d", array[11 + 8:11 + 8 + 8])[0])
                print(struct.unpack("d", array[11 + 8 + 8:11 + 8 + 8 + 8])[0])
            array = array[item_size:]
            items_size += item_size
            level.items.append(new_item)

            if new_item.item_id == 0:
                ruined = True
        if ruined:
            print(F"This level have an 0id item ):")

        #print(level.to_json())
        if return_size:
            return level, 34 + locked_amount + items_size
        return level

    def __copy__(self):
        return Level.from_byte(self.to_byte())
