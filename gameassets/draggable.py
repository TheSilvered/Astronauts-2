#!/usr/bin/env python3
import pygame

from typing import Optional

from .element import PosAni
from .position import Pos, IntPos
from .mouse_interaction import MouseInteraction
from .errors import NoParentError
from .defalut_values import *

pygame.init()


class Draggable(MouseInteraction):
    """
    A draggable object that follows the mouse cursor when moved
    Args:
        snap_pos (Pos?): position to which the draggable object is set after
            being released
        speed (float): speed used by the draggable to return to snap_pos, 1 is
            instantanious, anything below 1 doesn't work, 0 raises a
            ZeroDivisionError
        bounds (tuple?): the upper left and the bottom right corners of a box
            where the object has to stay

    Attributes:
        b0 (IntPos): upper-left corner of the boundary
        b1 (IntPos): bottom-right corner of the boundary
        _click (IntPos): offset from the upper-left corner of the point that
            has been clicked to drag the object
        _pending_pos_ani (str): name of the pos_animation paused when the
            draggable was being dragged
        _speed (int): speed used by the draggable to return to snap_pos
        snap_pos (IntPos): position to which the draggable object is set after
            being released
        dragging: if the object is currently dragged

    Methods:
        change_snap (rtype: None): changes the snap position
        fix_pos (rtype: None): puts the draggable back inside the boundaries
        update (rtype: None): updates it's position if dragged
        render (rtype: None): renders the element
    """
    def __init__(self,
       snap_pos: Optional[Pos] = D.SNAPPOS,
       speed: float = D.SPEED,
       bounds: Optional[tuple[Pos, Pos]] = D.BOUNDS,
       locked: bool = False,
       *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._p is not None:
            raise NoParentError("Draggable element cannot be parented")

        if bounds is not None:
            self.b0 = IntPos(bounds[0])
            self.b1 = IntPos(bounds[1])
        else:
            self.b0 = None
            self.b1 = None

        self._click = None
        self._pending_pos_ani = None

        self._speed = speed
        self.__snap_pos = None

        self._snap = None
        self.dragging = False
        self.locked = locked

        if snap_pos is not None:
            self.change_snap(snap_pos)
            self._current_ani2 = "_snap"

    @property
    def snap_pos(self):
        return self.__snap_pos

    def change_snap(self, pos: Pos) -> None:
        """
        Args:
            pos (Pos): position for snap_pos
        """
        ani = PosAni(
            name="_snap",
            frames={
                "function": lambda x: x + ((Pos(pos) - x) / self._speed),
                "frames": 1
            },
            loop=True,
            change_end=True,
            element=self,
            time=0.01
        )

        self.add_ani(ani, True)
        self.__snap_pos = pos
        if self.dragging:
            self._pending_pos_ani = "_snap"
        else:
            self._snap.start()

    def fix_pos(self) -> None:
        """Keeps the position of the draggable inside the boundaries"""
        if self.b0 is None:
            return
        if self._lu.x < self.b0.x:
            self.pos = self.pos.xya(0, self.b0.x)
        if self._lu.y < self.b0.y:
            self.pos = self.pos.xay(0, self.b0.y)
        if self._rd.x > self.b1.x:
            self.pos = self.pos.xya(0, self.b1.x - self.size.w)
        if self._rd.y > self.b1.y:
            self.pos = self.pos.xay(0, self.b1.y - self.size.h)

    def update(self) -> None:
        """Updates the position of the draggable if it's being dragged"""
        if self.clicked and self._click is None and not self.locked:
            self._click = self.pos - Pos(pygame.mouse.get_pos())
            self.dragging = True
            if self._current_ani2 is not None:
                self._pending_pos_ani = self._current_ani2
                getattr(self, self._current_ani2)._finish_end()
        elif self._click is not None \
             and pygame.mouse.get_pressed(self._bp)[self._b]:
            self.pos = IntPos(pygame.mouse.get_pos()) + self._click
        else:
            self._click = None
            self.dragging = False
            if self._pending_pos_ani is not None:
                getattr(self, self._pending_pos_ani).start()
                self._pending_pos_ani = None

    def render(self,
       surface: pygame.Surface,
       update: bool = D.RENDER.UPDATE,
       update_ani: bool = D.RENDER.UPDATEANI,
       *args, **kwargs) -> None:
        """
        Renders the texture onto the surface

        Args:
            surface (Surface): surface to blit the texture on
            update (bool): if the update() method should be called by render
            update_ani (bool): if update_ani() should be called when rendering
        """
        if update_ani:
            self.update_ani()
            self.fix_pos()
        if update:
            self.update()
            self.fix_pos()
        super().render(surface, update_ani=False, *args, **kwargs)


pygame.quit()
