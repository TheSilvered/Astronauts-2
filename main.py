from math import cos, degrees, sqrt
import time
import random
import os

import webbrowser
import tkinter
import tkinter.filedialog
from send2trash import send2trash, TrashPermissionError
import encrypter

use_easter_egg_titles = random.randint(1, 100) == 1

from constants import *

pygame.init()

with open(SETTINGS_PATH, "r") as settings_file:
    settings = json.load(settings_file)

flags = pygame.DOUBLEBUF

screen = pygame.display.set_mode(SIZE, flags)
icon = pygame.image.load(f"{LOCAL_DIR}/assets/textures/misc/icon.png")
if use_easter_egg_titles:
    pygame.display.set_caption(LAYOUT_NAMES[0])
else:
    pygame.display.set_caption("Astronauts!")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

current_layout = LayoutTypes.PLAY_SCREEN
fading_layout = LayoutTypes.NO_LAYOUT
fading_start = 0

bg_color = (12, 0, 117)
stars = []
stars_pos = []

random.seed(11)

for i in range(100):
    pos = ga.Pos(random.randint(0, SIZE.w), random.randint(0, SIZE.h))
    star = random.randint(1, 9)
    if star < 4: star = 1
    elif 3 < star < 9: star = 2
    else: star = 3

    path = f"{LOCAL_DIR}/assets/textures/background/star{star}.png"
    if star == 1:
        resize = SIZE // (640, 108)
    else:
        resize = SIZE // (192, 54)

    stars.append(
        pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), ga.Size(random.randint(*resize.list())))
    )
    stars_pos.append(pos)

screen.fill(bg_color)

for star, pos in zip(stars, stars_pos): screen.blit(star, pos)
loading_text = ga.StaticLabel(
    c_pos=SIZE//2,
    text=LANG.Loading.loading_levels,
    text_size=int(SIZE.w/20),
    text_font=FONT
)
loading_text.render(screen)
pygame.display.update()

track = 0
pygame.mixer.music.load(SOUND_TRACKS[track])
pygame.mixer.music.set_volume(settings["music_volume"])
pygame.mixer.music.play(fade_ms=2000)

# I need to set the screen mode before these get imported
from level import levels, reload_level, custom_levels_start, load_level, tiles, Tile, HbTile
from player import player1, player2
from assets_import import *

current_level = None
current_editor_level = None
dummy_editor_level = load_level(levels[0])
current_playing_level = [(), ()]

try: current_res_idx = ALLOWED_SCREEN_RES.index(settings["screen_res"])
except ValueError: current_res_idx = 0
current_lang_idx = LANGS.index(settings["language"])
starting_settings = (settings["screen_res"], settings["fullscreen"], settings["language"])

edits_history = []
current_edit = -1
ignore_button_up = False


def update_settings_file():
    global settings
    with open(SETTINGS_PATH, "w") as settings_file:
        json.dump(settings, settings_file, indent=4)


def set_layout(layout):
    global current_layout, fading_layout, fading_start, ignore_button_up
    fading_layout = current_layout
    current_layout = layout
    GAME_LAYOUTS[current_layout].run_buttons = True
    GAME_LAYOUTS[fading_layout].run_buttons = False
    if fading_layout == LayoutTypes.SETTINGS: update_settings_file()
    ignore_button_up = True
    if current_layout == LayoutTypes.EDITOR and current_editor_level is not None:
        player1.level = current_editor_level[0]
        player2.level = current_editor_level[1]
        reset_players()
        player1.locked = False
        player2.locked = False

    for i in GAME_LAYOUTS[fading_layout].items:
        if isinstance(i, ga.Slider):
            i._bar.fade_out.start()
            i._button.fade_out.start()
        else:
            i.fade_out.start()

    for i in GAME_LAYOUTS[current_layout].items:
        if isinstance(i, ga.Slider):
            i._bar.transparency = 0
            i._button.transparency = 0
            i._bar.fade_in.start()
            i._button.fade_in.start()
        else:
            i.transparency = 0
            i.fade_in.start()
            if isinstance(i, NewButton):
                i.normal._prev_val = i.sn
                i.hover._prev_val = i.sn
                i.click._prev_val = i.sn

    if use_easter_egg_titles:
        pygame.display.set_caption(LAYOUT_NAMES.get(current_layout, "Astronauts!"))

    fading_start = time.time()


def reset_players():
    player1.reset()
    player2.reset()


def set_level(level):
    global current_level, current_playing_level
    GAME_LAYOUTS[LayoutTypes.NEXT_LEVEL][3]._fargs = []
    try:
        current_playing_level.clear()
        if isinstance(levels[level], tuple):
            current_playing_level = list(load_level(levels[level][1]))
        else:
            current_playing_level = list(load_level(levels[level]))
        player1.level = current_playing_level[0]
        player2.level = current_playing_level[1]
        reset_players()
        current_level = level
        if current_level >= custom_levels_start:
            set_layout(LayoutTypes.IN_GAME_CUSTOM)
        else:
            set_layout(LayoutTypes.IN_GAME)
    except IndexError:
        if current_level >= custom_levels_start:
            set_layout(LayoutTypes.END_SCREEN)
        else:
            set_layout(LayoutTypes.CREDITS)


def flip_gravity():
    if player1.dead and player2.dead: return
    player1.flip_grav()
    player2.flip_grav()
    pygame.mixer.Sound.play(SWITCH_GRAV)


