import zlib
import random
import struct
import math
from os import walk


def explain_bin(array):
    return [int(i) for i in array]


class LevelGenerator:
    def __init__(self):
        mypath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\"
        output = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\RandomPack2\\data.mld"

        folders = next(walk(mypath), (None, None, []))[1]  # [] if no file
        islands = [LevelPack.read(mypath + f + "\\data.mld") for f in folders if
                   "gen" in f and "platform" in f]  # gonna use frogs on layout idk :D frog==34
        print(islands)
        layouts = [LevelPack.read(mypath + f + "\\data.mld") for f in folders if "gen" in f and "layout" in f]
        print(layouts)
        paths = [LevelPack.read(mypath + f + "\\data.mld") for f in folders if
                 "gen" in f and "paths" in f]  # arrows on layout arrows==26
        print(paths)
        enemy = [LevelPack.read(mypath + f + "\\data.mld") for f in folders if
                 "gen" in f and "enemy" in f]  # frogs on islands and paths?
        print(enemy)
        decor = [LevelPack.read(mypath + f + "\\data.mld") for f in folders if
                 "gen" in f and "decor" in f]  # arrows on islands and paths?
        print(decor)

        SIZE = 9
        l = LevelPack(SIZE, name="Hi", autor="Hello")
        for i in range(SIZE):
            # l.levels[i] = random.choice(random.choice(layouts).levels).__copy__()
            print(l.levels, "==========================================")
            # l.levels[i].substitute(36, paths)
            # l.levels[i].substitute(34, islands)
            # l.levels[i].substitute(34, enemy, probability=0.9)
            # l.levels[i].substitute(36, decor, probability=0.5)
        l.save(output)


class Transform:
    position = [0, 0]
    rotation = 0

    def __init__(self, x, y, r):
        self.position = [x, y]
        self.rotation = r

    @staticmethod
    def create_from_byte(array):
        return Transform(struct.unpack("d", array[:8])[0], struct.unpack("d", array[8:16])[0],
                         struct.unpack("d", array[16:24])[0])

    def convert_to_byte(self):
        return struct.pack("d", self.position[0]) + struct.pack("d", self.position[1]) + struct.pack("d", self.rotation)

    def localize_object_transform(self, old_root, new_root):
        """change root of the object"""
        new_transform = Transform(self.position[0], self.position[1], self.rotation)
        new_transform.position[0] -= old_root.position[0]
        new_transform.position[1] -= old_root.position[1]

        alpha = new_root.rotation

        new_transform.position[0] = new_transform.position[0] * math.cos(alpha) - new_transform.position[1] * math.sin(
            alpha)
        new_transform.position[1] = new_transform.position[0] * math.sin(alpha) + new_transform.position[1] * math.cos(
            alpha)

        new_transform.rotation += alpha

        new_transform.position[0] += new_root.position[0]
        new_transform.position[1] += new_root.position[1]
        return new_transform


