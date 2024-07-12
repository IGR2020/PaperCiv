import pygame as pg
from EPT import load_assets, Button, blit_text
import json
from os import listdir
from os.path import join
from math import ceil


class Kingdom:
    def __init__(self) -> None:
        self.people = []
        self.unemployed_people = []
        self.buildings = []
        self.resources = []

    def add_building(self, name, x, y):
        "this function will return -1 if the kingdon does not have the required resouces"
        for value in building_info[name]["cost"]:
            for i, item in enumerate(self.resources):
                new_item = item - value
                if not isinstance(new_item, int):
                    self.resources[i] = new_item
                    break
            else:
                return -1

        self.buildings.append(
            Building(x, y, name, building_info[name]["jobs"])
        )

    def display(self, window, x_offset=0, y_offset=0):
        for building in self.buildings:
            building.display(window, x_offset, y_offset)

        # items
        for i, item in enumerate(self.resources):
            blit_text(
                window,
                item.name + "   " + str(item.count),
                (0, i * text_size + text_size * 0.2 * i - 5),
                size=text_size,
            ).get_width()
            try:
                window.blit(
                    assets[item.name],
                    (resource_div_rect_x-default_item_size*2, i * text_size + text_size * 0.2 * i),
                )
            except KeyError:
                window.blit(
                    assets["Missing Item"],
                    (resource_div_rect_x-default_item_size*2, i * text_size + text_size * 0.2 * i),
                )

    def tick(self):
        for person in self.people:
            remaining_resources = person.job.work(self.resources)
            if not isinstance(remaining_resources, int):
                self.resources = remaining_resources
        for i, item in enumerate(self.resources):
            if item.name == "person":
                for j in range(item.count):
                    self.unemployed_people.append(Person())
                self.resources.pop(i)

    def employ_all_people(self):
        for i, person in enumerate(self.unemployed_people):
            for building in self.buildings:
                if building.jobs > 0:
                    self.unemployed_people.pop(i)
                    self.people.append(Person(building))
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
            return Item(self.name, self.count + other, self.tag)
        if not isinstance(other, Item):
            return -1
        if self.name == other.name or (
            (self.tag == other.tag or self.tag == other.name or self.name == other.tag)
            and self.tag is not None
        ):
            return Item(self.name, self.count + other.count, self.tag)
        return -1

    def __sub__(self, other):
        """This function will return -1 if it cannot subtract the values"""
        if (
            isinstance(other, int) or isinstance(other, float)
        ) and self.count > other.count:
            return Item(self.name, self.count - other, self.tag)
        if not isinstance(other, Item):
            return -1
        if (
            self.name == other.name
            or (
                (
                    self.tag == other.tag
                    or self.tag == other.name
                    or self.name == other.tag
                )
                and self.tag is not None
            )
        ) and self.count > other.count:
            return Item(self.name, self.count - other.count, self.tag)
        return -1

    def __repr__(self) -> str:
        return "{name: " + str(self.name) + ", count: " + str(self.count) + ",  tag: " + str(self.tag) + "}"


class Building(pg.Rect):
    def __init__(self, x, y, name, jobs, up_keep_cost=None):
        width, height = assets[name].get_size()
        super().__init__(x, y, width, height)
        self.name = name
        self.maintanince = up_keep_cost
        self.jobs = jobs
        self.manual = True

    def display(self, window, x_offset, y_offset):
        window.blit(assets[self.name], (self.x - x_offset, self.y - y_offset))

    def work(self, resources, called_as_click=False):
        "this function will return -1 if there are insufficent resoureces"
        if self.manual and not called_as_click:
            return -1
        
        for item in building_info[self.name]["in"]:
            for i, value in enumerate(resources):
                new_item = value - item
                if not isinstance(new_item, int):
                    resources[i] = new_item
                    break
            else:
                return -1
        for item in building_info[self.name]["out"]:
            for i, value in enumerate(resources):
                new_item = value + item
                if not isinstance(new_item, int):
                    resources[i] = new_item
                    break
            else:
                resources.append(item)
        return resources


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
            try:
                cost_items_loaded[-1].tag = value["tag"]
            except KeyError:
                continue
        for value in in_items:
            in_items_loaded.append(Item(value["item"], value["count"]))
            try:
                in_items_loaded[-1].tag = value["tag"]
            except KeyError:
                continue
        for value in out_items:
            out_items_loaded.append(Item(value["item"], value["count"]))
            try:
                out_items_loaded[-1].tag = value["tag"]
            except KeyError:
                continue
        jobs = building_data["jobs"]
        loaded_data[build] = {
            "cost": cost_items_loaded,
            "in": in_items_loaded,
            "out": out_items_loaded,
            "jobs": jobs,
        }
    return loaded_data


