import random
import json
import sys
import os

import pyautogui

import pygame
import gameassets as ga
import lang

pygame.init()
random.seed(11)

if "\\" in sys.argv[0]:
    LOCAL_DIR = "\\".join(sys.argv[0].split("\\")[:-1])
else:
    LOCAL_DIR = "/".join(sys.argv[0].split("/")[:-1])

SETTINGS_PATH = f"{os.getenv('APPDATA')}/astronauts/player_data/settings.json"

try:
    with open(SETTINGS_PATH, "r") as settings_file:
        settings = json.load(settings_file)
except Exception:
    __settings = '{"last_level": 0, "fullscreen": true, "screen_res": [1280, 720],'\
                 '"language": "EN", "music_volume": 1.0, "sfx_volume": 1.0,'\
                 '"show_hitboxes": false, "show_fps": false}'

    if not os.path.isdir(f"{os.getenv('APPDATA')}/astronauts"):
        os.mkdir(f"{os.getenv('APPDATA')}/astronauts")
    if not os.path.isdir(f"{os.getenv('APPDATA')}/astronauts/player_data"):
        os.mkdir(f"{os.getenv('APPDATA')}/astronauts/player_data")
    with open(SETTINGS_PATH, "w") as settings_file:
        settings_file.write(__settings)
    settings = json.loads(__settings)

# ==================== CONSTANTS ====================

SCREEN_WIDTH = pyautogui.size().width
SCREEN_HEIGHT = pyautogui.size().height

SCREEN_RES = [
    [640, 360], [640, 480], [800, 600], [1024, 768], [1152, 864], [1176, 664],
    [1280, 720], [1280, 768], [1280, 800], [1280, 960], [1280, 1024],
    [1360, 768], [1366, 768], [1400, 1050], [1440, 900], [1600, 900],
    [1600, 1024], [1680, 1050], [1768, 992], [1920, 1080]
]

ALLOWED_SCREEN_RES = [i for i in SCREEN_RES if i[0] < SCREEN_WIDTH and i[1] < SCREEN_HEIGHT]

if settings["fullscreen"] or not ALLOWED_SCREEN_RES:
    SIZE = ga.Size(pyautogui.size().width, pyautogui.size().height)
else:
    SIZE = ga.Size(settings["screen_res"])

with open(f"{LOCAL_DIR}/assets/langs/lang_acronyms.json", "r") as json_lang_info:
    lang_info = json.load(json_lang_info)

LANG = lang.load_txt(settings["language"], f"{LOCAL_DIR}/assets/langs")
LANGS = lang_info["list"]
LANG_NAMES = lang_info["associations"]

with open(f"{LOCAL_DIR}/assets/levels/levels.json") as levels_list_file:
    LEVELS_LIST = json.load(levels_list_file)

LOCKED_LEVELS = [f"{LOCAL_DIR}/assets/levels/{i}" for i in LEVELS_LIST["normal"]]
LOCKED_LEVELS.append(f"{LOCAL_DIR}/assets/levels/new_level_default.level")

if not ALLOWED_SCREEN_RES: ALLOWED_SCREEN_RES.append(["NaN ", " NaN"])

TILE_SIZE = ga.IntSize(round(SIZE.w / 40))
PIXEL = SIZE.w / 640
PER_TILE_ERROR = SIZE.w / 40 - round(SIZE.w / 40)
LEVEL_SIZE = ga.Size(TILE_SIZE * 19)