# [ id ] [ transform 24b ] [ joint and 8b speed ]
# 17, 0, 64, 143, ..., 63, 1, 0, 0, ... 0, 0, 0
class Item:
    item_id = 0
    transform = None
    joint = None
    expanded_info = None

    without_joint = [1, 3, 4, 5, 6]
    one_b = [4, 5, 6]

    item_names = {
        "fruit": 2,
        "exit_portal": 1,
        "clamp": 3,
        "leaves": 6,
        "rail": 7,
        "frog": 34
    }

    def __init__(self, item_id=-1, transform=None, joint=None, expanded_info=None):
        if item_id == -1:
            return

        self.item_id = item_id
        if transform is None:
            transform = Transform(100, 100, 0)
        self.transform = transform

        if item_id not in Item.without_joint:
            if joint is None:
                joint = (0, 0)
            self.joint = joint

        if item_id == Item.item_names["clamp"]:
            if expanded_info is None:
                expanded_info = [16.0, 8.0]
            self.expanded_info = expanded_info

        if item_id == Item.item_names["rail"]:
            if expanded_info is None:
                expanded_info = [100.0]
            self.expanded_info = expanded_info

        if item_id == Item.item_names["frog"]:
            if expanded_info is None:
                expanded_info = [0.0]
            self.expanded_info = expanded_info

        if item_id in Item.one_b:
            if expanded_info is None:
                expanded_info = [0]
            self.expanded_info = expanded_info

    def __copy__(self):
        return Item(self.item_id, self.transform, self.joint, self.expanded_info)

    @staticmethod
    def create_from_byte(array, return_size=True):
        size = 26
        item = Item()
        item.item_id = int.from_bytes(array[0:2], "little")
        item.transform = Transform.create_from_byte(array[2:])

        if item.item_id not in Item.without_joint:
            item.joint = (array[size], struct.unpack("d", array[size + 1:size + 9])[0])
            size += 9

        item.expanded_info = []
        if item.item_id == Item.item_names["clamp"]:
            item.expanded_info.append(struct.unpack("d", array[size:size + 8])[0])
            size += 8
            item.expanded_info.append(struct.unpack("d", array[size:size + 8])[0])
            size += 8
            # print(item.expanded_info, ": expanded")

        if item.item_id == Item.item_names["rail"] or item.item_id == Item.item_names["frog"]:
            item.expanded_info.append(struct.unpack("f", array[size:size + 4])[0])
            # print(item.expanded_info)
            size += 4

        if item.item_id in Item.one_b:
            size += 1
            item.expanded_info.append(array[size - 1])

        # print(f"Init Item with: [{explain_bin(array[:size])}]")
        # print(f"Item is:        [{explain_bin(item.convert_to_byte())}]")

        if return_size:
            return item, size
        return item

    def convert_to_byte(self):
        data = bytes()
        data += self.item_id.to_bytes(2, "little")
        data += self.transform.convert_to_byte()

        if self.item_id not in Item.without_joint:
            data += self.joint[0].to_bytes(1) + struct.pack("d", self.joint[1])

        if self.item_id == Item.item_names["clamp"]:
            data += struct.pack("d", self.expanded_info[0])
            data += struct.pack("d", self.expanded_info[1])

        if self.item_id == Item.item_names["rail"] or self.item_id == Item.item_names["frog"]:
            data += struct.pack("f", self.expanded_info[0])

        if self.item_id in Item.one_b:
            data += self.expanded_info[0].to_bytes(1)

        return data

    # 1:exit portal does not have joint
    # 4:hinge_minus, 5:hinge_plus does not have joint, have additional 1b
    # 3:clamp use 2 floats instead of joint
    # 7:rail adds float - length
    # 6:leaves have 1b for length, no joint
    # 34:frog have 4b more data? idk


#  3b             1b             1b             1b + nb         4b              24b
# [ color      ] [ fruit type ] [ boss/scroll ] [locked items] [ items amount ] [ entrance portal position and rotation]
# 105, 105, 105,   0,             1,             0,              2, 0, 0, 0,     0, 0, 0, 0, 0, 192, 114, 64, 0, ...
class Level:
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

    def convert_to_byte(self):
        data = bytes()
        data += self.color[0].to_bytes(1) + self.color[1].to_bytes(1) + self.color[2].to_bytes(1)
        data += self.fruit.to_bytes(1)
        data += self.level_flag.to_bytes(1)
        data += len(self.locked_items).to_bytes(1)
        for i in self.locked_items:
            data += i.to_bytes(1)
        data += (len(self.items) + 1).to_bytes(4, "little")
        data += self.portal_transform.convert_to_byte()

        for i in self.items:
            data += i.to_byte()

        return data

    @staticmethod
    def create_from_byte(array, return_size=False):
        color = (array[0], array[1], array[2])
        fruit = array[3]
        flag = array[4]
        print(flag, "FLAG")
        locked_amount = array[5]
        locked_items = [array[6 + i] for i in range(locked_amount)]
        print(explain_bin(array[6 + locked_amount:8 + locked_amount]))
        items = int.from_bytes(array[6 + locked_amount:8 + locked_amount], "little")
        print(items, "ITEMS")
        portal_transform = Transform.create_from_byte(array[10 + locked_amount:])

        level = Level(color=color, fruit=fruit, level_flag=flag, locked_items=locked_items,
                      portal_transform=portal_transform)

        print(f"Init level with: [{explain_bin(array[:34 + locked_amount])}]")

        level.items = []
        array = array[34 + locked_amount:]
        items_size = 0
        for i in range(items - 1):
            new_item, item_size = Item.create_from_byte(array, return_size=True)
            array = array[item_size:]
            items_size += item_size
            level.items.append(new_item)

        if return_size:
            return level, 34 + locked_amount + items_size
        return level

    def substitute(self, _id, level_packs, probability=1.0):
        to_del = []
        to_add = []

        print(f"found {len(self.items)} substitute items")
        for ind, i in enumerate(self.items):
            if i.item_id == _id:
                print("Подстановка")
                to_del.append(i)
                scene = random.choice(random.choice(level_packs).levels)
                print(scene, "SCENE________________")
                root = i.transform
                print(root)
                if abs(root.position[0]) + abs(root.position[1]) > 1000000:
                    continue
                if random.random() > probability:
                    continue
                for item in scene.items:
                    itm = item.__copy__()
                    itm.transform = itm.transform.localize_object_transform(scene.portal_transform, root)
                    to_add.append(itm)

        for i in to_del:
            self.items.remove(i)
        for i in to_add:
            self.items.append(i)

    def __copy__(self):
        return Level.create_from_byte(self.convert_to_byte())