assets = load_assets("assets/building buttons")
building_info = load_building_info("building info")

window_width, window_height = 1920 * 0.7, 1080 * 0.7
window = pg.display.set_mode((window_width, window_height), pg.RESIZABLE)
pg.display.set_caption("PaperCiv")

run = True
fps = 60
clock = pg.time.Clock()

text_size = 30
default_item_size = 32

button_size = 48
button_scale = 1

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
div_rect = pg.Rect(
    0, window_height - button_size * button_scale, window_width, 5
)  # decorational only
resource_div_rect = pg.Rect(300, 0, 5, window_height-button_size*button_scale)  # decorational only
resource_div_rect_x = resource_div_rect.x

# loading non-building assets
assets.update(load_assets("assets/buildings"))
assets.update(load_assets("assets/buttons"))
assets.update(
    load_assets("assets/items", None, ceil(text_size / default_item_size * 2))
)

play_button_size = 48
play_button = Button((window_width - play_button_size, 0), assets["Play"])


main_kingdom = Kingdom()
main_kingdom.resources = [
    Item("wheat", 100, "food"),
    Item("water", 100),
    Item("wood", 50),
    Item("person", 1),
]

is_configuring = False
configuring_pos = None
building_configered = None
# configure buttons
manual_config = Button((0, 0), assets["Off"], 1)
add_people_config = Button((0, 0), assets["Plus"])
minus_people_config = Button((0, 0), assets["Minus"])
people_text_pos = 70, 60
people_employed_stat = 0


def display():
    window.fill((255, 255, 255))
    main_kingdom.display(window)

    # buttons
    for button in buttons:
        button.display(window)
    play_button.display(window)
    pg.draw.rect(window, (0, 0, 0), div_rect)
    pg.draw.rect(window, (0, 0, 0), resource_div_rect)

    # draging buildings for adding
    if selected_button is not None:
        window.blit(assets[buttons[selected_button].info], pg.mouse.get_pos())

    # building configuration
    if is_configuring:
        window.blit(assets["Building Configure"], configuring_pos)
        manual_config.display(window)
        add_people_config.display(window)
        minus_people_config.display(window)
        blit_text(window, people_employed_stat, people_text_pos)
    pg.display.update()


selected_button = None

while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if is_configuring:
                if manual_config.clicked():
                    main_kingdom.buildings[building_configered].manual = not main_kingdom.buildings[building_configered].manual
                    if not main_kingdom.buildings[building_configered].manual:
                        manual_config.image = assets["On"]
                    else:
                        manual_config.image = assets["Off"]
                elif add_people_config.clicked():
                    try:
                        main_kingdom.unemployed_people.pop(0)
                        main_kingdom.people.append(Person(main_kingdom.buildings[building_configered]))
                        people_employed_stat += 1
                    except IndexError:
                        pass
                elif minus_people_config.clicked():
                    for i, person in enumerate(main_kingdom.people):
                        if id(person.job) == id(main_kingdom.buildings[building_configered]):
                            main_kingdom.people.pop(i)
                            main_kingdom.unemployed_people.append(Person())
                            people_employed_stat -= 1
                            break
                else:
                    is_configuring = False

            for i, button in enumerate(buttons):
                if button.clicked():
                    selected_button = i
                    break
            else:
                if play_button.clicked():
                    main_kingdom.tick()
                    main_kingdom.employ_all_people()
                    continue
                x, y = pg.mouse.get_pos()
                for i, building in enumerate(main_kingdom.buildings):
                    if building.collidepoint((x, y)):
                        if event.button == 1:
                            remaining_resources = building.work(main_kingdom.resources, True)
                            if not isinstance(remaining_resources, int):
                                main_kingdom.resources = remaining_resources
                        if event.button == 3:
                            people_employed_stat = 0
                            configuring_pos = x, y
                            is_configuring = True
                            building_configered = i
                            if not main_kingdom.buildings[building_configered].manual:
                                manual_config.image = assets["On"]
                            else:
                                manual_config.image = assets["Off"]
                            manual_config.topleft = x + 120, y + 4
                            add_people_config.topleft = x + 4, y + 60
                            minus_people_config.topleft = x + 140, y + 60
                            people_text_pos = x + 70, y + 60
                            for person in main_kingdom.people:
                                if id(person.job) == id(main_kingdom.buildings[building_configered]):
                                    people_employed_stat += 1


        if event.type == pg.MOUSEBUTTONUP:
            if selected_button is None:
                continue
            x, y = pg.mouse.get_pos()
            main_kingdom.add_building(buttons[selected_button].info, x, y)
            selected_button = None
    display()
pg.quit()
quit()
