import random
from Item import Item
from Transform import Transform


class ModifyLevel:
    @staticmethod
    def substitute(self, _id, level_packs, probability=2.0, up_limit=-1, soft=False):
        to_del = []
        to_add = []

        sub_items = [i for i in self.items if i.item_id == _id]

        if up_limit != -1:
            sub_items_use = random.choices(sub_items, k=min(up_limit, len(sub_items)))
        else:
            sub_items_use = sub_items

        for ind, i in enumerate(sub_items):
            to_del.append(i)
            if i not in sub_items_use:
                continue

            if soft:
                scene = level_packs[0].levels[0]
            else:
                scene = random.choice(random.choice(level_packs).levels)
            root = i.transform

            if abs(root.position[0]) + abs(root.position[1]) > 1000000:
                continue
            if random.random() > probability:
                continue

            part = []
            breaks = 0
            for item in scene.items:
                itm = item.__copy__()
                if abs(itm.transform.position[0]) + abs(itm.transform.position[1]) > 1000000:
                    breaks = True

                if itm.item_id == 0:
                    continue
                itm.transform = itm.transform.localize_object_transform(scene.portal_transform, root)

                if abs(itm.transform.position[0]) + abs(itm.transform.position[1]) > 1000000:
                    breaks += 1
                else:
                    part.append(itm)

            if breaks < 4:
                to_add.extend(part)

        for i in to_del:
            if i in self.items:
                self.items.remove(i)

        for i in to_add:
            if len(self.items) < 50:
                self.items.append(i)

    @staticmethod
    def modify_boxes(self, amount=50):
        for i in range(amount):
            self.items.append(Item(41, Transform(random.random() * 600, random.random() * 100, 0)))

    @staticmethod
    def modify_balls(self, amount=50):
        for i in range(amount):
            self.items.append(Item(43, Transform(random.random() * 600, 350 - random.random() * 100, 0)))

    @staticmethod
    def modify_gravity(self, percentage=0.5):
        for i in self.items:
            if i.joint is not None:
                if self.portal_transform.distance(i.transform) > 100:
                    if random.random() <= percentage:
                        i.joint = (0, 0)

        for i in range(30):
            self.items.append(Item(9, Transform(i * 25, 310, 0), (2, 0)))

    @staticmethod
    def modify_deletion(self, percentage=0.2):
        to_delete = []
        to_append = []

        for i in self.items:
            if i.item_id > 10:
                if self.portal_transform.distance(i.transform) > 100:
                    if random.random() <= percentage:
                        to_delete.append(i)
                        to_append.append(Item(44, i.transform, (1, 0)))

        for item in to_delete:
            self.items.remove(item)

        for item in to_append:
            self.items.append(item)

        self.color = (0, 0, 0)

    @staticmethod
    def modify_identical(self, data=None):
        pass

    @staticmethod
    def remove_item_near_spawn(self, item_id, distance):
        to_delete = []
        for item in self.items:
            if item.transform.distance(self.portal_transform) < distance and item.item_id == item_id:
                to_delete.append(item)

        for item in to_delete:
            self.items.remove(item)