class LevelPack:
    levels = None
    workshop_id = 0
    name = "unknown"
    author = "unknown"
    format = 9  # this script is based on the 9th version
    levels_raw = bytes()

    def __init__(self, size=9, name="unknown", autor="unknown"):
        self.levels = []
        for i in range(size):
            self.levels.append(Level())
        self.name = name
        self.autor = autor

    @staticmethod
    def reload(filepath):
        with open(filepath, "rb") as f, open("_" + filepath, "wb") as fw:
            tmp = f.read(2)
            print(tmp)
            fw.write(tmp)
            tmp = f.read(8)
            print(tmp)
            fw.write(tmp)
            tmp = f.read(1)
            print(tmp)
            fw.write(tmp)
            tmp = f.read(int.from_bytes(tmp))
            print(tmp)
            fw.write(tmp)
            tmp = f.read(2)
            print(tmp)
            fw.write(tmp)

    @staticmethod
    def read(filepath):
        pack = LevelPack(0)

        pack.levels = []
        with open(filepath, "rb") as f:
            pack.format = int.from_bytes(f.read(2), "little")
            pack.workshop_id = int.from_bytes(f.read(8), "little")
            pack.name = f.read(int.from_bytes(f.read(1))).decode("utf-8")
            pack.author = f.read(int.from_bytes(f.read(1))).decode("utf-8")
            pack.level_count = int.from_bytes(f.read(2), "little")

            print(f'Opened level pack "{pack.name}" from {pack.author}. Expected level count: {pack.level_count}')

            pack.levels_raw = f.read()
            pack.data = zlib.decompress(pack.levels_raw)
            print(f"whole contain {len(pack.data)}b")
            print(pack.data)

            data = pack.data
            while len(data):
                new_level, size = Level.create_from_byte(data, return_size=True)
                data = data[size:]
                pack.levels.append(new_level)

            return pack

    @staticmethod
    def read_header(filepath):
        with open(filepath, "rb") as f:
            format = int.from_bytes(f.read(2), "little")
            workshop_id = int.from_bytes(f.read(8), "little")
            name = f.read(int.from_bytes(f.read(1))).decode("utf-8")
            author = f.read(int.from_bytes(f.read(1))).decode("utf-8")
            level_count = int.from_bytes(f.read(2), "little")
            print(format, workshop_id, name, author, level_count)

            levels_raw = f.read()
            data = zlib.decompress(levels_raw)
            print(explain_bin(data))

    def save(self, filepath, name=None):
        with open(filepath, "wb") as f:
            f.write(self.format.to_bytes(2, "little"))
            f.write(self.workshop_id.to_bytes(8, "little"))
            if not name:
                name = self.name
            f.write(len(name).to_bytes(1))
            f.write(name.encode('utf-8'))
            f.write(len(self.author).to_bytes(1))
            f.write(self.author.encode('utf-8'))
            f.write(len(self.levels).to_bytes(2, "little"))

            # f.write(self.levels_raw)

            level_data = bytes()
            for i in self.levels:
                level_data += i.convert_to_byte()

            print(self.data)
            print(level_data)

            print("DATA")
            print(explain_bin(zlib.decompress(self.levels_raw)))
            print(explain_bin(level_data))

            f.write(zlib.compress(level_data, level=-1))
