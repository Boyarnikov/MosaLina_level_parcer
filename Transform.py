import struct
import math


class Transform:
    position = [0, 0]
    rotation = 0

    def __init__(self, x, y, r):
        self.position = [x, y]
        self.rotation = r

    def distance(self, other):
        return math.hypot(self.position[0] - other.position[0], self.position[1] - other.position[1])

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

        new_transform.position[0], new_transform.position[1] = new_transform.position[0] * math.cos(alpha) - \
                                                               new_transform.position[1] * math.sin(alpha), \
                                                               new_transform.position[0] * math.sin(alpha) + \
                                                               new_transform.position[1] * math.cos(alpha)

        new_transform.rotation += alpha

        new_transform.position[0] += new_root.position[0]
        new_transform.position[1] += new_root.position[1]
        return new_transform
