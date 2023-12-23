import zlib
import random
import struct
import math


def beautify_binary(_data):
    new_data = ""
    for i, ch in enumerate(_data):
        c = str(hex(ch))
        c += (6 - len(c)) * " "
        new_data += c
        if not i % 16:
            new_data += "\n"
    print(f"{i} bytes of level data found")
    return new_data


def add_transform(t1, t2):
    return t1[0] + t2[0], t1[1] + t2[1], t1[2] + t2[2]


def sub_transform(t1, t2):
    print(t1, t2)
    return t1[0] - t2[0], t1[1] - t2[1], t1[2] - t2[2]


def localize_object_transform(transform, old_root, new_root):
    new_transform = list(transform)
    new_transform[0] -= old_root[0]
    new_transform[1] -= old_root[1]

    alpha = new_root[2]

    new_transform[0], new_transform[1] = new_transform[0] * math.cos(alpha) - new_transform[1] * math.sin(alpha), \
        new_transform[0] * math.sin(alpha) + new_transform[1] * math.cos(alpha)

    new_transform[2] += alpha

    new_transform[0] += new_root[0]
    new_transform[1] += new_root[1]
    return new_transform


def add_object_transform(item, old, new):
    transform = localize_object_transform(Level.get_object_transform(item), old, new)
    new_item = item[:2] + struct.pack("d", transform[0]) + \
               struct.pack("d", transform[1]) + \
               struct.pack("d", transform[2]) + item[26:]
    return new_item


class Level:
    _position = (0, 0)
    items = []
    _header = []
    size = 0
    transform = (0, 0, 0)
    offset = 0

    def bin_to_int(array):
        return [int(i) for i in array]

    def __init__(self, pointer=None, level_data=None):
        self.items = []
        self._header = []
        if pointer is None:
            return
        start_pointer = pointer
        self.offset = level_data[pointer + 5]
        item_count = level_data[pointer + 5 + self.offset + 1] - 1
        print(f"level:")
        self._header = Level.bin_to_int(level_data[pointer: pointer + 34 + self.offset])
        print(self._header)
        pointer += 34 + self.offset
        self.transform = (struct.unpack("d", level_data[pointer - 24:pointer - 16])[0],
                          struct.unpack("d", level_data[pointer - 16:pointer - 8])[0],
                          struct.unpack("d", level_data[pointer - 8:pointer])[0])
        print(f"items: {item_count}")

        for i in range(item_count):
            size = 35
            if level_data[pointer] in [1, 4, 5, 6]:
                size -= 8
            if level_data[pointer] in [3]:
                size += 7
            self.items.append(level_data[pointer: pointer + size])
            print(Level.bin_to_int(self.items[-1]))
            pointer += size
        self.size = pointer - start_pointer

        self._header = self._header[:6 + self.offset] + [len(self.items) + 1] + self._header[7 + self.offset:]

    def __str__(self):
        res = ""
        res += str(self._header) + "\n"
        for i in self.items:
            res += str(Level.bin_to_int(i)) + "\n"
        return res

    def __copy__(self):
        l = Level()
        l.items = self.items.copy()
        l._header = self._header.copy()
        l._header[0] = random.randint(0, 255)
        l._header[1] = random.randint(0, 255)
        l._header[2] = random.randint(0, 255)
        l._header[3] = random.randint(0, 2)

        l.offset = self.offset
        l.transform = self.transform
        return l


    def substitute(self, _id, level_packs, probability = 1.0):
        to_del = []
        to_add = []
        print(f"всего {len(self.items)} предсетов")
        for ind, i in enumerate(self.items):
            if i[0] == _id:
                print("Подстановка")
                to_del.append(i)
                scene = random.choice(random.choice(level_packs).levels)
                print(Level.bin_to_int(i))
                root = Level.get_object_transform(i)
                print(root)
                if abs(root[0]) + abs(root[1]) + abs(root[2]) > 1000000:
                    continue
                if random.random() > probability:
                    continue
                for item in scene.items:
                    if item[0]:
                        print(Level.bin_to_int(item))
                        to_add.append(add_object_transform(item, scene.transform, root))

        for i in to_del:
            self.items.remove(i)
        for i in to_add:
            self.items.append(i)

        self._header = self._header[:6 + self.offset] + [len(self.items) + 1] + self._header[7 + self.offset:]

    def get_object_transform(item):

        x = struct.unpack("d", item[2:10])[0]
        y = struct.unpack("d", item[10:18])[0]
        r = struct.unpack("d", item[18:26])[0]
        print(f"object transform: ", x, y, r)
        return x, y, r

    def get_level_data(self):
        data = bytes(self._header)
        for i in self.items:
            data += bytes(i)
        return data


