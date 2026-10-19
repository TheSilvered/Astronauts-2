import json
import os

import pygame

import encrypter
import gameassets as ga
from constants import TILE_SIZE, PIXEL, PER_TILE_ERROR, \
                      LEVEL_OFFSET_RIGHT, LEVEL_OFFSET_LEFT, LOCAL_DIR
from assets_import import DOOR_FRAME, DOOR_FRAME_FLIPPED, DOOR_ANI_0, \
                          DOOR_ANI_1, DOOR_ANI_2, DOOR_ANI_3, DOOR_ANI_4


tiles = {}
tile_ids = []
levels = []
custom_levels_start = 0


def load_tiles():
    global tiles, tile_ids

    with open(os.path.join(LOCAL_DIR, "assets/textures/blocks/block_textures.json")) as f:
        paths = json.load(f)

    for path in paths:
        tiles.update(get_textures_image(os.path.join(LOCAL_DIR, path)))

    tile_ids = list(tiles)


def get_textures_image(path):
    img = pygame.image.load(path)
    img.convert_alpha()

    path = path.replace('.png', '.json')

    with open(path) as f:
        img_info = json.load(f)

    tile = ga.get_size(img) // img_info["res"]
    tile_t = []
    tile_hb = []

    tiles = {}

    for i in range(img_info["res"][0]):
        for j in range(img_info["res"][1]):
            rect = pygame.Rect(tile * (i, j), tile)
            tile_texture = img.subsurface(rect).copy()
            tile_texture = pygame.transform.scale(tile_texture, TILE_SIZE)
            tile_texture.set_colorkey(ga.BLACK)
            tile_t.append(tile_texture)
            if img_info["type"] == "solid":
                tile_hb.append([(0, 0, 16 * PIXEL, 16 * PIXEL)])
            elif img_info["type"] == "transparent":
                tile_hb.append([(0, 0, 0, 0)])
            elif img_info["type"] == "custom_solid":
                hb = img_info["hitboxes"][j + i*img_info["res"][1]]
                tile_hb.append([[i[j]*PIXEL for j in range(4)] for i in hb])
            else:
                raise TypeError(f"invalid block type ({img_info['type']}) in {path}")

    for id_, t, h in zip(range(*img_info["ids"]), tile_t, tile_hb):
        if img_info["has_alpha"]: t.convert_alpha()
        else: t.convert()
        tiles[id_] = {"t": t, "h": h, "k": img_info["kills"]}

    return tiles


load_tiles()


class OpenDoorAni(ga.TextureAni):
    def _finish_end(self) -> None:
        super()._finish_end()
        self.e.keep_open.start()
        self.e.opened = True


class CloseDoorAni(ga.TextureAni):
    def _finish_end(self) -> None:
        super()._finish_end()
        self.e.opened = False