def change_allowed_levels():
    if settings["last_level"] + 1 == custom_levels_start:
        return
    settings["last_level"] += 1
    update_settings_file()
    try:
        image = pygame.image.load(f"{LOCAL_DIR}/assets/textures/thumbnails/level{settings['last_level']}.png")
    except FileNotFoundError:
        image = pygame.image.load(f"{LOCAL_DIR}/assets/textures/thumbnails/no_image.png")

    image = pygame.transform.smoothscale(image, ga.IntSize(SIZE.w / 7.1))

    page = settings["last_level"] // 12

    button_index = settings["last_level"] - 12 * page

    button = NewButton(
        parent=SCREEN_E,
        c_anchor=BUTTON_ANCHOR[button_index // 4][button_index % 4],
        offset=BUTTON_OFFSET[button_index // 4][button_index % 4],
        size=SIZE // (6.4, 4),
        tn=image,
        sound=BUTTON_CLICK,
        text_kwargs={
            "text": LANG.LevelSelection.level.format(level_no=settings["last_level"] + 1),
            "text_size": int(SIZE.w / 42.6),
            "offset": (0, SIZE.h / 12),
            "text_font": FONT
        },
        function=set_level,
        fargs=[settings["last_level"]]
    )

    button.add_ani(ga.AlphaAni(**FADE_IN))
    button.add_ani(ga.AlphaAni(**FADE_OUT))

    GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages[page][button_index] = button


def get_level_button(name, image, row, col, locked, level_no):
    global button_textures
    image = pygame.transform.smoothscale(image, ga.IntSize(SIZE.w / 7.1))

    tn = button_textures._tn.frames[0].copy()
    th = button_textures._th.frames[0].copy()
    tc = button_textures._tc.frames[0].copy()

    button = NewButton(
        parent=SCREEN_E,
        c_anchor=BUTTON_ANCHOR[row][col],
        offset=BUTTON_OFFSET[row][col],
        size=SIZE // (6.4, 4),
        sn=ga.get_size(tn),
        tn=image,
        sound=BUTTON_CLICK,
        function=None if locked else set_level,
        fargs=[level_no],
        make_texture=False
    )

    image_element = ga.StaticElement(
        c_pos=ga.get_size(tn) // 2,
        texture=image
    )

    image_element.render(tn)
    image_element.render(th)
    image_element.render(tc)

    button.bn = tn
    button.bh = th
    button.bc = tc

    button.change_text(
        text_kwargs={
            "text": name,
            "text_size": int(SIZE.w / 42.6),
            "offset": (0, SIZE.h / 12),
            "text_font": FONT
        }
    )

    button.add_ani(ga.AlphaAni(**FADE_IN))
    button.add_ani(ga.AlphaAni(**FADE_OUT))

    return button


def gen_level_buttons():
    buttons = []

    current_row = 0
    current_column = -1
    current_page = 0

    locked_image = pygame.image.load(f"{LOCAL_DIR}/assets/textures/thumbnails/locked.png").convert_alpha()
    no_image = pygame.image.load(f"{LOCAL_DIR}/assets/textures/thumbnails/no_image.png").convert_alpha()
    gray_scale = pygame.image.load(f"{LOCAL_DIR}/assets/textures/thumbnails/grayscale.png").convert_alpha()

    for i in range(len(levels)):
        is_custom = i >= custom_levels_start
        if i > settings["last_level"] and not is_custom:
            image = locked_image
        elif is_custom:
                image = gray_scale
        else:
            try:
                image = pygame.image.load(f"{LOCAL_DIR}/assets/textures/thumbnails/level{i}.png")
            except FileNotFoundError:
                image = no_image

        if i == custom_levels_start:
            current_column = 0
            current_row = 0
            current_page += 1
            GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages.append([])
        else:
            current_column += 1
            if current_column > 3:
                current_row += 1
                current_column = 0
            if current_row > 2:
                current_column = 0
                current_row = 0
                current_page += 1
                GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages.append([])

        image = pygame.transform.smoothscale(image, ga.IntSize(SIZE.w / 7.1))

        button = get_level_button(
            name=levels[i][0] if is_custom else LANG.LevelSelection.level.format(level_no=i + 1),
            image=image,
            row=current_row,
            col=current_column,
            locked=i > settings["last_level"] and not is_custom,
            level_no=i
        )

        GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages[current_page].append(button)


def gen_block_pages():
    for i in sorted(list(tiles)):
        texture = pygame.transform.scale(tiles[i]["t"], TILE_SIZE * 2)

        element = BlockElement(
            parent=SCREEN_E,
            anchor=ga.AncType.UC,
            offset=SIZE // (2.9, 50),
            texture=texture,
            id_=i
        )

        element.add_ani(ga.AlphaAni(**FADE_IN))
        element.add_ani(ga.AlphaAni(**FADE_OUT))
        element.transparency = 0

        if tiles[i]["k"]:
            GAME_LAYOUTS[LayoutTypes.EDITOR].others[1].pages[2][0].pages.append([element])
        elif tiles[i]["h"] == [(0, 0, 0, 0)]:
            GAME_LAYOUTS[LayoutTypes.EDITOR].others[1].pages[3][0].pages.append([element])
        else:
            GAME_LAYOUTS[LayoutTypes.EDITOR].others[1].pages[1][0].pages.append([element])


def stop_game():
    update_settings_file()
    pygame.mixer.music.fadeout(200)
    save_level()
    time.sleep(0.2)
    pygame.quit()
    sys.exit()


def increase_screen_res():
    global current_res_idx, settings
    if settings["fullscreen"]: return
    if current_res_idx < len(ALLOWED_SCREEN_RES) - 1:
        current_res_idx += 1


def decrease_screen_res():
    global current_res_idx, settings
    if settings["fullscreen"]: return
    if current_res_idx > 0:
        current_res_idx -= 1


def increase_language():
    global current_lang_idx
    current_lang_idx = (current_lang_idx + 1) % len(LANGS)


def decrease_language():
    global current_lang_idx
    current_lang_idx = (current_lang_idx - 1) % len(LANGS)


def open_level(path=None):
    global current_editor_level, ignore_button_up

    with open(f"{LOCAL_DIR}/assets/levels/levels.json", "r") as levels_list_file:
        levels_list = json.load(levels_list_file)

    if path is None:
        tk_window = tkinter.Tk()
        tk_window.withdraw()
        path = tkinter.filedialog.askopenfilename(parent=tk_window, initialdir=f"{LOCAL_DIR}/assets/levels/custom")
        tk_window.destroy()
        ignore_button_up = True

    path = path.replace("\\", "/")

    if path in LOCKED_LEVELS:
        set_layout(LayoutTypes.FAILED_OPENING)
        return

    try:
        level = load_level(path)
    except Exception:
        if path != "":
            set_layout(LayoutTypes.FAILED_OPENING)
        return False

    level_name = path.split("/")[-1][:-6]

    level[0].name = level_name
    level[0].data = json.loads(encrypter.decrypt(path))

    current_editor_level = level

    player1.level = current_editor_level[0]
    player2.level = current_editor_level[1]
    reset_players()
    player1.locked = False
    player2.locked = False

    added = not level_name in levels_list["custom"][":order"]
    if added:
        levels_list["custom"][":order"].append(level_name)
        levels_list["custom"][level_name] = path
        levels.append((level_name, path))
        with open(f"{LOCAL_DIR}/assets/levels/levels.json", "w") as levels_list_file:
            json.dump(levels_list, levels_list_file, indent=4)
    else:
        levels[levels_list["custom"][":order"].index(level_name) + len(levels_list["normal"])] = (level_name, path)
        return True

    if len(GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages) == 1 or \
       len(GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages[-1]) == 12:
        GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages.append([])
        row = 0
        col = 0
    else:
        page_len = len(GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages[-1])
        row = page_len // 4
        col = page_len % 4

    try:
        image = pygame.image.load(f"{LOCAL_DIR}/assets/textures/thumbnails/{level_name}.png")
    except FileNotFoundError:
        image = pygame.image.load(f"{LOCAL_DIR}/assets/textures/thumbnails/grayscale.png")

    button = get_level_button(
        name=level_name,
        image=image,
        row=row, col=col,
        locked=False,
        level_no=len(levels) - 1
    )

    GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0].pages[-1].append(button)
    return True


def create_level(overwrite=False):
    global new_level_text
    if os.path.exists(f"{LOCAL_DIR}/assets/levels/custom/{new_level_text._current_text}.level") and not overwrite:
        set_layout(LayoutTypes.OVERWRITE)
        return

    with open(f"{LOCAL_DIR}/assets/levels/new_level_default.level", "rb") as base_file:
        with open(f"{LOCAL_DIR}/assets/levels/custom/{new_level_text._current_text}.level", "wb+") as new_level_file:
            new_level_file.write(base_file.read())

    open_level(f"{LOCAL_DIR}/assets/levels/custom/{new_level_text._current_text}.level")

    new_level_text._current_text = ""
    new_level_text._cursor_pos = 0
    new_level_text.update_text()
    set_layout(LayoutTypes.EDITOR)


def get_tile_pos():
    mouse_pos = ga.Pos(pygame.mouse.get_pos())

    if mouse_pos > LEVEL_OFFSET_RIGHT:
        mouse_pos -= LEVEL_OFFSET_RIGHT
        side = "right"
    else:
        mouse_pos -= LEVEL_OFFSET_LEFT
        side = "left"

    tile_pos = mouse_pos // TILE_SIZE
    if tile_pos.x > 18 or tile_pos.x < 0 or tile_pos.y > 18 or tile_pos.y < 0:
        return None
    else:
        return side, ga.IntPos(tile_pos)


def set_level_tile(side, tile_pos, tile_id=None, layer=None, change_edits=True):
    global current_editor_level, edits_history, current_edit
    if current_editor_level is None:
        return

    idx = 0 if side == "left" else 1
    door_pos = ga.Pos(current_editor_level[0].data[f"door_pos_{side}"])
    offset = LEVEL_OFFSET_LEFT if side == "left" else LEVEL_OFFSET_RIGHT

    if door_pos - 1 < tile_pos < door_pos + (4, 3):
        current_editor_level[0].data[f"flip_door_{side}"] = not current_editor_level[0].data[f"flip_door_{side}"]
        current_editor_level[idx].flip_door = not current_editor_level[idx].flip_door
        if current_editor_level[idx].flip_door:
            new_door_pos = current_editor_level[idx].frame_pos + TILE_SIZE * (1, 0) + offset
        else:
            new_door_pos = current_editor_level[idx].frame_pos + TILE_SIZE * (1, 1) + offset
        current_editor_level[idx].door.pos = new_door_pos
        current_editor_level[idx].gen_texture(current_layer_shown)
        if change_edits:
            if current_edit + 1 < len(edits_history):
                edits_history = edits_history[:current_edit + 1]
                current_edit = len(edits_history)
            else:
                current_edit += 1
            edits_history.append([[side, tile_pos], [side, tile_pos]])
        return

    if layer is None:
        layer = current_layer_shown - 1
    tile_selector = GAME_LAYOUTS[LayoutTypes.EDITOR].others[1]
    block_page = tile_selector.pages[tile_selector.current_page][0]
    if tile_id is None:
        tile_id = block_page.pages[block_page.current_page][0].id

    try:
        current_editor_level[0].data[f"layers_{side}"][layer][tile_pos[1]][tile_pos[0]] = tile_id
    except IndexError:
        current_editor_level[0].data[f"layers_{side}"][-1][tile_pos[1]][tile_pos[0]] = tile_id
        layer = len(current_editor_level[0].data[f"layers_{side}"]) - 1

    removed_id = 0
    has_removed = False
    is_removing = False

    for i in current_editor_level[idx].layered_groups[layer].sprites():
        if i.level_pos == tile_pos:
            if i.id == tile_id:
                return
            has_removed = True
            removed_id = i.id
            current_editor_level[idx].layered_groups[layer].remove(i)
            break

    for i in current_editor_level[idx].solid[layer]:
        if i.level_pos == tile_pos:
            is_removing = True
            current_editor_level[idx].solid[layer].remove(i)
        elif is_removing: break

    is_removing = False

    for i in current_editor_level[idx].damaging[layer]:
        if i.level_pos == tile_pos:
            is_removing = True
            current_editor_level[idx].damaging[layer].remove(i)
        elif is_removing: break

    if change_edits and (has_removed or tile_id != 0):
        if current_edit + 1 < len(edits_history):
            edits_history = edits_history[:current_edit + 1]
            current_edit = len(edits_history)
        else:
            current_edit += 1
        edits_history.append([[side, tile_pos, removed_id, layer], [side, tile_pos, tile_id, layer]])

    if tile_id != 0:
        tile = Tile(
            tile_type=tile_id,
            pos=ga.Pos(tile_pos) * TILE_SIZE,
            level_pos=tile_pos
        )

        hitbox_tiles = []

        for i in tiles[tile_id]["h"]:
            hitbox_tile = HbTile(
                pos=ga.Pos(tile_pos) * TILE_SIZE + offset,
                level_pos=tile_pos,
                hitbox=i
            )
            hitbox_tiles.append(hitbox_tile)


        current_editor_level[idx].layered_groups[layer].add(tile)
        if tiles[tile_id]["k"]:
            current_editor_level[idx].damaging[layer].add(*hitbox_tiles)
        elif hitbox_tiles[0].rect.size != (0, 0):
            current_editor_level[idx].solid[layer].add(*hitbox_tiles)

    current_editor_level[idx].gen_texture(current_layer_shown)


def change_door_pos():
    global door_info, is_dragging_door, can_drag_door
    if current_editor_level is None or get_tile_pos() is None:
        is_dragging_door = False
        can_drag_door = False
        return
    tile_pos = get_tile_pos()[1]
    side = get_tile_pos()[0]
    if side != door_info[0]:
        is_dragging_door = False
        can_drag_door = False
        return
    idx = int(door_info[0] == "right")
    door_pos = current_editor_level[0].data[f"door_pos_{side}"]
    if tile_pos - door_info[1] == door_pos:
        return

    offset = LEVEL_OFFSET_LEFT if door_info[0] == "left" else LEVEL_OFFSET_RIGHT
    frame_pos = tile_pos - door_info[1]
    current_editor_level[idx].frame_pos = TILE_SIZE * frame_pos
    current_editor_level[0].data[f"door_pos_{side}"] = frame_pos.list()
    if current_editor_level[idx].flip_door:
        new_door_pos = current_editor_level[idx].frame_pos + TILE_SIZE * (1, 0) + offset
    else:
        new_door_pos = current_editor_level[idx].frame_pos + TILE_SIZE * (1, 1) + offset
    current_editor_level[idx].door.pos = new_door_pos
    current_editor_level[idx].gen_texture(current_layer_shown)


def save_level():
    global current_editor_level, edits_history, current_edit

    if current_editor_level is None: return

    with open(f"{LOCAL_DIR}/assets/levels/levels.json") as level_info_file:
        level_info = json.load(level_info_file)

    encrypter.encrypt(json.dumps(current_editor_level[0].data),
                      level_info["custom"][current_editor_level[0].name],
                      False)

    edits_history = []
    current_edit = -1


def undo():
    global edits_history, current_edit
    try:
        if current_edit == -1: raise IndexError
        args = edits_history[current_edit][0]
    except IndexError:
        return

    set_level_tile(*args, change_edits=False)
    current_edit -= 1


def redo():
    global edits_history, current_edit
    current_edit += 1
    try:
        args = edits_history[current_edit][1]
    except IndexError:
        current_edit -= 1
        return

    set_level_tile(*args, change_edits=False)


def delete_level(force_deletion=False):
    global current_editor_level
    with open(f"{LOCAL_DIR}/assets/levels/levels.json") as levels_info_file:
        levels_info = json.load(levels_info_file)

    file_name = levels_info["custom"][levels_info["custom"][":order"][current_level - custom_levels_start]]

    if force_deletion:
        try:
            os.remove(file_name)
        except Exception:
            set_layout(LayoutTypes.FAILED_DELETION)
            return
    else:
        try:
            send2trash(file_name)
        except TrashPermissionError:
            set_layout(LayoutTypes.FAILED_TRASH)
            return
        except OSError:
            try:
                send2trash(file_name.replace("/", "\\"))
            except (TrashPermissionError, OSError):
                set_layout(LayoutTypes.FAILED_TRASH)
                return

    page = (current_level - custom_levels_start) // 12 + 1
    index = (current_level - custom_levels_start) - (12 * (page-1))
    levels_list = GAME_LAYOUTS[LayoutTypes.LEVEL_SELECT].others[0]
    if levels_list.current_page == 0: return
    current_col = ((len(levels_list.pages[-1]) - 1) % 4) - 1
    current_row = (len(levels_list.pages[-1]) - 1) // 4
    current_page = len(levels_list.pages) - 1
    if current_col < 0:
        current_row -= 1
        current_col = 3
    if current_row < 0:
        current_row = 2
        current_col = 3
        current_page -= 1

    del levels_list.pages[page][index]
    if levels_list.pages[page] == []:
        del levels_list.pages[page]
        levels_list.prev_page()
    if current_editor_level is not None:
        if current_editor_level[0].name == levels_info["custom"][":order"][current_level - custom_levels_start]:
            current_editor_level = None
    del levels_info["custom"][levels_info["custom"][":order"][current_level - custom_levels_start]]
    del levels_info["custom"][":order"][current_level - custom_levels_start]
    with open(f"{LOCAL_DIR}/assets/levels/levels.json", "w") as levels_info_file:
        json.dump(levels_info, levels_info_file, indent=4)

    for i in range(len(levels_list.pages) - 1, page - 1, -1):
        start = min(10, len(levels_list.pages[i]) - 1) if i == page\
                else min(11, len(levels_list.pages[i]) - 1)
        for j in range(start, -1, -1):
            if i == page and j < index: break
            levels_list.pages[i][j].offset = BUTTON_OFFSET[current_row][current_col]
            levels_list.pages[i][j]._anc_type = BUTTON_ANCHOR[current_row][current_col]
            levels_list.pages[i][j]._fargs[0] -= 1

            if i != current_page:
                levels_list.pages[i - 1].append(levels_list.pages[i][j])
                del levels_list.pages[i][j]
                if i == 0 and len(levels_list.pages[i]) == 0:
                    del levels_list.pages[i]

            if j == 0 and len(levels_list.pages[i]) == 0:
                del levels_list.pages[i]
                levels_list.prev_page()

            current_col -= 1
            if current_col < 0:
                current_row -= 1
                current_col = 3
            if current_row < 0:
                current_row = 2
                current_col = 3
                current_page -= 1

    set_layout(LayoutTypes.LEVEL_SELECT)


def change_language():
    pass


def add_image():
    if current_editor_level is None: return

    tk_window = tkinter.Tk()
    tk_window.withdraw()
    path = tkinter.filedialog.askopenfilename(parent=tk_window, initialdir=f"{LOCAL_DIR}/assets/levels/custom")
    tk_window.destroy()
    ignore_button_up = True

    path = path.replace("\\", "/")

    try:
        image = pygame.image.load(path)
    except Exception:
        set_layout(LayoutTypes.FAILED_OPENING)

    image = pygame.transform.smoothscale(image, (180, 90))

    new_image = pygame.Surface((180, 180))
    new_image.blit(image, (0, 24))
    new_image.set_colorkey((0, 0, 0))
    bytes_ = pygame.image.tostring(new_image, "RGBA")
    bytes_list = list(bytes_)
    new_bytes_list = [int(i / 255 * 127) for i in bytes_list]
    new_bytes_list = bytes(new_bytes_list)
    image_str = new_bytes_list.decode("ascii")
    current_editor_level[0].data["image"] = image_str


screen.fill(bg_color)
for star, pos in zip(stars, stars_pos): screen.blit(star, pos)
loading_text.change_text(LANG.Loading.gen_elements)
loading_text.render(screen)
pygame.display.update()

close_button = NewButton(
    parent=SCREEN_E,
    c_anchor=ga.AncType.UR,
    offset=SIZE // (-42.67, 24),
    size=max(SIZE.w, SIZE.h) // 32,
    cn=ga.RED,
    ch=(255, 70, 70),
    halo_ch=(255, 70, 70),
    tn=CLOSE_BUTTON,
    sound=BUTTON_CLICK,
    function=stop_game
)

minimize_button = NewButton(
    parent=SCREEN_E,
    c_anchor=ga.AncType.UR,
    offset=SIZE // (-16, 24),
    size=max(SIZE.w, SIZE.h) // 32,
    tn=MINIMIZE_BUTTON,
    sound=BUTTON_CLICK,
    function=pygame.display.iconify
)

button_textures = NewButton(
    pos=ga.Pos(0),
    size=SIZE // (6.4, 4)
)

use_control_buttons = pyautogui.size().height <= SIZE.h

next_level_bg = pygame.Surface(SIZE // 2, pygame.SRCALPHA)
curve = next_level_bg.get_width() // 10

points = (
    (0, curve),
    (curve, 0),
    (next_level_bg.get_width() - curve - 1, 0),
    (next_level_bg.get_width() - 1, curve),
    (next_level_bg.get_width() - 1, next_level_bg.get_height() - curve - 1),
    (next_level_bg.get_width() - curve - 1, next_level_bg.get_height() - 1),
    (curve, next_level_bg.get_height() - 1),
    (0, next_level_bg.get_height() - curve - 1)
)

pygame.draw.polygon(next_level_bg, NEXT_LEVEL_BG_COLOR, points)

w, h = ga.get_size(next_level_bg)
color = NEXT_LEVEL_BG_COLOR

for x in range(curve):
    for y in range(curve):
        distance = sqrt((x-curve) ** 2 + (y-curve) ** 2)
        off_x = w - x - 1
        off_y = h - y - 1
        if distance < curve:
            next_level_bg.set_at((x, y), color)
            next_level_bg.set_at((off_x, y), color)
            next_level_bg.set_at((x, off_y), color)
            next_level_bg.set_at((off_x, off_y), color)
        elif distance < curve + 1:
            current_color = color + (255 * (1 - (distance-curve)),)
            next_level_bg.set_at((x, y), current_color)
            next_level_bg.set_at((off_x, y), current_color)
            next_level_bg.set_at((x, off_y), current_color)
            next_level_bg.set_at((off_x, off_y), current_color)

GAME_LAYOUTS = {
    LayoutTypes.NO_LAYOUT: Layout(
        buttons=[],
        others=[]
    ),
    LayoutTypes.PLAY_SCREEN: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                size=SIZE // (4, 6),
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.PlayScreen.play,
                    "text_size": int(SIZE.w // 21.33),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.LEVEL_SELECT],
                # texture_debug=True
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / 6),
                size=SIZE // (6.4, 9),
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.PlayScreen.settings,
                    "text_size": int(SIZE.w // 36.57),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.SETTINGS]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / 3.28),
                size=SIZE // (6.4, 9),
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.PlayScreen.editor,
                    "text_size": int(SIZE.w // 36.57),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.EDITOR]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.DR,
                size=CHECKBOX_SIZE,
                offset=SIZE.w // -20,
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": "?",
                    "text_size": int(SIZE.w // 23),
                    "text_font": f"{LOCAL_DIR}/assets/font/bold.ttf"
                },
                function=set_layout,
                fargs=[LayoutTypes.HELP_SCREEN]
            )
        ),
        others=(
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=(0, SIZE.h / 5),
                text="Astronauts!",
                text_font=f"{LOCAL_DIR}/assets/font/bold.ttf",
                text_size=int(SIZE.w // 13)
            ),
        )
    ),
    LayoutTypes.CREDITS: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=SIZE // (15.06, 18),
                size=SIZE // (9.84, 18),
                tn=BACK_BUTTON,
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.Credits.back,
                    "text_size": int(SIZE.w // 51.2),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.LEVEL_SELECT]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=SIZE // (8.5, 2.35),
                size=SIZE // (6.4, 9),
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": "itch.io",
                    "text_size": int(SIZE.w // 36.57),
                    "text_font": FONT
                },
                function=webbrowser.open,
                fargs=["https://thesilvered.itch.io/"]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=SIZE // (-8.5, 2.35),
                size=SIZE // (6.4, 9),
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": "GitHub",
                    "text_size": int(SIZE.w // 36.57),
                    "text_font": FONT
                },
                function=webbrowser.open,
                fargs=["https://github.com/TheSilvered"]
            )
        ),
        others=(
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=(0, SIZE.h/6),
                text=LANG.Credits.game_made_by,
                text_size=int(SIZE.w / 25.6),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=(0, SIZE.h/3.5),
                text="TheSilvered",
                text_size=int(SIZE.w / 32),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h/10),
                text=f"{LANG.Credits.music}:",
                text_size=int(SIZE.w / 32),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h/6),
                text=LANG.Credits.song.format(song="Cosmic glow", author="Andrewkn"),
                text_size=int(SIZE.w / 42),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h/4.36),
                text=LANG.Credits.song.format(song="Deep space 9", author="Magic-828"),
                text_size=int(SIZE.w / 42),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h/3.42),
                text=LANG.Credits.song.format(song="Space vacuum - a cinematic journey", author="NaturesEye"),
                text_size=int(SIZE.w / 42),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h/2.82),
                text=LANG.Credits.song.format(song="The death of a Supernova", author="bandersn4tch"),
                text_size=int(SIZE.w / 42),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h/2.4),
                text=LANG.Credits.song.format(song="Universe - space sounds", author="JuliusH"),
                text_size=int(SIZE.w / 42),
                text_font=FONT
            )
        )
    ),
    LayoutTypes.SETTINGS: Layout(
        buttons=[
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=SIZE // (15.06, 18),
                size=SIZE // (9.84, 18),
                tn=BACK_BUTTON,
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.Settings.back,
                    "text_size": int(SIZE.w // 51.2),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.PLAY_SCREEN]
            )
        ],
        others=[
        Page(
        pages=(
            (
                CheckBox(
                    starting_state=settings["fullscreen"],
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.CL,
                    offset=SIZE // (5.21, 10),
                    size=CHECKBOX_SIZE,
                    sound=BUTTON_CLICK
                ),
                NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.DL,
                    offset=SIZE // (5.21, -4.5),
                    size=CHECKBOX_SIZE,
                    tn=LEFT_ARROW,
                    sound=BUTTON_CLICK,
                    function=decrease_screen_res
                ),
                NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.DL,
                    offset=SIZE // (2.4, -4.5),
                    size=CHECKBOX_SIZE,
                    tn=RIGHT_ARROW,
                    sound=BUTTON_CLICK,
                    function=increase_screen_res
                ),
                CheckBox(
                    starting_state=settings["show_fps"],
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.CC,
                    offset=SIZE // (21, 10),
                    size=CHECKBOX_SIZE,
                    sound=BUTTON_CLICK
                ),
                NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.DC,
                    offset=SIZE // (21, -4.5),
                    size=CHECKBOX_SIZE,
                    tn=LEFT_ARROW,
                    sound=BUTTON_CLICK,
                    function=decrease_language
                ),
                NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.DC,
                    offset=SIZE // (3.66, -4.5),
                    size=CHECKBOX_SIZE,
                    tn=RIGHT_ARROW,
                    sound=BUTTON_CLICK,
                    function=increase_language
                ),
                ga.Slider(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UL,
                    offset=SIZE // (6, 4),
                    indicator_kwargs={
                        "size": SIZE.h / 23
                    },
                    indicator_class=NewButton,
                    bar_kwargs={
                        "size": SIZE // (3.2, 36),
                        "curve": BUTTON_CURVE,
                        "cn": BAR_CN,
                        "ch": BAR_CH,
                        "cc": BAR_CC,
                        "halo_ch": BAR_CH,
                        "halo_cc": BAR_CC,
                        "halo": HALO,
                        # "texture_debug": True
                    },
                    indicator_pos=settings["music_volume"]
                ),
                ga.Slider(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UR,
                    offset=(-SIZE.w/6 - SIZE.w // 3.2, SIZE.h/4),
                    indicator_kwargs={
                        "size": SIZE.h / 23
                    },
                    indicator_class=NewButton,
                    bar_kwargs={
                        "size": SIZE // (3.2, 36),
                        "curve": BUTTON_CURVE,
                        "cn": BAR_CN,
                        "ch": BAR_CH,
                        "cc": BAR_CC,
                        "halo_ch": BAR_CH,
                        "halo_cc": BAR_CC,
                        "halo": HALO,
                        # "texture_debug": True
                    },
                    indicator_pos=settings["sfx_volume"]
                ),
                ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UL,
                    offset=(SIZE.w/6, SIZE.h/3.4),
                    text="---%",
                    text_size=int(SIZE.w // 36.57),
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UR,
                    offset=(-SIZE.w/6 - SIZE.w // 3.2, SIZE.h/3.4),
                    text="---%",
                    text_size=int(SIZE.w // 36.57),
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UL,
                    offset=(SIZE.w/6, SIZE.h/6),
                    text=LANG.Settings.music,
                    text_size=int(SIZE.w // 36.57),
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UR,
                    offset=(-SIZE.w/6 - SIZE.w // 3.2, SIZE.h/6),
                    text=LANG.Settings.sfx,
                    text_size=int(SIZE.w // 36.57),
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.CL,
                    offset=SIZE // (4.3, 15),
                    text=LANG.Settings.fullscreen.format(state=LANG.General.yes if settings["fullscreen"] else LANG.General.no),
                    text_size=int(SIZE.w // 36.57),
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.DL,
                    offset=SIZE // (3.3, -4.5),
                    text=f"{ALLOWED_SCREEN_RES[current_res_idx][0]}x{ALLOWED_SCREEN_RES[current_res_idx][1]}",
                    text_size=int(SIZE.w // 40),
                    color=ga.GRAY(180) if settings["fullscreen"] else ga.WHITE,
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.CC,
                    offset=SIZE // (11.3, 15),
                    text=LANG.Settings.show_fps.format(state=LANG.General.yes if settings["show_fps"] else LANG.General.no),
                    text_size=int(SIZE.w // 36.57),
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.UC,
                    offset=(0, SIZE.h // 12),
                    text=LANG.Settings.sound,
                    text_size=int(SIZE.w // 25),
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.CC,
                    offset=(0, -SIZE.h // 20),
                    text=LANG.Settings.video,
                    text_size=int(SIZE.w // 25),
                    text_font=FONT
                ),
                ga.Label(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.DC,
                    offset=SIZE // (6.21, -4.5),
                    text=LANG_NAMES[settings["language"]],
                    text_size=int(SIZE.w // 40),
                    text_font=FONT
                )
            ),
        ),
        next_page_button=NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CR,
                offset=(-SIZE.w // 25, 0),
                size=CHECKBOX_SIZE,
                tn=RIGHT_ARROW,
                sound=BUTTON_CLICK
            ),
        prev_page_button=NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CL,
                offset=(SIZE.w // 25, 0),
                size=CHECKBOX_SIZE,
                tn=LEFT_ARROW,
                sound=BUTTON_CLICK
            )
        )
        ]
    ),
    LayoutTypes.IN_GAME: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=SIZE // (15.06, 18),
                size=SIZE // (9.84, 18),
                tn=BACK_BUTTON,
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.InGameScreen.back,
                    "text_size": int(SIZE.w // 51.2),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.LEVEL_SELECT]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=SIZE // (-8.9, 15.65),
                size=SIZE // (5, 14.4),
                text_kwargs={
                    "text": LANG.InGameScreen.flip_gravity,
                    "text_size": int(SIZE.w / 45),
                    "text_font": FONT
                },
                function=flip_gravity
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=SIZE // (11.9, 15.65),
                size=SIZE // (7, 14.4),
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.InGameScreen.retry,
                    "text_size": int(SIZE.w / 45),
                    "text_font": FONT
                },
                function=reset_players
            )
        ),
        others=()
    ),
    LayoutTypes.IN_GAME_CUSTOM: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=SIZE // (15.06, 18),
                size=SIZE // (9.84, 18),
                tn=BACK_BUTTON,
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.InGameScreen.back,
                    "text_size": int(SIZE.w // 51.2),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.LEVEL_SELECT]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=SIZE // (-8.9, 15.65),
                size=SIZE // (5, 14.4),
                text_kwargs={
                    "text": LANG.InGameScreen.flip_gravity,
                    "text_size": int(SIZE.w / 45),
                    "text_font": FONT
                },
                function=flip_gravity
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=SIZE // (11.9, 15.65),
                size=SIZE // (7, 14.4),
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.InGameScreen.retry,
                    "text_size": int(SIZE.w / 45),
                    "text_font": FONT
                },
                function=reset_players
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=SIZE // (5, 15.65),
                size=CHECKBOX_SIZE,
                tn=DEL_ICON,
                sound=BUTTON_CLICK,
                function=set_layout,
                fargs=[LayoutTypes.CONFIRM_DELETION]
            )
        ),
        others=()
    ),
    LayoutTypes.NEXT_LEVEL: Layout(
        buttons=[
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=SIZE // (15.06, 18),
                size=SIZE // (9.84, 18),
                tn=BACK_BUTTON,
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.NextLevel.back,
                    "text_size": int(SIZE.w // 51.2),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.LEVEL_SELECT]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / 8),
                size=SIZE // (5, 9),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.NextLevel.next_level,
                    "text_size": int(SIZE.w / 28),
                    "text_font": FONT
                },
                function=set_level
            )
        ],
        others=[
            ga.Element(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                texture=next_level_bg.convert_alpha(),
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -7.2),
                text=LANG.NextLevel.level_completed,
                text_size=int(SIZE.w / 25.6),
                text_font=FONT
            )
        ],
        buttons_first=False
    ),
    LayoutTypes.EDITOR: Layout(
        buttons=[
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=ga.Pos(PIXEL) * 22,
                size=CONTROL_BUTTON_SIZE,
                tn=BACK2_ICON,
                sound=BUTTON_CLICK,
                function=set_layout,
                fargs=[LayoutTypes.PLAY_SCREEN]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=ga.Pos(PIXEL) * (60, 22),
                size=CONTROL_BUTTON_SIZE,
                tn=SAVE_ICON,
                sound=BUTTON_CLICK,
                function=save_level
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=ga.Pos(PIXEL) * (90, 22),
                size=CONTROL_BUTTON_SIZE,
                tn=OPEN_ICON,
                sound=BUTTON_CLICK,
                function=open_level
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=ga.Pos(PIXEL) * (120, 22),
                size=CONTROL_BUTTON_SIZE,
                tn=NEW_ICON,
                sound=BUTTON_CLICK,
                function=set_layout,
                fargs=[LayoutTypes.NEW_LEVEL]
            ),
            # NewButton(
            #     parent=SCREEN_E,
            #     c_anchor=ga.AncType.UL,
            #     offset=ga.Pos(PIXEL) * (155, 22),
            #     size=CONTROL_BUTTON_SIZE,
            #     tn=THUMBNAIL_ICON,
            #     sound=BUTTON_CLICK,
            #     function=add_image
            # ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=ga.Pos(PIXEL) * (160, 22),
                size=CONTROL_BUTTON_SIZE,
                tn=UNDO_ICON,
                sound=BUTTON_CLICK,
                function=undo
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=ga.Pos(PIXEL) * (190, 22),
                size=CONTROL_BUTTON_SIZE,
                tn=REDO_ICON,
                sound=BUTTON_CLICK,
                function=redo
            )
        ],
        others=[
            Page(
                pages=(
                (ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UC,
                    offset=SIZE // (6, 28),
                    text=LANG.Editor.layer.format(layer_no=1),
                    text_size=int(SIZE.w // 40),
                    text_font=FONT
                ),),
                (ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UC,
                    offset=SIZE // (6, 28),
                    text=LANG.Editor.layer.format(layer_no=2),
                    text_size=int(SIZE.w // 40),
                    text_font=FONT
                ),),
                (ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UC,
                    offset=SIZE // (6, 28),
                    text=LANG.Editor.layer.format(layer_no=3),
                    text_size=int(SIZE.w // 40),
                    text_font=FONT
                ),),
                (ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UC,
                    offset=SIZE // (6, 28),
                    text=LANG.Editor.layer.format(layer_no=4),
                    text_size=int(SIZE.w // 40),
                    text_font=FONT
                ),),
                (ga.Label(
                    parent=SCREEN_E,
                    anchor=ga.AncType.UC,
                    offset=SIZE // (6, 28),
                    text=LANG.Editor.layer.format(layer_no=5),
                    text_size=int(SIZE.w // 40),
                    text_font=FONT
                ),)),
                next_page_button=NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.UC,
                    offset=SIZE // (7, 11),
                    size=min(SIZE.h, SIZE.w) // 23,
                    sound=BUTTON_CLICK,
                    tn=DOWN_ARROW
                ),
                prev_page_button=NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.UC,
                    offset=SIZE // (7, 28),
                    size=min(SIZE.h, SIZE.w) // 23,
                    sound=BUTTON_CLICK,
                    tn=UP_ARROW
                ),
                starting_page=4
            ),
            Page(
                pages=[
                    [
                    Page(
                        pages=[[BlockElement(
                            parent=SCREEN_E,
                            anchor=ga.AncType.UC,
                            offset=SIZE // (2.9, 50),
                            texture=NO_BLOCK,
                            id_=0
                        )]]
                    )
                    ],
                    [Page(pages=[], loop_back=True)],
                    [Page(pages=[], loop_back=True)],
                    [Page(pages=[], loop_back=True)]
                ],
                next_page_button=NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.UC,
                    offset=SIZE // (3.15, 11),
                    size=min(SIZE.h, SIZE.w) // 23,
                    sound=BUTTON_CLICK,
                    tn=DOWN_ARROW
                ),
                prev_page_button=NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.UC,
                    offset=SIZE // (3.15, 28),
                    size=min(SIZE.h, SIZE.w) // 23,
                    sound=BUTTON_CLICK,
                    tn=UP_ARROW
                )
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UC,
                offset=SIZE // (-38, 16),
                text=LANG.Editor.no_level,
                text_size=int(SIZE.w // 40),
                text_font=FONT
            ),
            ga.Element(
                pos=-TILE_SIZE * 3,
                size=TILE_SIZE,
                texture=BLOCK_SELECTED,
                pos_ani={
                    "move": {
                        "frames": {
                            "function": lambda x: x + (ga.Pos(-TILE_SIZE * 2) - x) / 3,
                            "frames": 1
                        },
                        "time":0.01,
                        "loop": True,
                        "change_end": True
                    }
                }
            )
        ]
    ),
    LayoutTypes.NEW_LEVEL: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=SIZE // (8, 8),
                size=SIZE // (7, 13),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.ok,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=create_level,
                fargs=[False]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=SIZE // (-8, 8),
                size=SIZE // (7, 13),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.cancel,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.EDITOR]
            ),
            TextLabel(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                size=SIZE // (2.3, 18),
                offset=(0, SIZE.h // -40),
                sh_m=1,
                sc_m=1,
                ch=(10, 158, 255),
                cc=(33, 166, 255),
                halo_cn=ga.GRAY(40),
                halo_ch=(10, 158, 255),
                halo_cc=ga.WHITE,
                edge=SIZE.w // 427,
                edge_ch=(10, 158, 255),
                edge_cc=ga.WHITE,
                text_kwargs={
                    "text": "",
                    "text_size": int(SIZE.w // 51.2),
                    "text_font": FONT
                }
            )
        ),
        others=(
            ga.Element(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                texture=next_level_bg.convert_alpha(),
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -7.2),
                text="Insert level name:",
                text_size=int(SIZE.w / 35),
                text_font=FONT
            )
        ),
        buttons_first=False
    ),
    LayoutTypes.OVERWRITE: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=SIZE // (8, 8),
                size=SIZE // (7, 13),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.yes,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=create_level,
                fargs=[True]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=SIZE // (-8, 8),
                size=SIZE // (7, 13),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.no,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.NEW_LEVEL]
            )
        ),
        others=(
            ga.Element(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                texture=next_level_bg.convert_alpha(),
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -7.2),
                text=LANG.Editor.overwrite.split("\n")[0],
                text_size=int(SIZE.w / 35),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -15),
                text=LANG.Editor.overwrite.split("\n")[1],
                text_size=int(SIZE.w / 35),
                text_font=FONT
            )
        ),
        buttons_first=False
    ),
    LayoutTypes.FAILED_OPENING: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / 8),
                size=SIZE // (5, 9),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.ok,
                    "text_size": int(SIZE.w / 28),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.EDITOR]
            ),
        ),
        others=(
            ga.Element(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                texture=next_level_bg.convert_alpha(),
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -7.2),
                text=LANG.Editor.failed_opening,
                text_size=int(SIZE.w / 35),
                text_font=FONT
            )
        ),
        buttons_first=False
    ),
    LayoutTypes.LEVEL_SELECT: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=SIZE // (15.06, 18),
                size=SIZE // (9.84, 18),
                tn=BACK_BUTTON,
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.LevelSelection.back,
                    "text_size": int(SIZE.w // 51.2),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.PLAY_SCREEN]
            ),
        ),
        others=(
            Page(
                pages=[[]],
                next_page_button=NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.CR,
                    offset=(-SIZE.w // 25, 0),
                    size=CHECKBOX_SIZE,
                    tn=RIGHT_ARROW,
                    sound=BUTTON_CLICK
                ),
                prev_page_button=NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.CL,
                    offset=(SIZE.w // 25, 0),
                    size=CHECKBOX_SIZE,
                    tn=LEFT_ARROW,
                    sound=BUTTON_CLICK
                )
            ),
        )
    ),
    LayoutTypes.END_SCREEN: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h // 18),
                size=SIZE // (3, 13),
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.EndScreen.back_to_levels,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.LEVEL_SELECT]
            ),
        ),
        others=(
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h // -18),
                text=LANG.EndScreen.congrats,
                text_size=int(SIZE.w // 35),
                text_font=FONT
            ),
        )
    ),
    LayoutTypes.FAILED_TRASH: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=SIZE // (8, 8),
                size=SIZE // (7, 13),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.yes,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=delete_level,
                fargs=[True]
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=SIZE // (-8, 8),
                size=SIZE // (7, 13),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.no,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.IN_GAME_CUSTOM]
            )
        ),
        others=(
            ga.Element(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                texture=next_level_bg.convert_alpha(),
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -6),
                text=LANG.Editor.failed_trash.split("\n")[0],
                text_size=int(SIZE.w / 35),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -10),
                text=LANG.Editor.failed_trash.split("\n")[1],
                text_size=int(SIZE.w / 35),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -30),
                text=LANG.Editor.failed_trash.split("\n")[2],
                text_size=int(SIZE.w / 35),
                text_font=FONT
            )
        ),
        buttons_first=False
    ),
    LayoutTypes.FAILED_DELETION: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / 8),
                size=SIZE // (5, 9),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.ok,
                    "text_size": int(SIZE.w / 28),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.IN_GAME_CUSTOM]
            ),
        ),
        others=(
            ga.Element(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                texture=next_level_bg.convert_alpha(),
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -7.2),
                text=LANG.Editor.failed_deletion,
                text_size=int(SIZE.w / 35),
                text_font=FONT
            )
        ),
        buttons_first=False
    ),
    LayoutTypes.CONFIRM_DELETION: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=SIZE // (8, 8),
                size=SIZE // (7, 13),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.yes,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=delete_level
            ),
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=SIZE // (-8, 8),
                size=SIZE // (7, 13),
                sound=BUTTON_CLICK,
                halo_cn=ga.GRAY(40),
                text_kwargs={
                    "text": LANG.General.no,
                    "text_size": int(SIZE.w // 40),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.IN_GAME_CUSTOM]
            )
        ),
        others=(
            ga.Element(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                texture=next_level_bg.convert_alpha(),
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -7.2),
                text=LANG.Editor.confirm_deletion.split("\n")[0],
                text_size=int(SIZE.w / 35),
                text_font=FONT
            ),
            ga.Label(
                parent=SCREEN_E,
                c_anchor=ga.AncType.CC,
                offset=(0, SIZE.h / -15),
                text=LANG.Editor.confirm_deletion.split("\n")[1],
                text_size=int(SIZE.w / 35),
                text_font=FONT
            )
        ),
        buttons_first=False
    ),
    LayoutTypes.HELP_SCREEN: Layout(
        buttons=(
            NewButton(
                parent=SCREEN_E,
                c_anchor=ga.AncType.UL,
                offset=SIZE // (15.06, 18),
                size=SIZE // (9.84, 18),
                tn=BACK_BUTTON,
                sound=BUTTON_CLICK,
                text_kwargs={
                    "text": LANG.LevelSelection.back,
                    "text_size": int(SIZE.w // 51.2),
                    "text_font": FONT
                },
                function=set_layout,
                fargs=[LayoutTypes.PLAY_SCREEN]
            ),
        ),
        others=(Page(
            pages=[
                [
                    ga.Label(
                        parent=SCREEN_E,
                        c_anchor=ga.AncType.UC,
                        offset=(0, SIZE.h // 12),
                        text=LANG.HelpScreen.controls,
                        text_size=int(SIZE.w // 25),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 90),
                        text=LANG.HelpScreen.movement.split("\n")[0],
                        text_size=int(SIZE.w // 35),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 120),
                        text=LANG.HelpScreen.movement.split("\n")[1],
                        text_size=int(SIZE.w // 35),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 150),
                        text=LANG.HelpScreen.movement.split("\n")[2],
                        text_size=int(SIZE.w // 35),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 180),
                        text=LANG.HelpScreen.movement.split("\n")[3],
                        text_size=int(SIZE.w // 35),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 210),
                        text=LANG.HelpScreen.movement.split("\n")[4],
                        text_size=int(SIZE.w // 35),
                        text_font=FONT
                    )
                ],
                [
                    ga.Label(
                        parent=SCREEN_E,
                        c_anchor=ga.AncType.UC,
                        offset=(0, SIZE.h // 12),
                        text=LANG.HelpScreen.editor,
                        text_size=int(SIZE.w // 25),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 70),
                        text=LANG.HelpScreen.Editor.layers.split("\n")[0],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 90),
                        text=LANG.HelpScreen.Editor.layers.split("\n")[1],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 120),
                        text=LANG.HelpScreen.Editor.block.split("\n")[0],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 140),
                        text=LANG.HelpScreen.Editor.block.split("\n")[1],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 160),
                        text=LANG.HelpScreen.Editor.block.split("\n")[2],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 190),
                        text=LANG.HelpScreen.Editor.move_door.split("\n")[0],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 210),
                        text=LANG.HelpScreen.Editor.move_door.split("\n")[1],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 230),
                        text=LANG.HelpScreen.Editor.move_player.split("\n")[0],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 260),
                        text=LANG.HelpScreen.Editor.move_player.split("\n")[1],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 280),
                        text=LANG.HelpScreen.Editor.move_player.split("\n")[2],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    ),
                    ga.Label(
                        parent=SCREEN_E,
                        anchor=ga.AncType.UL,
                        offset=ga.Pos(PIXEL) * (90, 300),
                        text=LANG.HelpScreen.Editor.move_player.split("\n")[3],
                        text_size=int(SIZE.w // 45),
                        text_font=FONT
                    )
                ]
            ],
            next_page_button=NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.CR,
                    offset=(-SIZE.w // 25, 0),
                    size=CHECKBOX_SIZE,
                    tn=RIGHT_ARROW,
                    sound=BUTTON_CLICK
                ),
            prev_page_button=NewButton(
                    parent=SCREEN_E,
                    c_anchor=ga.AncType.CL,
                    offset=(SIZE.w // 25, 0),
                    size=CHECKBOX_SIZE,
                    tn=LEFT_ARROW,
                    sound=BUTTON_CLICK
                )
        ),)
    )
}

gen_level_buttons()
gen_block_pages()

music_slider        = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][6]
sfx_slider          = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][7]
music_perc          = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][8]
sfx_perc            = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][9]
fullscreen_checkbox = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][0]
fullscreen_state    = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][12]
screen_res_state    = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][13]
show_fps            = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][3]
show_fps_state      = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][14]
current_lang        = GAME_LAYOUTS[LayoutTypes.SETTINGS].others[0].pages[0][17]
new_level_text      = GAME_LAYOUTS[LayoutTypes.NEW_LEVEL][-1]
current_level_name  = GAME_LAYOUTS[LayoutTypes.EDITOR].others[2]
block_outline       = GAME_LAYOUTS[LayoutTypes.EDITOR].others[3]
block_outline.move.start()
block_outline.hide = True
pygame.mixer.music.set_volume(music_slider.value)
sound_effects = [BUTTON_CLICK, DEATH, SWITCH_GRAV]

