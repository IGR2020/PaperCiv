import pygame as pg
from EPT import load_assets, Button, blit_text
import json
from os import listdir
from os.path import join, isfile
from math import ceil
from time import time
import pickle


class Kingdom:
    def __init__(self, total_water=100_000, water_add=667) -> None:
        self.people = []
        self.unemployed_people = []
        self.buildings = []
        self.resources = []
        self.total_water = total_water
        self.water_added = water_add

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
        width, height = assets[name].get_size()
        self.buildings.append(
            Building(x, y, width, height, name, building_info[name]["jobs"])
        )

    def display(self, window, x_offset=0, y_offset=0, resource_display_y_offset=0):
        for building in self.buildings:
            building.display(window, x_offset, y_offset)

        # items
        for i, item in enumerate(self.resources):
            blit_text(
                window,
                item.name + "   " + str(item.count),
                (
                    0,
                    i * text_size + text_size * 0.2 * i - 5 + resource_display_y_offset,
                ),
                size=text_size,
            ).get_width()
            try:
                window.blit(
                    assets[item.name],
                    (
                        resource_div_rect.x - default_item_size * 2,
                        i * text_size + text_size * 0.2 * i + resource_display_y_offset,
                    ),
                )
            except KeyError:
                window.blit(
                    assets["Missing Item"],
                    (
                        resource_div_rect.x - default_item_size * 2,
                        i * text_size + text_size * 0.2 * i + resource_display_y_offset,
                    ),
                )

    def tick(self):
        self.total_water += self.water_added
        for person in self.people:
            remaining_resources = person.job.work(self.resources)
            if not isinstance(remaining_resources, int):
                for i, item in enumerate(remaining_resources):
                    if item.name == "water" and self.total_water < item.count:
                        remaining_resources.pop(i)
                        break
                    if item.name == "water":
                        self.total_water -= item.count
                        break
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
        return (
            "{name: "
            + str(self.name)
            + ", count: "
            + str(self.count)
            + ",  tag: "
            + str(self.tag)
            + "}"
        )


class Building:
    def __init__(self, x, y, width, height, name, jobs):
        self.rect = pg.Rect(x, y, width, height)
        self.name = name
        self.jobs = jobs
        self.manual = True
        self.has_ticked = False

    def display(self, window, x_offset, y_offset):
        if self.rect.x - x_offset < resource_div_rect.x:
            return
        if self.rect.bottom - y_offset > div_rect.y:
            return
        window.blit(assets[self.name], (self.rect.x - x_offset, self.rect.y - y_offset))

    def work(self, resources, called_as_click=False):
        "this function will return -1 if there are insufficent resoureces"
        if not called_as_click:
            self.has_ticked = False
        if self.has_ticked:
            return -1
        if self.manual and not called_as_click:
            return -1

        # limiting ticking to once per tick
        self.has_ticked = True

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
button_scale = 2

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
    0, window_height - button_size * button_scale - 5, window_width, 5
)  # decorational only
resource_div_rect = pg.Rect(
    300, 0, 5, window_height - button_size * button_scale
)  # decorational only

# loading non-building assets
assets.update(load_assets("assets/buildings"))
assets.update(load_assets("assets/buttons"))
assets.update(
    load_assets("assets/items", None, ceil(text_size / default_item_size * 2))
)

play_button_size = 48
play_button = Button((window_width - play_button_size, 0), assets["Play"])

username = "main"
save_name = "main.pkl"

# loading world data / creating new world
if isfile(f"Civ Data/{save_name}"):
    file = open(f"Civ Data/{save_name}", "rb")
    kingdoms = pickle.load(file)
    file.close()
else:
    kingdoms = {username: Kingdom()}
main_kingdom = kingdoms[username]
main_kingdom.resources = [
    Item("Wheat", 100, "food"),
    Item("Water", 100),
    Item("Wood", 50),
    Item("person", 1),
]

is_configuring = False
configuring_pos = None
building_configered = None

# configure buttons
manual_config = Button((0, 0), assets["Off"], 1)
add_people_config = Button((0, 0), assets["Plus"])
minus_people_config = Button((0, 0), assets["Minus"])
work_config = Button((0, 0), assets["Work"])
people_text_pos = 70, 60
people_employed_stat = 0

# button scrolling
building_scroll_right = Button(
    (
        window_width - button_size * button_scale,
        window_height - button_size * button_scale,
    ),
    assets["Right"],
    button_scale,
)
building_scroll_left = Button(
    (0, window_height - button_size * button_scale), assets["Left"], button_scale
)

# resource menu scrolling
is_scrolling_resource_menu = False
resource_scrolling = 0

# building offset
building_x_offset = 0
building_y_offset = 0

# tick speed (in seconds) / tick settings
tick_speed = 10
last_tick_time = time()
is_paused = False
# displaying tick progress
tick_progress = 0
total_tick_rect_width = 100
tick_progress_rect = pg.Rect(resource_div_rect.right, 0, total_tick_rect_width, 25)
tick_progress_rect_outline = pg.Rect(
    resource_div_rect.right,
    0,
    total_tick_rect_width * 1.1,
    tick_progress_rect.height * 1.2,
)