class Door(ga.Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opened = False
        self.add_ani(
            OpenDoorAni(
                name="open",
                frames=[DOOR_ANI_0, DOOR_ANI_1, DOOR_ANI_2,
                        DOOR_ANI_3, DOOR_ANI_4],
                time=0.03,
                scale=False
            )
        )
        self.add_ani(
            CloseDoorAni(
                name="close",
                frames=[DOOR_ANI_4, DOOR_ANI_3, DOOR_ANI_2,
                        DOOR_ANI_1, DOOR_ANI_0],
                time=0.03,
                scale=False
            )
        )
        self.add_ani(
            ga.TextureAni(
                name="keep_open",
                frames=[DOOR_ANI_4],
                loop=True,
                scale=False
            )
        )
        self.open.scale_frames()
        self.close.scale_frames()
        self.keep_open.scale_frames()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos, level_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = tiles[tile_type]["t"]
        self.rect = pygame.Rect(pos, (0, 0))
        self.level_pos = ga.Pos(level_pos)
        self.id = tile_type


class HbTile(pygame.sprite.Sprite):
    def __init__(self, pos, level_pos, hitbox):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.rect = pygame.Rect(hitbox)
        self.rect.topleft = pos + self.rect.topleft
        self.level_pos = level_pos


class Level:
    def __init__(self, level_data, side, name=None):
        if side == "left":
            offset = LEVEL_OFFSET_LEFT
        else:
            offset = LEVEL_OFFSET_RIGHT

        self.flip_door = level_data[f"flip_door_{side}"]
        self.side = side
        self.layers = level_data[f"layers_{side}"]
        self.offset = offset
        self.solid = []
        self.damaging = []
        self.layered_groups = []
        self.gen_tiles()
        self.texture = None
        self.frame_pos = TILE_SIZE * level_data[f"door_pos_{side}"]
        self.gen_texture()

        if level_data[f"flip_door_{side}"]:
            door_pos = self.frame_pos + TILE_SIZE * (1, 0) + offset
        else:
            door_pos = self.frame_pos + TILE_SIZE * (1, 1) + offset

        self.door = Door(
            pos=door_pos,
            size=TILE_SIZE * 2,
            texture=DOOR_ANI_0
        )

        self.door.open.scale_frames()
        self.player_starting_pos = ga.Pos(level_data[f"player_starting_pos_{side}"])
        tiles_of_error = self.player_starting_pos / 16
        self.player_starting_pos = self.player_starting_pos * PIXEL + offset - tiles_of_error * PER_TILE_ERROR
        self.name = name

    def gen_tiles(self):
        for layer in self.layers:
            self.layered_groups.append(pygame.sprite.Group())
            self.solid.append(pygame.sprite.Group())
            self.damaging.append(pygame.sprite.Group())
            for y, row in enumerate(layer):
                for x, tile_id in enumerate(row):
                    global tiles
                    if tile_id not in tile_ids: continue
                    tile = Tile(
                        tile_type=tile_id,
                        pos=ga.Pos(x, y) * TILE_SIZE,
                        level_pos=(x, y)
                    )

                    hitbox_tiles = []

                    for i in tiles[tile_id]["h"]:
                        hitbox_tile = HbTile(
                            pos=ga.Pos(x, y) * TILE_SIZE + self.offset,
                            level_pos=(x, y),
                            hitbox=i
                        )
                        hitbox_tiles.append(hitbox_tile)

                    self.layered_groups[-1].add(tile)

                    if tiles[tile_id]["k"]:
                        self.damaging[-1].add(*hitbox_tiles)
                    elif hitbox_tiles[0].rect.size != (0, 0):
                        self.solid[-1].add(*hitbox_tiles)

    def gen_texture(self, stop_at=-1):
        self.texture = pygame.Surface(TILE_SIZE * (len(self.layers[0][0]), len(self.layers[0])))
        self.texture.set_colorkey(ga.BLACK)
        for idx, group in enumerate(self.layered_groups):
            if idx == stop_at: break
            group.draw(self.texture)

        if self.flip_door:
            self.texture.blit(DOOR_FRAME_FLIPPED, self.frame_pos)
        else:
            self.texture.blit(DOOR_FRAME, self.frame_pos)


def load_levels():
    global levels, custom_levels_start
    with open(os.path.join(LOCAL_DIR, "assets/levels/levels.json")) as level_list_file:
        level_list = json.load(level_list_file)
        levels = []
        for level in level_list["normal"]:
            levels.append(os.path.join(LOCAL_DIR, f"assets/levels/{level}"))
        custom_levels_start = len(level_list["normal"])
        for level_name in level_list["custom"][":order"]:
            levels.append((level_name, level_list["custom"][level_name]))


def load_level(path):
    level_info = json.loads(encrypter.decrypt(path))
    return Level(level_info, "left"), Level(level_info, "right")


def reload_level(path, idx):
    levels[idx] = load_level(path)


    load_levels()


load_levels()
