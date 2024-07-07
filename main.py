import pygame as pg
from EPT import load_assets, Button
import json

assets = load_assets("assets")

class Kingdom:
    def __init__(self) -> None:
        self.people = []
        self.unemployed_people = []
        self.buildings = []
        self.homes = []
        self.resources = []

    def add_home(self, home):
        """This function will return -1 if the kingdom dosen't have the required values"""
        file = open(f"{home.name}.json", "r")
        data = json.load(file)["cost"]
        cost = load_items_from_json(data)
        for i, item in enumerate(self.resources):
            for value in cost:
                new_item = item - value
                if new_item != -1:
                    self.resources[i] = new_item
                    continue
                return -1
    def add_building(self, *args): ...

class Person:
    def __init__(self) -> None:
        self.home = None
        self.job = None

def load_items_from_json(data):
    items = []
    for value in data:
        name = value["name"]
        count = value["count"]
        items.append(Item(name, count))
    return items

class Item:
    def __init__(self, name, count) -> None:
        self.name = name
        self.count = count

    def __add__(self, other):
        """This function will return -1 if it cannot add the values"""
        if isinstance(other, int) or isinstance(other, float):
            return Item(self.name, self.count + other)
        if not isinstance(other, Item):
            return -1
        if self.name == other.name:
            return Item(self.name, self.count + other.count)
        return -1
    
    def __sub__(self, other):
        """This function will return -1 if it cannot subtract the values"""
        if isinstance(other, int) or isinstance(other, float):
            return Item(self.name, self.count - other)
        if not isinstance(other, Item):
            return -1
        if self.name == other.name:
            return Item(self.name, self.count - other.count)
        return -1
        

class Building(pg.Rect):
    def __init__(self, x, y, width, height, name, up_keep_cost=None):
        super().__init__(x, y, width, height)
        self.name = name
        self.maintanince = up_keep_cost

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
    buttons.append(Button((i*button_size*button_scale, window_height-button_size*button_scale), assets[asset], button_scale, asset))

def display():
    window.fill((255, 255, 255))
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