class LevelPack:
    levels = []

    def __init__(self, filename):
        self.levels = []
        with open(filename, "rb") as f:
            """header structure provided by @Rollin'Barrel, my beloved"""
            self._b_format = f.read(2)
            self._format = int.from_bytes(self._b_format)

            self._b_id = f.read(8)
            self._id = int.from_bytes(self._b_id)

            self._b_name_len = f.read(1)
            self._name_len = int.from_bytes(self._b_name_len)
            self._b_name = f.read(self._name_len)
            self._name = self._b_name.decode("utf-8")

            self._b_creator_len = f.read(1)
            self._creator_len = int.from_bytes(self._b_creator_len)
            self._b_creator = f.read(self._creator_len)
            self._creator = self._b_creator.decode("utf-8")

            self._b_level_count = f.read(2)
            self._level_count = int.from_bytes(self._b_level_count, "little")

            print(f'Opened levelpack "{self._name}" from {self._creator}')

            data = f.read()
            print(f"zipped contain {len(data)}b")
            self._level_data = zlib.decompress(data)

            pointer = 0
            print(f"Looking for {self._level_count} levels")
            for i in range(self._level_count):
                self.levels.append(Level(pointer, self._level_data))
                pointer += self.levels[-1].size

    def __str__(self):
        new_data = f'Levelpack "{self._name}" from {self._creator}\n'
        _data = self._level_data
        for i, ch in enumerate(_data):
            c = str(hex(ch))
            c += (6 - len(c)) * " "
            new_data += c
            if not i % 16:
                new_data += "\n"
        new_data += f"\n{i} bytes of level data found"
        return new_data

    def print_raw_data(self, _from, _to):
        print(*[i for i in self._level_data[_from:_to]], sep=", ")

    def raw_data(self, _from, _to):
        return self._level_data[_from:_to]

    def find_diff(self, other):
        """find all different bytes in data"""

        print("Looking for diffs:")
        for i in range(max(len(self._level_data), len(other._level_data))):
            ch1 = self._level_data[i] if i < len(self._level_data) else "_"
            ch2 = other._level_data[i] if i < len(other._level_data) else "_"
            if ch1 != ch2:
                print(f"diff in {i}: {ch1} -> {ch2}")
        print("done")

    def change_byte(self, val, addr):
        self._level_data = self._level_data[:addr] + bytes(val) + self._level_data[addr + 1:]

    def append_bytes(self, data, addr):
        self._level_data = self._level_data[:addr] + data + self._level_data[addr:]

    def inject_bytes(self, data, addr):
        self._level_data = self._level_data[:addr] + data + self._level_data[addr + len(data):]

    def save(self, filename):
        with open(filename, "wb", ) as f:
            f.write(self._b_format)
            f.write(self._b_id)
            f.write(self._b_name_len)
            f.write(self._b_name)
            f.write(self._b_creator_len)
            f.write(self._b_creator)
            f.write(self._b_level_count)

            self._level_data = bytes()
            for i in self.levels:
                self._level_data += i.get_level_data()

            f.write(zlib.compress(self._level_data, level=-1))

            print(f'Saved levelpack "{self._name}" from {self._creator} as "{filename}"')
