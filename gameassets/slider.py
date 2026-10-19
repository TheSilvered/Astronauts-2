#!/usr/bin/env python3
import pygame

from typing import Optional

from .element import StaticElement
from .draggable import Draggable
from .button import Button
from .position import IntPos, Pos
from .defalut_values import *

pygame.init()


class Slider(StaticElement):
    """
    Args:
        indicator_kwargs (dict): keyword arguments used when creating a button
            (halo, curve, cn, ...), is the cursor that you drag
            Any position specified will be ignored
        bar_kwargs (dict): keyword arguments used when creating a button (halo,
            curve, cn, ...), is the bar on which the indicator slides on
            Any position specified will be ignored
        min_value (float): minimum value of the slider
        max_value (float): maximum value of the slider
        indicator_pos (float?): position at which the indicator is set on
            initialization, it's a value between min_value and max_value,
            default is min_value
        arg_num (int): numbers of position to which the indicator will snap
            Ex: min_value = 1, max_value = 5, arg_num = 5. The indicator, in
            this case will automatically set it's position to be the closest
            value to either 1, 2, 3, 4 or 5
        snap_speed (float): speed at which the indicator gets to the closest
            position of arg_num

    Attrs:
        _bar (Button): bar on which the indicator slides
        _button (Button): the indicator that renders
        _drag (Draggable): the indicator that gets dragged
        min (float): minimum value of the silder
        max (float): maximum value of the slider
        _mp (int): maximium value in pixels
        arg_num (list): list of the x positions of arg_num

    Properties:
        value_pos (int): position in pixels relative to the start of the bar
        value (float): the value currently selected
    """
    def __init__(self,
       indicator_kwargs: dict,
       bar_kwargs: dict,
       indicator_class = S.INDICATORCLASS,
       bar_class = S.BARCLASS,
       min_value: float = S.MINVALUE,
       max_value: float = S.MAXVALUE,
       indicator_pos: Optional[float] = S.INDICATORPOS,
       arg_num: int = S.ARGNUM,
       snap_speed: float = S.SNAPSPEED,
       use_c_for_cursor: bool = False,
       *args, **kwargs):

        super().__init__(*args, **kwargs)
        if "size" in bar_kwargs:
            self.change_size(bar_kwargs["size"])
        elif "c_size" in bar_kwargs:
            self.change_size(c_size=bar_kwargs["c_size"])
        pos_kwargs = {"pos", "c_pos", "parent"}
        if pos_kwargs & set(indicator_kwargs) != set():
            indicator_kwargs["c_pos"] = None
            indicator_kwargs["parent"] = None
            indicator_kwargs["anchor"] = None
            indicator_kwargs["c_anchor"] = None

        if indicator_class is None: indicator_class = Button
        if bar_class is None: bar_class = Button

        indicator_kwargs["pos"] = IntPos(0)
        bar_kwargs["pos"] = self.pos
        self._bar = bar_class(**bar_kwargs)
        self._button = indicator_class(**indicator_kwargs)
        self._bar.always_click = True
        self._button.always_click = True

        b0 = IntPos(self._bar._l    , self._bar._c.y - self._button.h/2)
        b1 = IntPos(self._bar._r + 1, self._bar._c.y + self._button.h/2)

        self._drag = Draggable(
            c_pos=IntPos(self._bar._l-self._button.w/2, self._bar._c.y),
            size=self._button.size,
            bounds=(b0, b1),
            speed=snap_speed,
            always_click=True
        )

        # Sets the anchor for _button, I couldn't do it before
        # because I needed the size of the button to create _drag,
        # the parent
        self._button._p = self._drag
        self._button._c_anc = True
        self._button._anc_type = "_c"
        self._button._pos = None
        self._button._c_pos = None
        self._button.offset_n = -IntPos(self._button._halo_o/2)
        self._button.offset_h = -IntPos(self._button._halo_o/2)

        self.min = min_value
        self.max = max_value
        self._mp = self._bar.w - self._button.w + 1

        if self.max != 0 and indicator_pos is not None:
            if self.max-self.min == 0:
                return
            self._drag.pos = (
                self._mp*(indicator_pos-self.min)/(self.max-self.min) + b0.x,
                self._bar._c.y)

        if arg_num < 2:
            self.arg_num = [i for i in range(self._mp + 1)]
        else:
            self.arg_num = [self._mp / (arg_num-1) * i
                            for i in range(arg_num)]

    @property
    def value_pos(self):
        return self._drag.pos.x - self._drag.b0.x

    @property
    def value(self):
        return ((self.max - self.min) * self.value_pos) / self._mp + self.min

    def render(self, surface, *args, **kwargs):
        hovered = self._bar.hovered or self._button.hovered
        clicked = self._button.clicked or self._drag.dragging
        if clicked: hovered = False

        abs_diff = lambda value: abs(value - self.value_pos)
        snap_pos = min(self.arg_num, key=abs_diff) + self._bar._l

        self._drag.update_ani()
        self._drag.fix_pos()

        if self._bar.clicked and not clicked:
            self._drag.pos = IntPos(
                x=pygame.mouse.get_pos()[0] - self._drag.w / 2,
                y=self._drag.y
            )
            self._drag._prev_hovered = True

        self._drag.update()
        self._drag.fix_pos()

        if self._drag.snap_pos != Pos(snap_pos, self._drag.y):
            self._drag.change_snap(Pos(snap_pos, self._drag.y))

        self._bar.render(surface, False, hovered, clicked, *args, **kwargs)
        self._button.render(surface, False, hovered, clicked, *args, **kwargs)


pygame.quit()
