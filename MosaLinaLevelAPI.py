import zlib
import random
import struct
import math
from os import walk

from LevelPack import LevelPack
from Level import Level
from Item import Item
from Transform import Transform
from Modify import ModifyLevel as ml


class LevelGenerator:
    @staticmethod
    def generate_random(soft=False):
        """Find all tagged packs in level packs and use them to substitute"""
        mypath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\"
        output = mypath + "ARandomPack\\data.mld"

        folders = next(walk(mypath), (None, None, []))[1]  # [] if no file
        islands = [LevelPack.read(mypath + f + "\\data.mld") for f in folders if
                   "gen" in f and "platform" in f]  # use frogs on layout frog==34
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

        dump = []
        size = 1000
        pack = LevelPack(size, name="RandomLevels", autor="RandomGenerator")
        for i in range(size):

            print(f"GENERATING LEVEL {i}")
            dump.append([])

            pack.levels[i] = random.choice(random.choice(layouts).levels).__copy__()
            pack.levels[i].color = (random.randint(10, 200), random.randint(10, 200), random.randint(10, 200))
            #pack.levels[i].color = (random.choice([0, 105, 255]), random.choice([0, 105, 255]), random.choice([0, 105, 255]))
            pack.levels[i].fruit = random.randint(0, 2)
            dump[i].append(pack.levels[i].__copy__())
            print("generating paths")
            ml.substitute(pack.levels[i], 36, paths, soft=soft)
            dump[i].append(pack.levels[i].__copy__())
            print("generating islands")
            ml.substitute(pack.levels[i], 34, islands, soft=soft)
            dump[i].append(pack.levels[i].__copy__())
            print("generating enemy")
            ml.substitute(pack.levels[i], 38, enemy, probability=0.3, soft=soft)
            dump[i].append(pack.levels[i].__copy__())
            print("generating decor")
            ml.substitute(pack.levels[i], 36, decor, probability=0.3, soft=soft)
            dump[i].append(pack.levels[i].__copy__())

            ml.substitute(pack.levels[i], 42, decor, probability=0.5, soft=soft)
            dump[i].append(pack.levels[i].__copy__())

            to_delete = []
            to_append = []
            for item in pack.levels[i].items:
                if (item.item_id == 2 or item.item_id == 1) and (
                        (not 25 < item.transform.position[0] < 575) or not (25 < item.transform.position[1] < 300)):
                    to_delete.append(item)

            for item in to_delete:
                pack.levels[i].items.remove(item)

            ml.remove_item_near_spawn(pack.levels[i], 9, 50)

            for item in to_append:
                pack.levels[i].items.append(item)

            modifiers = [ml.modify_identical, ml.modify_deletion, ml.modify_gravity, ml.modify_boxes, ml.modify_balls]
            weights = [90, 1, 3, 3, 3]
            random.choices(modifiers, weights, k=1)[0](pack.levels[i])

            dump[i].append(pack.levels[i].__copy__())

        pack.save(output)
        return dump

    @staticmethod
    def generate_grid():
        """Find all tagged packs in level packs and use them to substitute"""
        mypath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\"
        output = mypath + "AGrid\\data.mld"

        size = 9
        pack = LevelPack(size, name="Grid", autor="RandomGenerator")

        for i in range(30):
            for j in range(20):
                pack.levels[0].items.append(Item(2, Transform(i * 25, j * 25, 0)))

        to_delete = []
        for item in pack.levels[0].items:
            if (item.item_id == 2 or item.item_id == 3) and (
                    (not 25 < item.transform.position[0] < 575) or not (25 < item.transform.position[1] < 325)):
                to_delete.append(item)

        for item in to_delete:
            pack.levels[0].items.remove(item)

        ml.remove_item_near_spawn(pack.levels[0], 2, 50)

        for i in range(1, 45):
            pack.levels[1].items.append(Item(i, Transform((i % 10) * 50 + 50, (i // 10) * 50 + 50, 0), (1, 0)))

        pack.save(output)
