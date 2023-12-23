from Level import Level
from BinHelpers import explain_bin
import zlib


class LevelPack:
    """
    Stores packs with meta for editor, author and steam
    """
    levels = None
    workshop_id = 0
    name = "unknown"
    author = "unknown"
    format = 9                  # this script is based on the 9th version of editor

    def __init__(self, size=9, name="unknown", autor="unknown"):
        self.levels = []
        for i in range(size):
            self.levels.append(Level())
        self.name = name
        self.autor = autor

    @staticmethod
    def read(filepath, overflow=False):
        """Generates Level Pack for a file"""
        pack = LevelPack(0)

        pack.levels = []
        with open(filepath, "rb") as f:
            pack.format = int.from_bytes(f.read(2), "little")
            pack.workshop_id = int.from_bytes(f.read(8), "little")
            pack.name = f.read(int.from_bytes(f.read(1))).decode("utf-8")
            pack.author = f.read(int.from_bytes(f.read(1))).decode("utf-8")
            pack.level_count = int.from_bytes(f.read(2), "little")

            print(f'Opened level pack "{pack.name}" from {pack.author}. Expected level count: {pack.level_count}')

            levels_raw = f.read()
            pack.data = zlib.decompress(levels_raw)

            data = pack.data
            ind = 0
            while len(data):
                if ind >= 9 and not overflow:
                    break

                print(f"INIT LEVEL {ind}")
                ind += 1
                new_level, size = Level.from_byte(data, return_size=True)
                data = data[size:]
                pack.levels.append(new_level)

            return pack

    @staticmethod
    def read_header(filepath):
        """Reads a header of the file (for the debug purposes)"""
        with open(filepath, "rb") as f:
            level_format = int.from_bytes(f.read(2), "little")
            workshop_id = int.from_bytes(f.read(8), "little")
            name = f.read(int.from_bytes(f.read(1))).decode("utf-8")
            author = f.read(int.from_bytes(f.read(1))).decode("utf-8")
            level_count = int.from_bytes(f.read(2), "little")
            print(level_format, workshop_id, name, author, level_count)

            levels_raw = f.read()
            data = zlib.decompress(levels_raw)
            print(explain_bin(data))

    def save(self, filepath, name=None):
        """
        Saves Level Pack as file
        :param filepath:
        :param name: replaces name of the pack if given
        :return:
        """
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

            level_data = bytes()
            for i in self.levels:
                level_data += i.to_byte()

            print(f"Saved pack {self.name} as {name} at {filepath}")

            f.write(zlib.compress(level_data, level=-1))
