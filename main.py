import zlib
import random
import struct
import os
from LevelPack import LevelPack, Level
from MosaLinaLevelAPI import LevelPack, Level, Item, Transform, LevelGenerator

from os import listdir
from os.path import isfile, join
from os import walk




#l = LevelPack.read("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\gen%20platforms%20fruit\\data.mld")
#for item in l.levels[1].items:
#    print(item.item_id, item.transform.position)

L = LevelGenerator.generate_grid()
L2 = LevelGenerator.generate_random()


while True:
    n = int(input())

    SIZE = 9
    output = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\AGeneration\\data.mld"
    l = LevelPack(SIZE, name=f"Generation of {n}", autor="RandomGenerator")

    l.levels[0] = L2[n][0]
    l.levels[1] = L2[n][1]
    l.levels[2] = L2[n][2]
    l.levels[3] = L2[n][3]
    l.levels[4] = L2[n][4]

    l.save(output)


#l2 = LevelPack(9, name="Hi", autor="Hello")
#l2.save("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\RandomPack\\data.mld")
#l3 = LevelPack.read("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\RandomPack2\\data.mld")

#LevelPack.reload("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test\\data.mld")
#l = LevelPack.read("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test\\data.mld")

'''
l = LevelPack(9, name="Hi", autor="Hello")
for i in range(1, 46):
    print(i)
    l.levels[0].items.append(Item(i, Transform((i % 10)*50 + 50, 100 + 50 * (i//10), 0), joint=(1, 0)))
l.save("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test2\\data.mld")
'''
"""
l1 = LevelPack.read("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\gen%20platforms%20fruit\\data.mld")
l1.levels = l1.levels[:9]
l1.save("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\gen%20platforms%20fruit\\data.mld")
"""
#LevelPack.reload("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test\\data.mld")


"""
l = LevelPack.read(
    "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test\\data.mld")
l.save("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test2\\data.mld")
"""


'''
for i in range(1, 46):
    print(i)
    l.levels[0].items.append(Item(i, Transform((i % 10)*50 + 50, 100 + 50 * (i//10), 0), joint=(1, 0)))
'''

'''
l1 = LevelPack.read("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test2\\data.mld")

LevelPack.read_header("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test\\data.mld")
LevelPack.read_header("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\test2\\data.mld")
'''
'''



mypath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\"
output = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mosa Lina\\userdata\\levelpacks\\RandomPack\\data.mld"

folders = next(walk(mypath), (None, None, []))[1]  # [] if no file
islands = [LevelPack(mypath+f+"\\data.mld") for f in folders if "gen" in f and "island" in f] #gonna use frogs on layout idk :D frog==34
print(islands)
layouts = [LevelPack(mypath+f+"\\data.mld") for f in folders if "gen" in f and "layout" in f]
print(layouts)
paths = [LevelPack(mypath+f+"\\data.mld") for f in folders if "gen" in f and "paths" in f] #arrows on layout arrows==26
print(paths)
enemy = [LevelPack(mypath+f+"\\data.mld") for f in folders if "gen" in f and "enemy" in f] #frogs on islands and paths?
print(enemy)
decor = [LevelPack(mypath+f+"\\data.mld") for f in folders if "gen" in f and "decor" in f] #arrows on islands and paths?
print(decor)

SIZE = 1000

print("===============================")
l = LevelPack(output)
print("===============================")
print(l._b_level_count)
l._b_level_count = struct.pack("h", SIZE)
print(l._b_level_count)
for i in range(SIZE):
    if len(l.levels) <= i:
        l.levels.append(None)
    l.levels[i] = random.choice(random.choice(layouts).levels).__copy__()
    l.levels[i].substitute(36, paths)
    l.levels[i].substitute(34, islands)
    l.levels[i].substitute(34, enemy, probability=0.9)
    l.levels[i].substitute(36, decor, probability=0.5)
l.save(output)

'''
'''

l1 = LevelPack("LevelBlocks\\start.mld")
l2 = LevelPack("LevelBlocks\\enemy.mld")

for i in range(9):
    l1.levels[i].substitute(36, l2)


print(l1.levels[0])
print(len(l2.levels), "врагов")

l1.save("LevelBlocks\\data.mld")

l3 = LevelPack(output)
'''
