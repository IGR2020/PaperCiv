import pygame as pg
from EPT import load_assets, Button
import json
from os import listdir
from os.path import join


class Kingdom:
    def __init__(self) -> None:
        self.people = []
        self.unemployed_people = []
        self.buildings = []
        self.resources = []

    def add_building(self, name, x, y, width, height): 
        "this function will return -1 if the kingdon does not have the required resouces"
        for value in building_info[name]["cost"]:
            for i, item in enumerate(self.resources):
                new_item = item - value
                if not isinstance(new_item, int):
                    self.resources[i] = new_item
                    break
            else:
                return -1
            
        self.buildings.append(Building(x, y, width, height, name, building_info[name]["jobs"]))

    def display(self, window, x_offset=0, y_offset=0):
        for building in self.buildings:
            building.display(window, x_offset, y_offset)

    def tick(self):
        for person in self.people:
            person.job.work(self.resources)
        for i, item in enumerate(self.resources):
            if item.name == "person":
                self.unemployed_people.append(Person())
                self.resources.pop(i)
        
    def employ_all_people(self):
        for i in range(len(self.unemployed_people)):
            for building in self.buildings:
                if building.jobs > 0:
                    self.people.append(Person(building))
                    self.unemployed_people.pop(i)
                    building.jobs -= 1
                    break
class Person:
    def __init__(self, job=None) -> None:
        self.job = job


class Item:
    def __init__(self, name, count, tag=None) -> None:
        self.name = name
        self.count = count
        self.tag = tag

    def __add__(self, other):
        """This function will return -1 if it cannot add the values"""
        if isinstance(other, int) or isinstance(other, float):
            return Item(self.name, self.count + other)
        if not isinstance(other, Item):
            return -1
        if self.name == other.name or (self.tag == other.tag and self.tag is not None):
            return Item(self.name, self.count + other.count)
        return -1

    def __sub__(self, other):
        """This function will return -1 if it cannot subtract the values"""
        if isinstance(other, int) or isinstance(other, float):
            return Item(self.name, self.count - other)
        if not isinstance(other, Item):
            return -1
        if self.name == other.name or (self.tag == other.tag and self.tag is not None):
            return Item(self.name, self.count - other.count)
        return -1

    def __repr__(self) -> str:
        return "{'name': " + str(self.name) + ", 'count': " + str(self.count) + "}"


class Building(pg.Rect):
    def __init__(self, x, y, width, height, name, jobs, up_keep_cost=None):
        super().__init__(x, y, width, height)
        self.name = name
        self.maintanince = up_keep_cost
        self.jobs = jobs

    def display(self, window, x_offset, y_offset):
        window.blit(assets[self.name], (self.x - x_offset, self.y - y_offset))

    def work(self, resources):
        "this function will return -1 if there are insufficent resoureces"
        for item in building_info[self.name]["in"]:
            for value in resources:
                new_item = value - item
                if not isinstance(new_item, int):
                    value = new_item
                    break
                return -1


def load_building_info(path):
    # loading the directory
    data = {}
    for file in listdir(path):
        with open(join(path, file)) as json_file:
            data[file.replace(".json", "")] = json.load(json_file)
            json_file.close()

    # extracting all data
    loaded_data = {}
    for build in data:
        building_data = data[build]
        cost = building_data["cost"]
        in_items = building_data["in"]
        out_items = building_data["out"]
        cost_items_loaded = []
        in_items_loaded = []
        out_items_loaded = []
        for value in cost:
            cost_items_loaded.append(Item(value["item"], value["count"]))
        for value in in_items:
            in_items_loaded.append(Item(value["item"], value["count"]))
        for value in out_items:
            out_items_loaded.append(Item(value["item"], value["count"]))
        jobs = building_data["jobs"]
        loaded_data[build] = {
            "cost": cost_items_loaded,
            "in": in_items_loaded,
            "out": out_items_loaded,
            "jobs": jobs
        }
    return loaded_data


assets = load_assets("assets")
building_info = load_building_info("building info")

window_width, window_height = 900, 500
window = pg.display.set_mode((window_width, window_height))
pg.display.set_caption("PaperCiv")

run = True
fps = 60
clock = pg.time.Clock()

button_size = 25
button_scale = 4

buttons = []
for i, asset in enumerate(assets):
    buttons.append(
        Button(
            (
                i * button_size * button_scale,
                window_height - button_size * button_scale,
            ),
            assets[asset],
            button_scale,
            asset,
        )
    )

main_kingdom = Kingdom()
main_kingdom.resources = [Item("wheat", 10, "food"), Item("water", 70), Item("wood", 50), Item("person", 1)]
main_kingdom.add_building("House2", 0, 0, 100, 100)
main_kingdom.tick()
main_kingdom.employ_all_people()
main_kingdom.tick()
print(len(main_kingdom.people))
print(main_kingdom.resources)

def display():
    window.fill((255, 255, 255))
    main_kingdom.display(window)
    for button in buttons:
        button.display(window)
    pg.display.update()


while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
    display()
pg.quit()
quit()
