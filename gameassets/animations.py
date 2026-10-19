#!/usr/bin/env python3
import pygame

import time as t
from abc import ABC, abstractmethod
from typing import Optional, Any

from .position import *
from .defalut_values import *

try:
    from defaut_values import *
except ImportError:
    pass


class AnimType:
    """
    Default animations types:
        TEXTURE
        SIZE    |
        POS     | -> functional animations
        ALPHA   |

    Additional functional animations:
        FUNC1   |
        FUNC2   | -> functional animations
        FUNC3   |

        These can be ran on top of all the other animations and are dummy types
        for custom animations of custom elements
    """
    TEXTURE = 0
    SIZE = 1
    POS = 2
    ALPHA = 3
    FUNC1 = 4
    FUNC2 = 5
    FUNC3 = 6
    TFUNC1 = 7
    TFUNC2 = 8
    TFUNC3 = 9

    f = [1, 7]
    # When updating, update Element.get_texture docstring
    tf = [7, 10]


class AniBase(ABC):
    """
    Abstract class for any animation that contains a defined list of frames

    Args:
        frames (list): frames of the animation, see [ANIMATION CLASS].__doc__
            for more detail
        name (str): name of the animation and of the attribute to access it
        element (Element): the element which owns the animation
        time (float): time in seconds between frames
        loop (bool): if the animations should loop end() is called
        type_ (AnimType): type of the animation

    Attrs:
        frame (int): current frame
        e (Element): element of the animation
        frmes (list): list containing all the frames of the animation
        time (float): time between frames
        loop (bool): if the animation should loop
        last_time (float): last time the frame was changed
        name (str): name of the animation
        ended (bool): if the animation has been stopped or is running
        must_end (bool): if the animation is waiting to change frame to end
            itself effectively
        type (AnimType): type of the animation

    Methods:
        next (rtype: None): updates the current frame if it must be changed
        start (rtype: None): starts the animation
        end (rtype: None): ends the animation smoothly (no split-second frames)
        _finish_end (rtype: None): effectively ends the animation

    Abstract methods:
        get_frame (rtype: Any): returns the current frame or changes something
            in its element

    Dunder methods:
        __repr__ (rtype: str)
    """
    def __init__(self,
       frames: list,
       name: str,
       element: Any = AB.E,
       time: int = AB.TIME,
       loop: bool = AB.LOOP,
       type_: Optional[int] = AB.TYPE):
        self.frame = 0
        self.e = element
        self.frames = frames
        self.time = time
        self.loop = loop
        self.last_time = t.time()
        self.name = name
        self.ended = True
        self.must_end = False
        self.type = type_

    def next(self) -> None:
        """Updates the frame count"""
        # If the time since the last frame is not enough
        if t.time() < self.time + self.last_time or self.ended:
            return

        if self.must_end:
            self._finish_end()
            return

        # Keeps the animation at the same speed with a time between frames
        # bigger than self.time
        if self.time:
            self.frame += int((t.time()-self.last_time) // self.time)
        else:
            self.frame += 1
        if self.time:
            self.last_time += self.time
        if self.loop:
            self.frame %= len(self.frames)
        elif self.frame >= len(self.frames):
            self._finish_end()

    def start(self) -> None:
        """Starts the animation"""
        if self.e is None:
            raise ValueError(f"Animation {self.name} has no element")
        if self.must_end:
            self.must_end = False
        if self.ended:
            e_ani = getattr(self.e, f"_current_ani{self.type}")
            if e_ani is not None and e_ani != self.name:
                getattr(self.e, e_ani)._finish_end()
            setattr(self.e, f"_current_ani{self.type}", self.name)
            self.last_time = t.time()
            self.frame = 0
            self.ended = False

    def end(self) -> None:
        """Initializes the end process of the animation"""
        self.must_end = True

    def _finish_end(self) -> None:
        """Effectively ends the animation"""
        setattr(self.e, f"_current_ani{self.type}", None)
        self.frame = 0
        self.ended = True
        self.must_end = False

    def __del__(self) -> None:
        del self.frames, self.name, self.type

    @abstractmethod
    def get_frame(self) -> Any:
        pass

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"{self.name}: frames = {self.frames}, time = {self.time}, "\
               f"loop = {self.loop}, type = {self.type}"


class FuncAniBase(AniBase, ABC):
    """
    Abstract class for animations that can have a function instead of a list
    of frames

    Args:
        frames (list, dict): instead of specifying all the frames one by one,
            you can define a function that is ran with the previous value
            returned (a starting value is given)
            Keys of the dictionary are:
            - "function": the function used in the animation, it must take one
                argument and must return one value of the same type
            - "frames": how many times to call the function before the animation
                is considered ended
        change_end (bool): if at the end of the animation, the property changed
            should not return at the starting_val
        starting_val (Any): value used as the first value of the animataion

    Attrs:
        change_end (bool): if at the end of the animation, the property changed
            should not return at the starting_val
        _can_change (bool): if the frame must be changed
        _pendign_frames (int): number of frames that are yet to be calculated,
            if between two calls of next() multiple frames should be calculated,
            this keeps track of how many times to call the function
        _using_list (bool): if the frames argument (inherited from AniBase) is
            a list or not
        _prev_val (Any): previous value returned by the function
        starting_val (Any): doesn't get changed, value passed at the function
            at the first call

    Methods:
        next (rtype: None): updates the current frame and the pending frames
        get_frame (rtype: None): updated self._prev_val (does not do anything
            unless completed by a specific subclass that returns something or
            that changes something)

    Abstract methods:
        change_end_func (rtype: Any): function called if self.change_end is
            False or when the animation is in loop and it has to restart
    """
    def __init__(self,
       change_end: bool = FAB.CHANGEEND,
       starting_val: Any = FAB.STARTINGVAL,
       reset_on_loop: bool = FAB.RESETONLOOP,
       *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_end = change_end
        self._can_change = True
        self._pending_frames = 0
        self._using_list = isinstance(self.frames, list)
        self._prev_val = None
        self.starting_val = starting_val
        self.reset_on_loop = reset_on_loop

    def next(self) -> None:
        if self._using_list:
            super().next()

        if t.time() < self.time + self.last_time or self.ended:
            self._can_change = False
            return

        if self.must_end:
            self._finish_end()
            return

        if self.time:
            frames = int((t.time()-self.last_time) // self.time)
        else:
            frames = int(t.time()-self.last_time)

        self.frame += frames
        self._pending_frames = frames
        if self.frame > self.frames["frames"]:
            self._pending_frames = self.frame - self.frames["frames"]
        self._can_change = True

        self.last_time += self.time * self._pending_frames + self.time

        if self.frame >= self.frames["frames"]:
            self.frame = self.frames["frames"] - self.frame
            if not self.change_end and self.reset_on_loop:
                self.change_end_func()
                self._prev_val = self.starting_val

            if not self.loop:
                self._finish_end()

    def get_frame(self, i: Optional[int] = None) -> None:
        if isinstance(self.frames, list):
            self._prev_val = self.frames[self.frame if i is None else i]
        elif self._can_change:
            for _ in range(self._pending_frames):
                self._prev_val = self.frames["function"](self._prev_val)
            self._pending_frames = 0
        return

    @abstractmethod
    def change_end_func(self) -> Any:
        pass

    def start(self) -> None:
        if self.ended:
            self._prev_val = self.starting_val
        super().start()

    def _finish_end(self) -> None:
        if not self.change_end:
            self.change_end_func()
        super()._finish_end()


class TextureFuncAniBase(FuncAniBase):
    """
    This class allows the animation to modify the current texture of the
    animation, can overwrite the current texture animation or modify the
    current given frame

    These modifications are applied from the frame given by the texture
    animation in this order:
        AnimType.TFUNC1
        AnimType.TFUNC2
        AnimType.TFUNC3

    If either one is not playing it will be skipped
    """

    def get_element_frame(self):
        skips = []
        for i in range(self.type, AnimType.tf[1]):
            skips.append(i - AnimType.tf[0])
        return self.e.get_texture(False, skips)

    def change_end_func(self):
        pass


class TextureAni(AniBase):
    """
    Args:
        scale (bool): if the frames of the animation should be scaled on
            initialization

    Attrs:
        unscaled_frames (list): list of frames that are not scaled, used to not
            lose any detail

    Methods:
        scale_frames (rtype: None): scales the frames to the size of its element
            or to a specified size
        get_frame (rtype: pygame.Surface): returns the surface of the current frame
    """
    def __init__(self, scale: bool = TA.SCALE, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = AnimType.TEXTURE
        self.o_frames = self.frames.copy()
        if scale: self.scale_frames()

    def get_frame(self, i: Optional[int] = None) -> pygame.Surface:
        """
        Returns the current frame
        Args:
            i (int?): index of the frame, if None self.frame is used
        """
        return self.frames[self.frame if i is None else i]

    def scale_frames(self, size=None):
        size = self.e.size if size is None else size
        self.frames = [pygame.transform.scale(i, size) for i in self.o_frames]

    def __del__(self) -> None:
        del self.o_frames
        super().__del__()

class SizeAni(FuncAniBase):
    """
    Args:
        anim_to_scale (iterable?): which animations of the element to scale
            if it's None it will scale all of which are in _texture_ani
    Attrs:
        anim_to_scale (iterable?): the same as the argument

    Methods:
        get_frame (rtype: None): changes the size of the element to be _prev_val
        change_end_func (rtype: None): changes the size of the element to
            starting_val
    """
    def __init__(self,
       anim_to_scale: Optional[set] = SA.ANIMTOSCALE,
       *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = AnimType.SIZE
        self.anim_to_scale = anim_to_scale

    def get_frame(self, *args, **kwargs):
        """
        Changes the size of the element to the current frame
        Args:
            i (int?): index of the frame, if None self.frame is used
        """
        super().get_frame(*args, **kwargs)
        # If an element has a lot of animaitons, changing the size each time
        # can be very laggy
        if self._can_change:
            self.e.change_size(Size(self._prev_val), None, self.anim_to_scale)

    def start(self, auto_start_val=True):
        if auto_start_val:
            self.starting_val = self.e.size
        super().start()

    def change_end_func(self):
        """Resets the animation to the starting one"""
        self.e.change_size(Size(self.starting_val), None, self.anim_to_scale)


class PosAni(FuncAniBase):
    """
    Methods:
        get_frame (rtype: None): changes the element's position to _prev_val
        change_end_funt (rtype: None): changes the element's position to
            starting_val
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = AnimType.POS

    def get_frame(self, *args, **kwargs):
        """
        Changes the position of the element to the current frame
        Args:
            i (int?): index of the frame, if None self.frame is used
        """
        super().get_frame(*args, **kwargs)
        self.e.pos = round(self._prev_val)

    def start(self, auto_start_val=True):
        if auto_start_val:
            self.starting_val = self.e.pos
        super().start()

    def change_end_func(self):
        """Resets the postition to the starting one"""
        self.e.pos = self.starting_val


class AlphaAni(FuncAniBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = AnimType.ALPHA

    def get_frame(self, *args, **kwargs):
        super().get_frame(*args, **kwargs)
        self.e.transparency = round(self._prev_val)

    def start(self, auto_start_val=True):
        if auto_start_val:
            self.starting_val = self.e.transparency
        super().start()

    def change_end_func(self):
        self.e.transparency = self.starting_val