LEVEL_OFFSET_LEFT = (SIZE // (2, 7.65) - (LEVEL_SIZE.w, 0)) * (0.5, 1)
LEVEL_OFFSET_RIGHT = SIZE // (2, 7.65) + ((SIZE.w // 2 - LEVEL_SIZE.w) / 2, 0)

SCREEN_E = ga.StaticElement(pos=(0, 0), size=SIZE)

COMET_TEXTURE = pygame.image.load(f"{LOCAL_DIR}/assets/textures/background/comet.png")

FONT = f"{LOCAL_DIR}/assets/font/regular.ttf"

BUTTON_CN = (0, 180, 255)
BUTTON_CH = (0, 200, 255)
BUTTON_CC = (0, 170, 255)

HALO = SIZE.w / 110 if SIZE.w > SIZE.h else SIZE.h // 60
BUTTON_CURVE = SIZE.h // 100 if SIZE.h < SIZE.w else SIZE.w // 178

NEXT_LEVEL_BG_COLOR = (60, 62, 68)

BUTTON_OFFSET = [
    [SIZE // (5, 4)   , SIZE // (2.5, 4)   , SIZE // (-2.5, 4)   , SIZE // (-5, 4)   ],
    [SIZE // (5, 30)  , SIZE // (2.5, 30)  , SIZE // (-2.5, 30)  , SIZE // (-5, 30)  ],
    [SIZE // (5, -5.5), SIZE // (2.5, -5.5), SIZE // (-2.5, -5.5), SIZE // (-5, -5.5)]
]

BUTTON_ANCHOR = [
    [ga.AncType.UL, ga.AncType.UL, ga.AncType.UR, ga.AncType.UR],
    [ga.AncType.CL, ga.AncType.CL, ga.AncType.CR, ga.AncType.CR],
    [ga.AncType.DL, ga.AncType.DL, ga.AncType.DR, ga.AncType.DR]
]

CHECKBOX_SIZE = ga.Size(min(SIZE.h, SIZE.w) // 11)
CONTROL_BUTTON_SIZE = ga.Size(min(SIZE.h, SIZE.w) // 15)

BAR_CN = ga.GRAY(220)
BAR_CH = ga.WHITE
BAR_CC = ga.GRAY(235)

FADE_SPEED = 0.01

FADE_IN = {
    "name": "fade_in",
    "frames": {
        "function": lambda x: x + 10,
        "frames": 27
    },
    "change_end": True,
    "time": FADE_SPEED / 2,
    "starting_val": 0
}

FADE_OUT = {
    "name": "fade_out",
    "frames": {
        "function": lambda x: x - 10,
        "frames": 27
    },
    "change_end": True,
    "time": FADE_SPEED / 2,
    "starting_val": 255
}

SOUND_TRACKS = [
    f"{LOCAL_DIR}/assets/music/space_vacuum_a_cinematic_journey.mp3",
    f"{LOCAL_DIR}/assets/music/deep_space_9.mp3",
    f"{LOCAL_DIR}/assets/music/universe_space_sounds.mp3",
    f"{LOCAL_DIR}/assets/music/cosmic_glow.mp3",
    f"{LOCAL_DIR}/assets/music/the_death_of_a_supernova.mp3"
]


class LayoutTypes:
    NO_LAYOUT = -1
    PLAY_SCREEN = 0
    CREDITS = 1
    IN_GAME = 2
    NEXT_LEVEL = 3
    EDITOR = 4
    SETTINGS = 5
    LEVEL_SELECT = 6
    FAILED_OPENING = 7
    NEW_LEVEL = 8
    OVERWRITE = 9
    END_SCREEN = 10
    IN_GAME_CUSTOM = 11
    FAILED_TRASH = 12
    FAILED_DELETION = 13
    CONFIRM_DELETION = 14
    HELP_SCREEN = 15


LAYOUT_NAMES = {
    LayoutTypes.NO_LAYOUT: "Astronauts!",
    LayoutTypes.PLAY_SCREEN: "Shouldn't you be studying?",
    LayoutTypes.IN_GAME: "Press F1 to see the hitboxes!",
    LayoutTypes.IN_GAME_CUSTOM: "Press F1 to see the hitboxes!",
    LayoutTypes.NEXT_LEVEL: "Good job!",
    LayoutTypes.CREDITS: "You did it! And hi, I made this game :)",
    LayoutTypes.SETTINGS: "Looks like you want to change ...",
    LayoutTypes.LEVEL_SELECT: "What a hard choise...",
    LayoutTypes.EDITOR: "Mmmm creating, what are you up to?",
    LayoutTypes.FAILED_OPENING: "Oops... it's not a level...",
    LayoutTypes.NEW_LEVEL: "Ohh, it's getting intresting!",
    LayoutTypes.OVERWRITE: "Will you delete me? :'(",
    LayoutTypes.END_SCREEN: "No more levels here...",
    LayoutTypes.FAILED_TRASH: "Oops... something went wrong...",
    LayoutTypes.FAILED_DELETION: "Oops... something went wrong...",
    LayoutTypes.CONFIRM_DELETION: "Pweeaasee nooo!11!1!!!"
}

ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 "
# ==================== CLASSES ====================
class MagnAni(ga.TextureFuncAniBase):
    def __init__(self, prop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = ga.AnimType.TFUNC1
        self.prop = prop

    def start(self):
        if not self.ended: return
        if self.e._current_ani7 not in (None, self.name):
            self.starting_val = getattr(self.e, self.e._current_ani7)._prev_val
        super().start()

    def get_frame(self, *args, **kwargs):
        super().get_frame(*args, **kwargs)
        texture = pygame.transform.smoothscale(self.get_element_frame(), round(self._prev_val))
        self.e.change_size(self._prev_val * self.prop)
        return texture


class NewButton(ga.Button):
    def __init__(self,
       sn: ga.Size = None,
       sh: ga.Size = None,
       sc: ga.Size = None,
       sh_m: ga.Size = 1.15,
       sc_m: ga.Size = 1.07,
       *args, **kwargs):
        kwargs["halo"] = HALO
        if not "curve" in kwargs: kwargs["curve"] = BUTTON_CURVE
        kwargs["always_click"] = True
        # kwargs["texture_debug"] = True
        super().__init__(*args, **kwargs)

        if sn is None: sn = ga.get_size(self._tn.frames[0])
        if sh is None: sh = sn * sh_m
        if sc is None: sc = sn * sc_m

        sn = ga.Size(sn)
        sh = ga.Size(sh)
        sc = ga.Size(sc)

        self.sn = sn
        self.sh = sh
        self.sc = sc

        prop_sn = ga.Size(self.size) / sn
        prop_sh = ga.Size(self.size) * sh_m / sh
        prop_sc = ga.Size(self.size) * sc_m / sc

        self.add_ani(MagnAni(
            name="normal",
            frames={
                "function": lambda x: x + ((sn - x) / 4),
                "frames": 1
            },
            loop=True,
            reset_on_loop=False,
            time=0.01,
            starting_val=sn,
            prop=prop_sn
        ))
        self.add_ani(MagnAni(
            name="hover",
            frames={
                "function": lambda x: x + ((sh - x) / 4),
                "frames": 1
            },
            loop=True,
            reset_on_loop=False,
            time=0.01,
            starting_val=sh,
            prop=prop_sh
        ))
        self.add_ani(MagnAni(
            name="click",
            frames={
                "function": lambda x: x + ((sc - x) / 1.5),
                "frames": 1
            },
            loop=True,
            reset_on_loop=False,
            time=0.01,
            starting_val=sc,
            prop=prop_sc
        ))

    def render(self,
       surface: pygame.Surface,
       force_n: bool = False,
       force_h: bool = False,
       force_c: bool = False,
       *args, **kwargs):

        forced = force_n or force_h or force_c
        clicked = (self.clicked and not forced) or force_c
        hovered = (self.hovered and not forced) or force_h

        if clicked:
            self.click.start()
        elif hovered:
            self.hover.start()
        else:
            self.normal.start()

        super().render(surface, force_n, force_h, force_c, *args, **kwargs)


class CheckBox(NewButton):
    def __init__(self, starting_state=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._f = self.switch
        self.value = starting_state
        self.checked_texture = pygame.image.load(f"{LOCAL_DIR}/assets/textures/buttons/checkbox_checked.png").convert_alpha()
        self.unchecked_texture = pygame.image.load(f"{LOCAL_DIR}/assets/textures/buttons/checkbox_unchecked.png").convert_alpha()
        self.checked_texture = pygame.transform.smoothscale(self.checked_texture, self.size)
        self.unchecked_texture = pygame.transform.smoothscale(self.unchecked_texture, self.size)
        self.set_texture()

    def switch(self):
        self.value = not self.value
        self.set_texture()

    def set_texture(self):
        if self.value:
            img = ga.StaticElement(
                pos=ga.Pos(self._halo) - 1,
                size=ga.get_size(self.checked_texture),
                texture=self.checked_texture
            )
        else:
            img = ga.StaticElement(
                pos=ga.Pos(self._halo) - 1,
                size=ga.get_size(self.unchecked_texture),
                texture=self.unchecked_texture
            )

        tn = self.bn.copy()
        img.render(tn)
        th = self.bh.copy()
        img.render(th)
        tc = self.bc.copy()
        img.render(tc)
        self._tn.frames = [tn]
        self._th.frames = [th]
        self._tc.frames = [tc]


class Layout:
    def __init__(self, buttons, others, run_buttons=True, buttons_first=True):
        if buttons_first:
            self.items = buttons + others
        else:
            self.items = others + buttons
        self.others = others
        self.current_idx = 0
        self.max_idx = len(self.items)
        self.buttons_end_idx = len(buttons) if buttons_first else len(others) - 1
        self.run_buttons = run_buttons
        self.buttons_first = buttons_first

        self.__add_ani_to_item(self.items)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_idx >= self.max_idx:
            self.current_idx = 0
            raise StopIteration

        if (self.current_idx < self.buttons_end_idx and self.buttons_first\
           or self.current_idx > self.buttons_end_idx and not self.buttons_first) and self.run_buttons:
            self.items[self.current_idx].auto_run()

        self.current_idx += 1
        return self.items[self.current_idx - 1]

    def __getitem__(self, index):
        return self.items[index]

    def __setitem__(self, index, other):
        if isinstance(other, ga.Slider):
            other._bar.add_ani(ga.AlphaAni(**FADE_IN))
            other._bar.add_ani(ga.AlphaAni(**FADE_OUT))
            other._button.add_ani(ga.AlphaAni(**FADE_IN))
            other._button.add_ani(ga.AlphaAni(**FADE_OUT))
        else:
            other.add_ani(ga.AlphaAni(**FADE_IN))
            other.add_ani(ga.AlphaAni(**FADE_OUT))
        self.items[index] = other

    def __delitem__(self, index):
        del self.items[index]
        self.max_idx -= 1
        if index < self.buttons_end_idx:
            self.buttons_end_idx -= 1

    def get_other(self, index):
        return self.others[index]

    def set_other(self, index, other):
        self.others[index] = self.items[index + self.buttons_end_idx] = other

    def del_other(self, index):
        del self.others[index]
        del self.items[index + self.buttons_end_idx]
        self.max_idx -= 1

    def add_item(self, other):
        if isinstance(other, ga.Slider):
            other._bar.add_ani(ga.AlphaAni(**FADE_IN))
            other._bar.add_ani(ga.AlphaAni(**FADE_OUT))
            other._button.add_ani(ga.AlphaAni(**FADE_IN))
            other._button.add_ani(ga.AlphaAni(**FADE_OUT))
        else:
            other.add_ani(ga.AlphaAni(**FADE_IN))
            other.add_ani(ga.AlphaAni(**FADE_OUT))

        if isinstance(other, ga.Button) or issubclass(other, ga.Button):
            self.items.insert(self.buttons_end_idx, other)
            self.buttons_end_idx += 1
        else:
            self.items.append(other)
        self.max_idx += 1

    def __add_ani_to_item(self, items):
        for i in items:
            if isinstance(i, ga.Slider):
                i._bar.add_ani(ga.AlphaAni(**FADE_IN))
                i._bar.add_ani(ga.AlphaAni(**FADE_OUT))
                i._button.add_ani(ga.AlphaAni(**FADE_IN))
                i._button.add_ani(ga.AlphaAni(**FADE_OUT))
                i._bar.transparency = 0
                i._button.transparency = 0
            elif isinstance(i, Page):
                for page in i.pages:
                    self.__add_ani_to_item(page)
                if i.has_buttons:
                    i.prev_page_button.add_ani(ga.AlphaAni(**FADE_IN))
                    i.prev_page_button.add_ani(ga.AlphaAni(**FADE_OUT))
                    i.next_page_button.add_ani(ga.AlphaAni(**FADE_IN))
                    i.next_page_button.add_ani(ga.AlphaAni(**FADE_OUT))
            else:
                i.add_ani(ga.AlphaAni(**FADE_IN))
                i.add_ani(ga.AlphaAni(**FADE_OUT))
                i.transparency = 0


class FadeOutPage:
    def __init__(self, page_element):
        self.e = page_element

    def start(self):
        self.e.run_buttons = False
        for i in self.e.pages[self.e.current_page]:
            if isinstance(i, ga.Slider):
                i._bar.fade_out.start()
                i._button.fade_out.start()
            elif isinstance(i, Page):
                i.fade_out.start()
            else:
                i.fade_out.start()
        if self.e.has_buttons:
            self.e.prev_page_button.fade_out.start()
            self.e.next_page_button.fade_out.start()


class FadeInPage:
    def __init__(self, page_element):
        self.e = page_element

    def start(self):
        self.e.run_buttons = True
        for i in self.e.pages[self.e.current_page]:
            if isinstance(i, ga.Slider):
                i._bar.transparency = 0
                i._button.transparency = 0
                i._bar.fade_in.start()
                i._button.fade_in.start()
            else:
                i.transparency = 0
                i.fade_in.start()

        for page in self.e.pages:
            for i in page:
                if isinstance(i, NewButton):
                    i.normal._prev_val = i.sn
                    i.hover._prev_val = i.sn
                    i.click._prev_val = i.sn

        if self.e.has_buttons:
            self.e.prev_page_button.transparency = 0
            self.e.next_page_button.transparency = 0
            self.e.prev_page_button.fade_in.start()
            self.e.next_page_button.fade_in.start()


class Page:
    def __init__(self,
       pages,
       next_page_button=None,
       prev_page_button=None,
       starting_page=0,
       run_buttons=True,
       loop_back=False):
        self.current_page = starting_page
        self.starting_page = starting_page
        self.pages = pages
        self.__transparency = 255
        self.run_buttons = run_buttons
        self.next_page_button = next_page_button
        self.prev_page_button = prev_page_button
        self.has_buttons = self.next_page_button is not None
        if self.has_buttons:
            self.next_page_button._f = self.next_page
            self.prev_page_button._f = self.prev_page
        self.fade_in = FadeInPage(self)
        self.fade_out = FadeOutPage(self)
        self.loop_back = loop_back

    def add_ani(self, ani):
        for page in self.pages:
            for i in page:
                if isinstance(i, ga.Slider):
                    i._bar.add_ani(ani)
                    i._button.add_ani(ani)
                    i._bar.transparency = 0
                    i._button.transparency = 0
                else:
                    i.add_ani(ani)
                    i.transparency = 0

    @property
    def transparency(self):
        return self.__transparency

    @transparency.setter
    def transparency(self, value):
        self.__transparency = value
        for element in self.pages[self.current_page]:
            element.transparency = value
        if self.has_buttons:
            self.next_page_button.transparency = value
            self.prev_page_button.transparency = value

    def next_page(self):
        self.current_page += 1
        if self.current_page >= len(self.pages):
            if self.loop_back: self.current_page = 0
            else: self.current_page -= 1

    def prev_page(self):
        self.current_page -= 1
        if self.current_page < 0:
            if self.loop_back: self.current_page = len(self.pages) - 1
            else: self.current_page = 0

    def render(self, surface):
        for i in self.pages[self.current_page]:
            if self.run_buttons and isinstance(i, NewButton):
                i.auto_run()

            i.render(surface)
        if not self.has_buttons: return
        if len(self.pages) > 1:
            if self.loop_back or self.current_page + 1 != len(self.pages):
                self.next_page_button.render(surface)
                if self.run_buttons:
                    self.next_page_button.auto_run()
            if self.loop_back or self.current_page != 0:
                self.prev_page_button.render(surface)
                if self.run_buttons:
                    self.prev_page_button.auto_run()


class TextLabel(NewButton):
    def __init__(self, *args, **kwargs):
        self.text_size = kwargs["text_kwargs"]["text_size"]
        super().__init__(*args, **kwargs)

        self.typing = False
        self._f = self.toggle
        self._current_text = ""
        self._cursor_pos = -1

    def toggle(self):
        self.typing = True
        self._cursor_pos = len(self._current_text)
        self.update_text()

    def type(self, key):
        if key.key == pygame.K_BACKSPACE:
            self._current_text = self._current_text[:self._cursor_pos - 1] + self._current_text[self._cursor_pos:]
            self._cursor_pos -= 1
            if self._cursor_pos < 0: self._cursor_pos = 0
        elif key.key == pygame.K_LEFT:
            self._cursor_pos -= 1
            if self._cursor_pos < 0: self._cursor_pos = 0
        elif key.key == pygame.K_RIGHT:
            self._cursor_pos += 1
            if self._cursor_pos > len(self._current_text): self._cursor_pos = len(self._current_text)
        else:
            if not key.unicode in ALLOWED_CHARS or len(key.unicode) == 0 or len(self._current_text) == 15:
                return
            self._current_text = self._current_text[:self._cursor_pos] + key.unicode + self._current_text[self._cursor_pos:]
            self._cursor_pos += 1
        self.update_text()

    def update_text(self):
        text = self._current_text[:self._cursor_pos] + ("|" if self.typing else "") + self._current_text[self._cursor_pos:]
        self.change_text({
            "text": text,
            "text_size": self.text_size,
            "text_font": FONT
        })

    def render(self, surface):
        super().render(surface, force_c=self.typing)


class BlockElement(ga.Element):
    def __init__(self, id_, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id_


# ==================== FUNCTIONS ====================

def get_comet():
    comet_size = ga.Size(random.randint(128, 255))
    comet_pos = (random.randint(comet_size.w * 2, SIZE.w + comet_size.w*2),
                -random.randint(comet_size.h, 255))
    comet_ani = ga.PosAni(
        name="slide",
        frames={
            "function": lambda x: x + (-SIZE.h/72, SIZE.h/72),
            "frames": 100
        },
        time=0.002
    )
    comet = ga.Element(
        pos=comet_pos,
        size=comet_size,
        texture=COMET_TEXTURE,
        animations=[comet_ani]
    )
    del comet_size, comet_pos, comet_ani
    return comet
