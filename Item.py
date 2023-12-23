from Transform import Transform
from BinHelpers import explain_bin
import struct
import json


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
    def from_byte(array, return_size=True):
        """Creates Item object from byte form"""
        size = 26
        item = Item()
        item.item_id = int.from_bytes(array[0:2], "little")

        if item.item_id == 0:
            size += 9
            item.transform = Transform.create_from_byte(array[11:])
            item.joint = (0, 0.0)
            return item, size

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

        if item.item_id == Item.item_names["rail"] or item.item_id == Item.item_names["frog"]:
            item.expanded_info.append(struct.unpack("f", array[size:size + 4])[0])
            size += 4

        if item.item_id in Item.one_b:
            size += 1
            item.expanded_info.append(array[size - 1])

        # print(f"Init item with: {explain_bin(array[:size])}")
        if return_size:
            return item, size
        return item

    def to_json(self):
        j = json.dumps({'Item': {'id': self.item_id,
                                 "transform": {"x": self.transform.position[0], "y": self.transform.position[1],
                                               "r": self.transform.rotation},
                                 "joint": self.joint,
                                 "expanded_info": self.expanded_info}})
        return j

    @staticmethod
    def from_json(j):
        json.loads(j)
        item = json.loads(j).get("Item", None)
        if item is None:
            raise json.JSONDecodeError(j, "Error while parsing, no Item found", 0)
        item_id = item.get("id", 0)
        t = item.get("transform", Transform(0, 0, 0))
        transform = Transform(t.get("x", 0), t.get("y", 0), t.get("r", 0))
        joint = item.get("joint", [])
        expanded = item.get("expanded_info", [])
        return Item(item_id, transform, joint, expanded)

    def to_byte(self):
        """Converts object back to byte form"""
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
    # 34:frog have 4b more data?


item_ids = [range(0, 45)]