def display():
    window.fill((255, 255, 255))
    main_kingdom.display(
        window, building_x_offset, building_y_offset, resource_scrolling
    )

    # buttons
    for button in buttons:
        button.display(window)
    play_button.display(window)
    building_scroll_left.display(window)
    building_scroll_right.display(window)
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
        work_config.display(window)

    # tick progress display
    pg.draw.rect(window, (0, 0, 0), tick_progress_rect_outline)
    pg.draw.rect(
        window, (255 * tick_progress, 255 - 255 * tick_progress, 0), tick_progress_rect
    )

    pg.display.update()


selected_button = None

while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:

            # saving civ data
            kingdoms[username] = main_kingdom
            file = open(f"Civ Data/{save_name}", "wb")
            pickle.dump(kingdoms, file)
            file.close()

            run = False

        if event.type == pg.MOUSEBUTTONDOWN:
            if is_configuring:
                if manual_config.clicked():
                    main_kingdom.buildings[building_configered].manual = (
                        not main_kingdom.buildings[building_configered].manual
                    )
                    if not main_kingdom.buildings[building_configered].manual:
                        manual_config.image = assets["On"]
                    else:
                        manual_config.image = assets["Off"]
                elif add_people_config.clicked():
                    if main_kingdom.buildings[building_configered].jobs < 1:
                        continue
                    try:
                        main_kingdom.unemployed_people.pop(0)
                        main_kingdom.people.append(
                            Person(main_kingdom.buildings[building_configered])
                        )
                        people_employed_stat += 1
                        main_kingdom.buildings[building_configered].jobs -= 1
                    except IndexError:
                        pass
                elif minus_people_config.clicked():
                    for i, person in enumerate(main_kingdom.people):
                        if id(person.job) == id(
                            main_kingdom.buildings[building_configered]
                        ):
                            main_kingdom.people.pop(i)
                            main_kingdom.unemployed_people.append(Person())
                            people_employed_stat -= 1
                            main_kingdom.buildings[building_configered].jobs += 1
                            break
                elif work_config.clicked():
                    remaining_resources = building.work(main_kingdom.resources, True)
                    if not isinstance(remaining_resources, int):
                        main_kingdom.resources = remaining_resources
                    work_config.image = assets["Work Pressed"]
                else:
                    is_configuring = False
                continue

            for i, button in enumerate(buttons):
                if button.clicked():
                    selected_button = i
                    break
            else:
                # getting the x, y positions
                x, y = pg.mouse.get_pos()
                # button clicking
                if play_button.clicked():
                    is_paused = not is_paused
                    if is_paused:
                        play_button.image = assets["Pause"]
                    else:
                        play_button.image = assets["Play"]
                    continue
                elif building_scroll_left.clicked():
                    for button in buttons:
                        button.x -= 1
                    continue
                elif building_scroll_right.clicked():
                    for button in buttons:
                        button.x += 1
                    continue
                elif x < resource_div_rect.x:
                    is_scrolling_resource_menu = True
                    continue
                # updating x, y in context to x / y offset
                x += building_x_offset
                y += building_y_offset
                # building clicking (work / config)
                for i, building in enumerate(main_kingdom.buildings):
                    if building.rect.collidepoint((x, y)):
                        # updating x, y to fit config menu in screen
                        x -= building_x_offset
                        y -= building_y_offset

                        people_employed_stat = 0
                        configuring_pos = x, y
                        is_configuring = True
                        building_configered = i
                        if not main_kingdom.buildings[building_configered].manual:
                            manual_config.image = assets["On"]
                        else:
                            manual_config.image = assets["Off"]
                        manual_config.topleft = x + 140, y + 4
                        add_people_config.topleft = x + 4, y + 60
                        minus_people_config.topleft = x + 140, y + 60
                        people_text_pos = x + 70, y + 60
                        for person in main_kingdom.people:
                            if id(person.job) == id(
                                main_kingdom.buildings[building_configered]
                            ):
                                people_employed_stat += 1
                        work_config.topleft = x, y + 120
                        break

        if event.type == pg.MOUSEBUTTONUP:
            is_scrolling_resource_menu = False
            work_config.image = assets["Work"]
            if selected_button is None:
                continue
            x, y = pg.mouse.get_pos()
            if x < resource_div_rect.x:
                selected_button = None
                continue
            if y > div_rect.y:
                selected_button = None
                continue
            main_kingdom.add_building(
                buttons[selected_button].info,
                x + building_x_offset,
                y + building_y_offset,
            )
            selected_button = None

    mouse_pressed_buttons = pg.mouse.get_pressed()
    rel_x, rel_y = pg.mouse.get_rel()
    if True in mouse_pressed_buttons:
        if is_scrolling_resource_menu:
            resource_scrolling += rel_y
            resource_scrolling = min(resource_scrolling, 0)
        elif building_scroll_left.clicked():
            for button in buttons:
                button.x -= 1
        elif building_scroll_right.clicked():
            for button in buttons:
                button.x += 1
        elif selected_button is None:
            building_x_offset -= rel_x
            building_y_offset -= rel_y

    # tick logic
    if not is_paused:
        time_since_last_tick = time() - last_tick_time
        tick_progress = time_since_last_tick / tick_speed
        tick_progress_rect.width = total_tick_rect_width * tick_progress
        if time_since_last_tick > tick_speed:
            main_kingdom.tick()
            main_kingdom.employ_all_people()
            last_tick_time = time()
    else:
        last_tick_time = time() - tick_speed * tick_progress

    display()
pg.quit()
quit()
