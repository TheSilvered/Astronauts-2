#!/usr/bin/env python3
import pygame
from pygame import gfxdraw
import math

from typing import Optional

from .element import *
from .label import Label
from .mouse_interaction import MouseInteraction
from .colors import MAGENTA, BLACK, GRAY, RED, ColorType, P
from .position import *
from .defalut_values import *

pygame.init()


class Button(MouseInteraction):
    """
    Button class that lets you run a function when the button is clicked

    Args:
        tn (Surface?): texture of the button when it's idle
        th (Surface?): texture of the button when it's hovered
        tc (Surface?): texture of the button when it's clicked
        cn (ColorType): color of the button when it's idle
        ch (ColorType?): color of the button when it's hovered
        cc (ColorType?): color of the button when it's clicked
        make_texture (bool): if the texture should be created on initialization,
            if false, gameassets.button.Button.buffer_texture() must be called
        curve (int): radious of the curve of the corner the button
        halo (int): how much the halo should spread from the size of the button,
            0 means no halo
        old_halo (int): sets the halo to be similar to the old halo calculation
        halo_intensity (int): how transparent should the halo be, 0 or a value
            bigger than the halo, throws an error
        halo_mul (float): how much the halo should increase when the button is
            hovered or clicked by the mouse
        halo_cn (ColorType?): color of the halo when the button it's idle
        halo_ch (ColorType?): color of the halo when the button it's hovered
        halo_cc (ColorType?): color of the halo when the button it's clicked
        halo_offset (Pos, IntPos): offset of the halo from the centre
        brush_size (int): size of the brush used to blur the halo, larger brush
            means that the minimum halo without a visible edge increases
        edge (int): thickness of the edge, 0 is no edge
        edge_cn (ColorType?): color of the edge when the button it's idle
        edge_ch (ColorType?): color of the edge when the button it's hovered
        edge_cc (ColorType?): color of the edge when the button it's clicked
        sound (Sound?): sound to play when the button gets clicked
        text_kwargs (dict?): keyword arguments to build a label that is the
            text of the button, you can specify an offset but not a position or
            a parent
        texture_debug (bool): if true adds guidelines to the texture to the
            borders of the texture an the actual borders of the button
        function (function): function to run when the button is clicked
        fargs (list?): arguments of the function
        fkwargs (dict?): keyword arguments of the function

    Attrs:
        _colors (list): list containing the colors of the button
        _halo_c (list): list containing the colors of the halo
        _edge_c (list): list containing the colors of the edge
        _curve (int): radius of the curvature of the corners
        _edge (int): thickness of the edge
        _halo (int): thickness of the halo
        _halo_m (int): multiplier of the halo
        _halo_i (int): intensity of the halo
        _halo_o (IntPos): offset of the halo
        _ho (IntPos): offset of the halo with the negative arguments being 0
        _bo (IntPos): offset of the main body of the button, with the absolute
            values of the negative arguments of _halo_o
        _text_kwargs (dict): keyword arguments of the text of the button
        _bn (Surface): base of the button idle without text
        _bh (Surface): base of the button hovered without text
        _bc (Surface): base of the button clicked without text
        _tn (TextureAni): animation containing the texture of the button idle
        _th (TextureAni): animation containing the texture of the button hovered
        _tc (TextureAni): animation containing the texture of the button clicked
        _sound (Sound?): sound of the button
        _f (function?): function of the button
        _fargs (list): args of the function
        _fkwargs (dict): kwargs of the function
        _can_run (bool): if the button can call the function again (prevents
            repetitive calls on auto_run())

    Methods:
        __texture (rtype: Surface): builds the texture of the button
        _add_text (rtype: Surface): adds the text to a button texture
        change_text (rtype: None): changes the text of the button, if the
            texture is imported throgh buffer_texture, the text will not be
            changed, but added on top
        save_texture_buffers (rtype: None): saves the textures into buffers, the
            names are automatic, more later
        load_texture_buffers (rtype: None): loads the textures from buffers
        save_texture_png (rtype: None): saves the textures to pngs
        load_texture_png (rtype: None): loads the textures from pngs
        run (rtype: None): runs the function of the button if visible
        auto_run (rtype: bool): calls run() if the button is clicked, returns
            True if the button ran the function
        render (rtype: None): renders the button on the specified surface, has
            additional arguments

        save_texture_buffers, given a path, saves the textures adding
        tn.texture, th.texture and tc.texture for the normal texture, hovered
        texture and clicked texture respectively

        Similarly save_texture_png saves the textures adding tn.png, th.png and
        tc.png for the normal texture, hovered texture and clicked texture
        respectively and load_texture_png will add the same extensions to the
        path to open the textures
    """
    def __init__(self,
       tn: Optional[pygame.Surface] = B.TN,
       th: Optional[pygame.Surface] = B.TH,
       tc: Optional[pygame.Surface] = B.TC,
       cn:          ColorType  = B.CN,
       ch: Optional[ColorType] = B.CH,
       cc: Optional[ColorType] = B.CC,
       make_texture: bool = B.MAKETEXTURE,
       curve: int = B.CURVE,
       halo: int = B.HALO,
       old_halo: int = B.OLDHALO,
       halo_intensity: float = B.HALOINTENSITY,
       halo_mul: float = B.HALOMUL,
       halo_cn: Optional[ColorType] = B.HALOCN,
       halo_ch: Optional[ColorType] = B.HALOCH,
       halo_cc: Optional[ColorType] = B.HALOCC,
       halo_offset: Pos = B.HALOOFFSET,
       brush_size: int = B.BRUSHSIZE,
       edge: int = B.EDGE,
       edge_cn: Optional[ColorType] = B.EDGECN,
       edge_ch: Optional[ColorType] = B.EDGECH,
       edge_cc: Optional[ColorType] = B.EDGECC,
       sound: Optional[pygame.mixer.Sound] = B.SOUND,
       text_kwargs: Optional[dict] = B.TEXTKWARGS,
       texture_debug: bool = B.TEXTUREDEBUG,
       function = B.FUNCTION,
       fargs: Optional[list] = B.FARGS,
       fkwargs: Optional[dict] = B.FKWARGS,
       *args, **kwargs):

        super().__init__(*args, **kwargs)
        if ch is None: ch = cn
        if cc is None: cc = ch

        if halo_cn is None:
            halo_cn = cn
            halo_ch = ch
            halo_cc = cc
        else:
            if halo_ch is None: halo_ch = halo_cn
            if halo_cc is None: halo_cc = halo_ch

        if tn is not None:
            if th is None: th = tn
            if tc is None: tc = th
            if cn == BLACK:
                super().change_size((tn.get_width(), tn.get_height()))

        if edge_cn is None: edge_cn = cn
        if edge_ch is None: edge_ch = edge_cn
        if edge_cc is None: edge_cc = edge_ch

        self._colors = [cn, ch, cc]
        self._halo_c = [halo_cn, halo_ch, halo_cc]
        self._edge_c = [edge_cn, edge_ch, edge_cc]

        if curve > self.size.w // 2:
            curve = self.size.w // 2
        if curve > self.size.h // 2:
            curve = self.size.h // 2

        self._curve = curve

        if halo + 1 < brush_size: brush_size = int(halo) + 1

        self._b_size = brush_size
        old_halo_size = brush_size // 2 - 1
        if halo == 0 and old_halo != 0:
            if old_halo <= old_halo_size*2 - 1:
                halo = old_halo // 2
            else:
                halo = old_halo // 2 + old_halo_size

        self._edge = edge
        self._halo = halo
        self._halo_m = halo_mul
        self._halo_i = halo_intensity
        if self._halo_i > self._halo:
            self._halo_i = self._halo
        if halo > 0 and halo_intensity > 0:
            self._halo_o = IntPos(halo_offset)
        else:
            self._halo_o = IntPos(0)

        self._ho = IntPos(0)
        self._bo = IntPos(0)

        if self._halo_o.x < 0:
            self._ho.x = -self._halo_o.x
        else:
            self._bo.x = self._halo_o.x

        if self._halo_o.y < 0:
            self._ho.y = -self._halo_o.y
        else:
            self._bo.y = self._halo_o.y

        if self._c_pos is None and not self._c_anc:
            self.offset_n = -IntPos(self._halo)
            # self.offset_n = IntPos(0)
            self.offset_h = -IntPos(self._halo * self._halo_m)
            # self.offset_h = IntPos(0)
            if self._halo_o.x > 0:
                self.offset_n.x -= self.w - (self.w - self._halo_o.x)
                self.offset_h.x -= self.w - (self.w - self._halo_o.x)
            if self._halo_o.y > 0:
                self.offset_n.y -= self.h - (self.h - self._halo_o.y)
                self.offset_h.y -= self.h - (self.h - self._halo_o.y)
        else:
            self.offset_n = self.offset_h = -IntPos(self._halo_o/2)

        if text_kwargs is None:
            text_kwargs = {"text": ""}
        self._text_kwargs = text_kwargs

        self._texture_debug = texture_debug
        if tn is not None and make_texture:
            tn, self.bn = self.__texture(0, halo           , tn)
            th, self.bh = self.__texture(1, halo * halo_mul, th)
            tc, self.bc = self.__texture(2, halo * halo_mul, tc)

        elif make_texture:
            tn, self.bn = self.__texture(0, halo           )
            th, self.bh = self.__texture(1, halo * halo_mul)
            tc, self.bc = self.__texture(2, halo * halo_mul)

        self._tn = TextureAni(False, [tn], "_tn", self, loop=True)
        self._th = TextureAni(False, [th], "_th", self, loop=True)
        self._tc = TextureAni(False, [tc], "_tc", self, loop=True)

        self._sound = sound

        self._f = function
        self._fargs = [] if fargs is None else fargs
        self._fkwargs = {} if fkwargs is None else fkwargs

        self._can_run = True

        del self.image
        self.image = None

    @property
    def pos(self):
        if self._pos is not None:
            return round(self._pos)
        elif self._anc:
            return getattr(self._p, self._anc_type) + self.offset
        else:
            return getattr(self._p, self._anc_type) - self.size/2 + self.offset
    @pos.setter
    def pos(self, value: Pos):
        value = Pos(value)

        if self._anc or self._c_anc:
            self.offset = value - self.pos
            self.offset_n = self.offset_h = -IntPos(self._halo_o/2)
        else:
            self._pos = value
            if self._halo_o.x > 0:
                self.offset_n.x -= self.w - (self.w - self._halo_o.x)
                self.offset_h.x -= self.w - (self.w - self._halo_o.x)
            if self._halo_o.y > 0:
                self.offset_n.y -= self.h - (self.h - self._halo_o.y)
                self.offset_h.y -= self.h - (self.h - self._halo_o.y)

        if self._c_pos is not None:
            self._c_pos = self._pos + self.size / 2

        self.rect.topleft = self.pos

    def __texture(self,
       color_index: int,
       halo: int,
       image: Optional[pygame.Surface] = B.TEXTURE.IMAGE) -> pygame.Surface:
        """
        Args:
            color_index (int): 0, 1, 2 index of the color to pick from
                _colors, _halo_c and _edge_c
            halo (int): dimension of the halo
            image (Surface): texture to use
        """
        halo = int(halo)
        main_body = pygame.Surface(self.size, pygame.SRCALPHA)
        t_size = self.size + halo*2 + abs(self._halo_o)
        h_size = t_size - abs(self._halo_o)
        t = pygame.Surface(t_size, pygame.SRCALPHA)

        color = self._colors[color_index]
        halo_c = self._halo_c[color_index]
        edge_c = self._edge_c[color_index]

        edge = self._edge
        curve = self._curve

        if color == BLACK: color = GRAY(1)
        if halo_c == BLACK: halo_c = GRAY(1)
        if edge_c == BLACK: edge_c = GRAY(1)

        if "color" in self._text_kwargs and self._text_kwargs["color"] == BLACK:
            self._text_kwargs["color"] = GRAY(1)

        main_body.set_colorkey(BLACK)

        edge_rect = pygame.Rect(0, 0, self.w, self.h)
        inner_rect = pygame.Rect(edge, edge, self.w - edge*2, self.h - edge*2)

        in_curve = curve - edge

        pygame.draw.rect(main_body, edge_c, edge_rect, 0, curve)
        pygame.draw.rect(main_body, color, inner_rect, 0, in_curve)

        width = main_body.get_width()
        height = main_body.get_height()

        for x in range(curve):
            for y in range(curve):
                distance = math.sqrt((x-curve)**2 + (y-curve)**2)
                f_x = width - x - 1
                f_y = height - y - 1
                if distance < curve:
                    main_body.set_at((x, y), edge_c)
                    main_body.set_at((f_x, y), edge_c)
                    main_body.set_at((x, f_y), edge_c)
                    main_body.set_at((f_x, f_y), edge_c)
                elif distance < curve + 1:
                    current_color = edge_c + (255 * (1 - (distance-curve)),)
                    main_body.set_at((x, y), current_color)
                    main_body.set_at((f_x, y), current_color)
                    main_body.set_at((x, f_y), current_color)
                    main_body.set_at((f_x, f_y), current_color)

        alpha = lambda new, prev, a: a * new + (1 - a) * prev

        for x in range(in_curve):
            for y in range(in_curve):
                f_x = width - x - 1 - edge
                f_y = height - y - 1 - edge
                distance = math.sqrt((x-in_curve)**2 + (y-in_curve)**2)
                if distance < in_curve:
                    main_body.set_at((x + edge, y + edge), color)
                    main_body.set_at((f_x, y + edge), color)
                    main_body.set_at((x + edge, f_y), color)
                    main_body.set_at((f_x, f_y), color)
                elif distance < in_curve + 1:
                    if edge:
                        a = 1 - (distance-in_curve)
                        new_color = list(color)
                        new_color[0] = alpha(new_color[0], edge_c[0], a)
                        new_color[1] = alpha(new_color[1], edge_c[1], a)
                        new_color[2] = alpha(new_color[2], edge_c[2], a)
                    else:
                        a = 255 * (1 - (distance-in_curve))
                        new_color = color + (a,)
                    main_body.set_at((x + edge, y + edge), new_color)
                    main_body.set_at((f_x, y + edge), new_color)
                    main_body.set_at((x + edge, f_y), new_color)
                    main_body.set_at((f_x, f_y), new_color)

        main_body.set_alpha(255)

        size = self._b_size // 2

        if halo > 0 and self._halo_i > 0:
            alpha = 255 // (halo // self._halo_i)
            halo_range = halo if halo <= (size-1) * 2 - 1 else halo - size - 1
            for i in range(0, halo_range):
                main_body.set_alpha(alpha)
                t.blit(
                    pygame.transform.scale(main_body, self.size + i*2),
                    IntPos(halo - i)
                )

            blur_t = pygame.Surface(h_size//2).convert_alpha()
            rect_size = (self._b_size, self._b_size)

            offset_x = abs(self._halo_o.x)
            offset_y = abs(self._halo_o.y)
            if offset_x > h_size.w//2: offset_x = h_size.w//2
            if offset_y > h_size.h//2: offset_y = h_size.h//2
            if offset_x > curve + halo > offset_y:
                offset_y = curve + halo
            if offset_y > curve + halo > offset_x:
                offset_x = curve + halo

            h_side_i = range(halo + curve, halo + curve + 1)
            h_side_j = range(halo + offset_y + curve)

            v_side_i = range(halo + offset_x + curve)
            v_side_j = range(halo + curve, halo + curve + 1)

            c_range = range(halo + curve)
            # Horizontal side
            for i in h_side_i:
                for j in h_side_j:
                    rect_pos = (i - size, j - size)
                    rect = pygame.Rect(rect_pos, rect_size)
                    average = pygame.transform.average_color(t, rect)
                    blur_t.set_at((i, j), halo_c + (average[3],))

            x1 = halo + curve
            x2 = h_size.w//2
            for y in h_side_j:
                try:
                    color = blur_t.get_at((x1, y))
                # If there is no horizontal side, just continue
                except IndexError:
                    break
                pygame.draw.line(blur_t, color, (x1, y), (x2, y))

            # Vertical side
            for i in v_side_i:
                for j in v_side_j:
                    rect_pos = (i - size, j - size)
                    rect = pygame.Rect(rect_pos, rect_size)
                    average = pygame.transform.average_color(t, rect)
                    blur_t.set_at((i, j), halo_c + (average[3],))

            y1 = halo + curve
            y2 = h_size.h//2
            for x in v_side_i:
                try:
                    color = blur_t.get_at((x, y1))
                # If there is not vertical side, just continue
                except IndexError:
                    break
                pygame.draw.line(blur_t, color, (x, y1), (x, y2))

            # Corner
            for i in c_range:
                for j in c_range:
                    rect_pos = (i - size, j - size)
                    rect = pygame.Rect(rect_pos, rect_size)
                    average = pygame.transform.average_color(t, rect)
                    blur_t.set_at((i, j), halo_c + (average[3],))

            t = pygame.Surface(t_size, pygame.SRCALPHA)
            t.blit(blur_t, IntPos(0, 0) + self._ho)
            blur_t = pygame.transform.flip(blur_t, True, False)
            t.blit(blur_t, IntPos(h_size.w//2, 0) + self._ho)
            blur_t = pygame.transform.flip(blur_t, False, True)
            t.blit(blur_t, IntPos(h_size.w//2, h_size.h//2) + self._ho)
            blur_t = pygame.transform.flip(blur_t, True, False)
            t.blit(blur_t, IntPos(0, h_size.h//2) + self._ho)

            main_body.set_alpha(255)
            t.blit(main_body, IntPos(halo) + self._bo)

        else:
            t.blit(main_body, (0, 0))

        if image is not None:
            image = Element(
                c_pos=t_size/2 - abs(self._halo_o/2),
                size=(image.get_width(), image.get_height()),
                texture=image
            )
            image.render(t, offset=self._bo)

        t.set_colorkey(BLACK)

        # Used to change text
        base = t.copy()

        t = self._add_text(t)

        if self._texture_debug:
            pygame.draw.lines(t, MAGENTA, True, ((0, 0)    , t_size.xay(-1, 0),
                                                 t_size - 1, t_size.xya(-1, 0)))

        return t, base

    def _add_text(self, base: pygame.Surface) -> pygame.Surface:
        """
        Adds the current text to a base

        Args:
            base (Surface): base to add the text onto
        """
        base = base.copy()
        self._text_kwargs["c_pos"] = (base.get_width()/2, base.get_height()/2)
        if self._text_kwargs["text"] != "":
            text = Label(**self._text_kwargs)
            text.pos += text.offset
            text.render(base, offset=self._halo_o/2)
        return base

    def change_text(self, text_kwargs: dict) -> None:
        """
        Changes the text of the button

        Args:
            text_kwargs (dict): kwargs for the text label
        """
        self._text_kwargs = text_kwargs
        pos1 = (self.bn.get_width()/2, self.bn.get_height()/2)
        pos2 = (self.bh.get_width()/2, self.bh.get_height()/2)
        self._text_kwargs["c_pos"] = pos1
        self._tn.frames = [self._add_text(self.bn)]
        self._text_kwargs["c_pos"] = pos2
        self._th.frames = [self._add_text(self.bh)]
        self._tc.frames = [self._add_text(self.bc)]

    def save_texture_buffers(self, path: str) -> None:
        """
        Saves the texture buffers in files in RGBA mode

        Args:
            path (str): path of the texture file
        """
        if len(path) > 0 and not path[-1] in "\\/": path += "/"
        tn = pygame.image.tostring(self._tn.frames[0], "RGBA")
        th = pygame.image.tostring(self._th.frames[0], "RGBA")
        tc = pygame.image.tostring(self._tc.frames[0], "RGBA")
        with open(path + "tn.texture", "wb") as f:
            f.write(tn)
        with open(path + "th.texture", "wb") as f:
            f.write(th)
        with open(path + "tc.texture", "wb") as f:
            f.write(tc)

    def load_texture_buffers(self,
       tn: bytes,
       th: Optional[bytes] = B.BUFFERTEXTURE.TH,
       tc: Optional[bytes] = B.BUFFERTEXTURE.TC) -> None:
        """
        Loads the textures from buffers
        Requires the button to be initialized with the same size, halo and
        halo offset to be loaded correctly

        Args:
            tn (bytes): texture for button idle
            tn (bytes): texture for button hovered
            tn (bytes): texture for button clicked
        """
        tn_size = self.size + self._halo*2 + abs(self._halo_o)
        th_size = self.size + int(self._halo*self._halo_m)*2 + abs(self._halo_o)

        if th is None:
            th_size = tn_size

        self._tn.frames = [pygame.image.frombuffer(tn, tn_size, "RGBA")]
        self._th.frames = [pygame.image.frombuffer(th, th_size, "RGBA")]
        self._tc.frames = [pygame.image.frombuffer(tc, th_size, "RGBA")]
        self.bn, = self._tn.frames
        self.bh, = self._th.frames
        self.bc, = self._tc.frames

    def save_texture_png(self, path: str) -> None:
        """
        Saves the textures in .png files
        Requires the button to be initialized with the same size, halo and
        halo offset

        Args:
            path (str): path of the textures

            Given the path, the function will automatically add tn.png, th.png
            and tc.png for the normal texture, hovered texture and clicked
            texture respectively
        """
        pygame.image.save(self._tn.frames[0], f"{path}tn.png")
        pygame.image.save(self._th.frames[0], f"{path}th.png")
        pygame.image.save(self._tc.frames[0], f"{path}tc.png")

    def load_texture_png(self, path: str) -> None:
        """
        Loads the textures from .png files

        Args:
            path (str): path of the textures

            Given the path, the function will automatically add tn.png, th.png
            and tc.png for the normal texture, hovered texture and clicked
            texture respectively
        """
        self._tn.frames = [pygame.image.load(f"{path}tn.png")]
        self._th.frames = [pygame.image.load(f"{path}th.png")]
        self._tc.frames = [pygame.image.load(f"{path}tc.png")]

    def run(self) -> None:
        """Runs self._f if the button is visible and plays the sound"""
        if not self.visible:
            return

        if self._sound:
            pygame.mixer.Sound.play(self._sound)

        if self._f is None:
            return

        self._f(*self._fargs, **self._fkwargs)

    def auto_run(self) -> bool:
        """Calls self.run() if the button is clicked"""
        # Prevents spam
        if self.clicked and self._can_run:
            self.run()
            self._can_run = False
            return True

        elif not self.clicked:
            self._can_run = True
        return False

    def render(self,
       surface: pygame.Surface,
       force_n: bool = B.RENDER.FORCEN,
       force_h: bool = B.RENDER.FORCEH,
       force_c: bool = B.RENDER.FORCEC,
       pos: Optional[Pos] = B.RENDER.POS,
       offset: (Pos, IntPos) = B.RENDER.OFFSET,
       update: bool = B.RENDER.UPDATE,
       *args, **kwargs) -> None:
        """
        Renders the correct texture onto the surface

        Args:
            surface (Surface): surface to blit the texture onto
            force_n (bool): forces the normal texture
            force_h (bool): forces the hovered texture
            force_c (bool): forces the clicked texture
            update (bool): if the state of the button (normal, hovered or
                clicked) should be updated
        """

        forced = force_n or force_h or force_c
        if update:
            clicked = (self.clicked and not forced) or force_c
            hovered = (self.hovered and not forced) or force_h
        else:
            clicked = force_c
            hovered = force_h

        if clicked:
            self._tc.start()
            super().render(surface, pos, self.offset_h+offset, *args, **kwargs)
        elif hovered:
            self._th.start()
            super().render(surface, pos, self.offset_h+offset, *args, **kwargs)
        else:
            self._tn.start()
            super().render(surface, pos, self.offset_n+offset, *args, **kwargs)

        if self._texture_debug:
            pygame.draw.lines(surface, MAGENTA, True, (self._lu,
                                                       self._ru,
                                                       self._rd,
                                                       self._ld))


pygame.quit()
