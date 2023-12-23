import zlib
import random
import struct


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


class Level:
    def __init__(self, filename):
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
            self._level_count = int.from_bytes(self._b_level_count)

            print(f'Opened levelpack "{self._name}" from {self._creator}')

            data = f.read()
            print(f"zipped contain {len(data)}b")
            self._level_data = zlib.decompress(data)

            level_data = beautify_binary(self._level_data)
            # print(level_data)

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
            f.write(zlib.compress(self._level_data, level=-1))

            print(f'Saved levelpack "{self._name}" from {self._creator} as "{filename}"')

    def get_scene(self, index):
        if index >= self._level_count:
            return None
        pointer = 0
        while index != 0:
            index -= 1
            offset = self._level_data[pointer + 5]
            item_count = self._level_data[pointer + 5 + offset + 1] - 1
            print(f"level:")
            self.print_raw_data(pointer, pointer + 34 + offset)
            pointer += 34 + offset
            print(f"items: {item_count}")

            for i in range(item_count):
                size = 35
                if self._level_data[pointer] in [1, 4, 5, 6]:
                    size -= 8
                self.print_raw_data(pointer, pointer + size)
                pointer += size
        return pointer


