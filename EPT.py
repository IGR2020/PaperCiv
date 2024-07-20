import pygame
from os import listdir
from os.path import join, isfile, isdir

pygame.font.init()


def blit_text(win, text, pos, colour=(0, 0, 0), size=30, font="arialblack", blit=True):
    text = str(text)
    font_style = pygame.font.SysFont(font, size)
    text_surface = font_style.render(text, True, colour)
    if blit:
        win.blit(text_surface, pos)
    return text_surface


class Button(pygame.Rect):
    def __init__(self, pos, image, scale=1, *args):
        x, y = pos
        width, height = image.get_width() * scale, image.get_height() * scale
        super().__init__(x, y, width, height)
        self.image = pygame.transform.scale(image, (width, height))
        if len(args) == 1:
            self.info = args[0]
        else:
            self.info = args

    def clicked(self):
        pos = pygame.mouse.get_pos()
        if self.collidepoint(pos):
            return True
        return False

    def display(self, win, background=None):
        """
        background can be any RGB value
        """
        if background is not None:
            pygame.draw.rect(win, background, self)
        win.blit(self.image, self)


def load_assets(path, size: int = None, scale: float = None, getSubDirsAsList=False):
    sprites = {}
    for file in listdir(path):
        if getSubDirsAsList and isdir(join(path, file)):
            sprites[file.replace(".png", "")] = load_assets_list(
                join(path, file), size, scale
            )
            continue
        elif not isfile(join(path, file)):
            continue
        if size is None and scale is None:
            sprites[file.replace(".png", "")] = pygame.image.load(join(path, file))
        elif scale is not None:
            sprites[file.replace(".png", "")] = pygame.transform.scale_by(
                pygame.image.load(join(path, file)), scale
            )
        else:
            sprites[file.replace(".png", "")] = pygame.transform.scale(
                pygame.image.load(join(path, file)), size
            )
    return sprites


def load_assets_list(path, size: int = None, scale: float = None):
    sprites = []
    for file in listdir(path):
        if not isfile(join(path, file)):
            continue
        if size is None and scale is None:
            sprites.append(pygame.image.load(join(path, file)))
        elif scale is not None:
            sprites.append(
                pygame.transform.scale_by(pygame.image.load(join(path, file)), scale)
            )
        else:
            sprites.append(
                pygame.transform.scale(pygame.image.load(join(path, file)), size)
            )
    return sprites


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(
    path, width, height, direction=True, resize=None, autocrop=False
):
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []

        for i in range(sprite_sheet.get_width() // width):
            for j in range(sprite_sheet.get_height() // height):
                surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                rect = pygame.Rect(i * width, j * height, width, height)
                surface.blit(sprite_sheet, (0, 0), rect)
                sprites.append(pygame.transform.scale2x(surface))

        if resize is not None:
            sprites = [pygame.transform.scale(surface, resize) for surface in sprites]

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites
