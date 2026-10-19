#!/usr/bin/env python3
import pygame

from .element import Element
from .position import *
from .defalut_values import *

pygame.init()


class MouseInteraction(Element):
    """
    A class that adds properties to interact with the mouse

    Args:
        button (int): the button that the mouse should be pressed with
        pressed (int): number of buttons to check when getting the buttons
            pressed valid values: 3, 5
        original_size (Size): size of the surface where the button is rendered
        scaled_size (Size): size of the surface that is then presented, if
            this doesn't match, the mouse position scaled accordingly
        scaled_offset (Pos): position of the upper-left corner of the surface
            where the button is drawn
        always_click (bool): if the element should be able to be clicked even
            whith another elemenr already clicked

    Attrs:
        _b (int): button used to press the element with
        _bp (int): buttons to check when getting the buttons pressed
        _prev_hovered (bool): if the element was hovered for at least one frame
            before being clicked
        _keep_click (bool): if the element should remain clicked
        pixel_mul (Size): scaled_size / original_size, used to calculate the
            mouse position
        always_click (bool): if the element should be able to be clicked even
            whith another elemenr already clicked

    Class variables:
        clicked_id (int, None): the id of the currently clicked object, it's
            None if no object is clicked

    Properties:
        can_be_clicked (bool): if the element can be considered clicked, always
            returns true if self.always_click is true
        hovered (bool): returns if the mouse is hovering the element
        clicked (bool): returns True if the element has been clicked with at
            least one frame of being hovered without being clicked
    """

    clicked_id = None

    def __init__(self,
       button: int = M.BUTTON,
       pressed: int = M.PRESSED,
       original_size: Size = M.ORIGINALSIZE,
       scaled_size: Size = M.SCALEDSIZE,
       scaled_offset: Pos = M.SCALEDOFFSET,
       always_click: bool = M.ALWAYSCLICK,
       *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._b = button
        self._bp = pressed
        self._prev_hovered = False
        self._keep_click = False
        self.pixel_mul = IntSize(scaled_size) // IntSize(original_size)
        self._scaled_offset = IntPos(scaled_offset)
        if self.pixel_mul == 0: self.pixel_mul = 1
        self.always_click = always_click

    @property
    def can_be_clicked(self):
        if self.always_click: return True
        return MouseInteraction.clicked_id in (id(self), None)

    @property
    def hovered(self):
        if not self.can_be_clicked:
            self._prev_hovered = False
            return False
        m_pos = (IntPos(pygame.mouse.get_pos()) - self._scaled_offset) / self.pixel_mul
        hovered = self._lu < m_pos < self._rd
        if hovered and not pygame.mouse.get_pressed(self._bp)[self._b]:
            self._prev_hovered = True
        elif not hovered:
            self._prev_hovered = False

        return hovered

    @property
    def clicked(self):
        clicked = self.hovered \
                  and pygame.mouse.get_pressed(self._bp)[self._b] \
                  and (self._prev_hovered or self._keep_click) \
                  and self.can_be_clicked
        self._keep_click = clicked
        if clicked: self._prev_hovered = False

        if self.always_click: return clicked

        if MouseInteraction.clicked_id == id(self) and not clicked:
            MouseInteraction.clicked_id = None
        elif MouseInteraction.clicked_id is None and clicked:
            MouseInteraction.clicked_id = id(self)

        return clicked


pygame.quit()