current_layer_shown = 5
can_drag_door = False
is_dragging_door = False
door_info = ["left", (0, 0)]
prev_info = []

for i in sound_effects: i.set_volume(sfx_slider.value)

frame = 0
percentage = lambda: (int(degrees(cos(frame/100)))/2 + 57) / 114 + 0.25
bg_speed = 0.03

comet_latency = random.random() + 1
last_comet = time.time()

comets = []

fps_label = ga.StaticLabel(
    text="0",
    parent=SCREEN_E,
    anchor=ga.AncType.DL,
    offset=SIZE // (256, -27.69),
    text_size=int(SIZE.w / 64),
    text_font=FONT
)

update_settings_label = ga.StaticLabel(
    parent=SCREEN_E,
    c_anchor=ga.AncType.DC,
    offset=(0, -SIZE.h // 20),
    text=LANG.Settings.restart_to_apply,
    text_size=int(SIZE.w // 40),
    text_font=FONT
)

fps = 0
last_check = time.time()

if len(sys.argv) == 2 and open_level(sys.argv[1]):
    set_layout(LayoutTypes.EDITOR)

while True:
    alpha_time = clock.tick()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            stop_game()

        elif e.type == pygame.KEYDOWN:
            if new_level_text.typing:
                new_level_text.type(e)
            if e.key == pygame.K_r and current_layout in (LayoutTypes.IN_GAME,
                                                          LayoutTypes.EDITOR,
                                                          LayoutTypes.IN_GAME_CUSTOM):
                reset_players()
                if current_layout == LayoutTypes.EDITOR:
                    player1.locked = False
                    player2.locked = False

            elif e.key in (pygame.K_g, pygame.K_DOWN, pygame.K_s) and \
               current_layout in (LayoutTypes.IN_GAME, LayoutTypes.EDITOR, LayoutTypes.IN_GAME_CUSTOM):
                flip_gravity()

            elif e.key == pygame.K_RETURN:
                if current_layout == LayoutTypes.NEXT_LEVEL:
                    GAME_LAYOUTS[current_layout][3].run()
                elif current_layout == LayoutTypes.CREDITS:
                    GAME_LAYOUTS[current_layout][0].run()
                elif current_layout == LayoutTypes.END_SCREEN:
                    GAME_LAYOUTS[current_layout][0].run()

            elif e.key == pygame.K_F6 and current_layout == LayoutTypes.IN_GAME:
                reload_level(f"{LOCAL_DIR}/assets/levels/level{current_level}.json", current_level)
                from level import levels
                player1.level = levels[current_level][0]
                player2.level = levels[current_level][1]

            elif e.key == pygame.K_F2:
                screen.fill(ga.P(bg_color, percentage()))

            elif e.key == pygame.K_F1:
                settings["show_hitboxes"] = not settings["show_hitboxes"]
                update_settings_file()

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == pygame.BUTTON_LEFT:
            if current_editor_level is None or get_tile_pos() is None or current_layout != LayoutTypes.EDITOR:
                continue

            tile_pos = get_tile_pos()
            door_pos = ga.Pos(current_editor_level[0].data[f"door_pos_{tile_pos[0]}"])
            if door_pos - 1 < tile_pos[1] < door_pos + (4, 3) and not (player1.hovered or player2.hovered):
                can_drag_door = True
                door_info = [tile_pos[0], tile_pos[1] - door_pos]

        elif e.type == pygame.MOUSEBUTTONUP and e.button == pygame.BUTTON_LEFT:
            prev_info = []
            if ignore_button_up:
                ignore_button_up = False
                continue
            if current_layout == LayoutTypes.NEW_LEVEL:
                if not new_level_text.hovered:
                    new_level_text.typing = False
                new_level_text.update_text()
            elif current_layout == LayoutTypes.EDITOR:
                if is_dragging_door:
                    is_dragging_door = False
                    can_drag_door = False
                    continue
                elif player1.dragging or player2.dragging: continue
                can_drag_door = False
                info = get_tile_pos()
                if info is not None:
                    set_level_tile(*info)

        elif e.type == pygame.MOUSEMOTION:
            if not pygame.mouse.get_pressed()[0]: continue
            if current_layout != LayoutTypes.EDITOR or current_editor_level is None:
                continue
            if can_drag_door and not is_dragging_door:
                is_dragging_door = True
            elif is_dragging_door:
                change_door_pos()
            elif player1.dragging:
                player1.speed = ga.Pos(e.rel) * (5, 1.5)
            elif player2.dragging:
                player2.speed = ga.Pos(e.rel) * (5, 1.5)
            else:
                info = get_tile_pos()
                if info is None or current_editor_level is None: continue
                door_pos = ga.Pos(current_editor_level[0].data[f"door_pos_{info[0]}"])
                if door_pos - 1 < info[1] < door_pos + (4, 3): continue
                if info != prev_info:
                    set_level_tile(*info)
                    prev_info = info

        elif e.type == pygame.MOUSEWHEEL and current_layout == LayoutTypes.EDITOR:
            block_selector = GAME_LAYOUTS[LayoutTypes.EDITOR].others[1]
            block_group = block_selector.pages[block_selector.current_page][0]
            block_element = block_group.pages[block_group.current_page][0]
            if block_element._lu < pygame.mouse.get_pos() < block_element._rd:
                if e.y + 1:
                    block_group.prev_page()
                else:
                    block_group.next_page()

    if not pygame.mixer.music.get_busy():
        track = (track + 1) % len(SOUND_TRACKS)
        pygame.mixer.music.load(SOUND_TRACKS[track])
        pygame.mixer.music.play(fade_ms=2000)

    screen.fill(ga.P(bg_color, percentage()))
    # screen.fill(bg_color)

    for star, pos in zip(stars, stars_pos): screen.blit(star, pos)

    if time.time() - last_comet >= comet_latency:
        for i in comets: del i
        comets.clear()
        for i in range(random.randint(1, 4)):
            comets.append(get_comet())
            comets[i - 1].slide.start()

        last_comet = time.time()
        comet_latency = random.random() + 1

    for i in comets: i.render(screen)

    if time.time() - fading_start <= FADE_SPEED * 30:
        for i in GAME_LAYOUTS[fading_layout]: i.render(screen)
    else:
        for i in GAME_LAYOUTS[current_layout]:
            if isinstance(i, ga.Slider):
                i._bar.transparency = 255
                i._button.transparency = 255
                i._bar.visible = True
                i._button.visible = True
            else:
                i.transparency = 255
                i.visible = True

    if current_layout in (LayoutTypes.IN_GAME, LayoutTypes.NEXT_LEVEL, LayoutTypes.IN_GAME_CUSTOM,
                          LayoutTypes.CONFIRM_DELETION, LayoutTypes.FAILED_TRASH,
                          LayoutTypes.FAILED_DELETION):
        level1 = current_playing_level[0]
        level2 = current_playing_level[1]
        screen.blit(level1.texture, level1.offset)
        screen.blit(level2.texture, level2.offset)
        level1.door.render(screen)
        level2.door.render(screen)
        if current_layout in (LayoutTypes.IN_GAME, LayoutTypes.IN_GAME_CUSTOM, LayoutTypes.NEXT_LEVEL):
            player1.render(screen, pos=ga.Pos(player1.rect.topleft))
            player2.render(screen, pos=ga.Pos(player2.rect.topleft))

        if settings["show_hitboxes"]:
            for i in level1.solid:
                for j in i: pygame.draw.rect(screen, ga.CYAN, j.rect, 1)
            for i in level1.damaging:
                for j in i: pygame.draw.rect(screen, ga.RED, j.rect, 1)
            for i in level2.solid:
                for j in i: pygame.draw.rect(screen, ga.CYAN, j.rect, 1)
            for i in level2.damaging:
                for j in i: pygame.draw.rect(screen, ga.RED, j.rect, 1)
            pygame.draw.rect(screen, ga.BLUE, level1.door.rect, 1)
            pygame.draw.rect(screen, ga.BLUE, level2.door.rect, 1)
            if current_layout in (LayoutTypes.IN_GAME, LayoutTypes.IN_GAME_CUSTOM):
                pygame.draw.rect(screen, ga.CYAN, player1.rect, 1)
                pygame.draw.rect(screen, ga.CYAN, player2.rect, 1)
                pygame.draw.rect(screen, ga.RED, player1.damage_hitbox.rect, 1)
                pygame.draw.rect(screen, ga.RED, player2.damage_hitbox.rect, 1)
                pygame.draw.aaline(screen, ga.YELLOW, player1._c, player1._c + player1.speed * 2)
                pygame.draw.aaline(screen, ga.YELLOW, player2._c, player2._c + player2.speed * 2)

        if player1.colliding(level1.door) \
           and not level2.door.opened \
           and not player1.dead:
            level2.door.open.start()
        elif not player1.colliding(level1.door) and level2.door.opened:
            level2.door.close.start()

        if player2.colliding(level2.door) \
           and not level1.door.opened \
           and not player2.dead:
            level1.door.open.start()
        elif not player2.colliding(level2.door) and level1.door.opened:
            level1.door.close.start()

        if level1.door.opened and level2.door.opened:
            player1.enter_door()
            player2.enter_door()
            if current_layout != LayoutTypes.NEXT_LEVEL:
                set_layout(LayoutTypes.NEXT_LEVEL)
                # if the next level is locked and there are more levels
                if current_level == settings["last_level"] and settings["last_level"] + 1 != len(levels):
                    change_allowed_levels()

    elif current_layout in (LayoutTypes.EDITOR, LayoutTypes.FAILED_OPENING, LayoutTypes.NEW_LEVEL):
        if current_editor_level is None:
            screen.blit(dummy_editor_level[0].texture, dummy_editor_level[0].offset)
            screen.blit(dummy_editor_level[1].texture, dummy_editor_level[1].offset)
            dummy_editor_level[0].door.render(screen)
            dummy_editor_level[1].door.render(screen)
            if current_level_name._text != LANG.Editor.no_level:
                current_level_name.change_text(LANG.Editor.no_level)

        else:
            screen.blit(current_editor_level[0].texture, current_editor_level[0].offset)
            screen.blit(current_editor_level[1].texture, current_editor_level[1].offset)
            current_editor_level[0].door.render(screen)
            current_editor_level[1].door.render(screen)
            if current_layer_shown != GAME_LAYOUTS[LayoutTypes.EDITOR].others[0].current_page + 1:
                current_layer_shown = GAME_LAYOUTS[LayoutTypes.EDITOR].others[0].current_page + 1
                current_editor_level[0].gen_texture(current_layer_shown)
                current_editor_level[1].gen_texture(current_layer_shown)

            if settings["show_hitboxes"]:
                for i in current_editor_level[0].solid:
                    for j in i: pygame.draw.rect(screen, ga.CYAN, j.rect, 1)
                for i in current_editor_level[0].damaging:
                    for j in i: pygame.draw.rect(screen, ga.RED, j.rect, 1)
                for i in current_editor_level[1].solid:
                    for j in i: pygame.draw.rect(screen, ga.CYAN, j.rect, 1)
                for i in current_editor_level[1].damaging:
                    for j in i: pygame.draw.rect(screen, ga.RED, j.rect, 1)
                pygame.draw.rect(screen, ga.BLUE, current_editor_level[0].door.rect, 1)
                pygame.draw.rect(screen, ga.BLUE, current_editor_level[1].door.rect, 1)

            if current_layout == LayoutTypes.EDITOR:
                player1.render(screen, pos=ga.Pos(player1.rect.topleft))
                player2.render(screen, pos=ga.Pos(player2.rect.topleft))
                if settings["show_hitboxes"]:
                    pygame.draw.rect(screen, ga.CYAN, player1.rect, 1)
                    pygame.draw.rect(screen, ga.CYAN, player2.rect, 1)
                    pygame.draw.rect(screen, ga.RED, player1.damage_hitbox.rect, 1)
                    pygame.draw.rect(screen, ga.RED, player2.damage_hitbox.rect, 1)
                    pygame.draw.aaline(screen, ga.YELLOW, player1._c, player1._c + player1.speed * 2)
                    pygame.draw.aaline(screen, ga.YELLOW, player2._c, player2._c + player2.speed * 2)

                current_editor_level[0].player_starting_pos = player1.pos
                player_pixel_pos = (player1.pos - current_editor_level[0].offset) / PIXEL
                current_editor_level[0].data["player_starting_pos_left"] = player_pixel_pos.list()
                current_editor_level[1].player_starting_pos = player2.pos
                player_pixel_pos = (player2.pos - current_editor_level[1].offset) / PIXEL
                current_editor_level[0].data["player_starting_pos_right"] = player_pixel_pos.list()

                if current_level_name._text != current_editor_level[0].name:
                    current_level_name.change_text(current_editor_level[0].name)

                current_pos = get_tile_pos()
                if current_pos is None or player1.dragging or player1.dragging or player1.hovered or player2.hovered:
                    block_outline.pos = -TILE_SIZE * 2
                    block_outline.hide = True
                    block_outline.move._finish_end()
                else:
                    offset = LEVEL_OFFSET_LEFT if current_pos[0] == "left" else LEVEL_OFFSET_RIGHT
                    pos = current_pos[1] * TILE_SIZE + offset
                    if block_outline.hide:
                        block_outline.pos = pos
                        block_outline.hide = False
                        block_outline.move.start()
                    else:
                        block_outline.move.frames = {
                            "function": lambda x: x + (ga.Pos(pos) - x) / 2,
                            "frames": 1
                        }

    elif current_layout == LayoutTypes.SETTINGS:
        settings["music_volume"] = music_slider.value
        settings["sfx_volume"]   = sfx_slider.value
        settings["fullscreen"]   = fullscreen_checkbox.value
        settings["language"]     = LANGS[current_lang_idx]
        settings["show_fps"]     = show_fps.value
        if ALLOWED_SCREEN_RES[current_res_idx] != ["NaN ", " NaN"]:
            settings["screen_res"] = ALLOWED_SCREEN_RES[current_res_idx]
        pygame.mixer.music.set_volume(music_slider.value)
        for i in sound_effects: i.set_volume(sfx_slider.value)
        music_perc.change_text(f"{round(music_slider.value * 100)}%")
        sfx_perc.change_text(f"{round(sfx_slider.value * 100)}%")
        fullscreen_state.change_text(LANG.Settings.fullscreen.format(state=LANG.General.yes if settings["fullscreen"] else LANG.General.no))
        show_fps_state.change_text(LANG.Settings.show_fps.format(state=LANG.General.yes if settings["show_fps"] else LANG.General.no))
        screen_res_state.change_text(f"{ALLOWED_SCREEN_RES[current_res_idx][0]}x{ALLOWED_SCREEN_RES[current_res_idx][1]}")
        current_lang.change_text(LANG_NAMES[settings["language"]])
        screen_res_state._color = ga.GRAY(150) if settings["fullscreen"] else ga.WHITE

    if current_layout == LayoutTypes.NEXT_LEVEL and not GAME_LAYOUTS[current_layout][3]._fargs:
        if current_level == custom_levels_start - 1:
            GAME_LAYOUTS[current_layout][3]._fargs = [len(levels)]
        else:
            GAME_LAYOUTS[current_layout][3]._fargs = [current_level + 1]

    for i in GAME_LAYOUTS[current_layout]: i.render(screen)

    if current_layout == LayoutTypes.SETTINGS and \
       (settings["screen_res"], settings["fullscreen"], settings["language"]) != starting_settings:
            if settings["language"] != starting_settings[2] or \
               settings["fullscreen"] != starting_settings[1] or \
               settings["screen_res"] != starting_settings[0] and not settings["fullscreen"]:
                update_settings_label.render(screen)

    fps += 1
    if time.time() - last_check >= 1:
        fps_label.change_text(str(fps))
        fps = 0
        last_check = time.time()
    if settings["show_fps"]:
        fps_label.render(screen)

    if use_control_buttons:
        close_button.render(screen)
        close_button.auto_run()
        minimize_button.render(screen)
        minimize_button.auto_run()

    pygame.display.update()

    frame = (frame + bg_speed * alpha_time) % 627
