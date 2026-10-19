#!/usr/bin/env python3
import pygame

from os import path
from typing import Optional

from .element import Element, StaticElement
from .colors import BLACK, ColorType
from .defalut_values import *

pygame.init()


class Label(Element):
    """A simple text label
    Args:
        text (str): the text to display
        text_size (int): the size of the text, default size is 15
        text_font (str?): the font to use to render the text
        text_style (str): defines the style of the text. Valid arguments:
            "bold", "italic", "underline" and "noaa" (no anti alias).
            You can combine these values separating them with a space.
            Ex: font_style="bold underline"
        color (tuple): color of the text to render
        tilt (int): rotation of the text in degrees, with 0 being horizontal.
            If the tilt is changed after initialization, nothing is updated
            until change_text() is called

    Attrs:
        _aa (bool): if the text is anti-aliased
        _font (font.Font): font of the label
        tilt (int): current tilt of the lable (if it was changed but
            change_text() was not called will return the new value)
        _color (tuple): color of the text
        _text (str): text of the label

    Methods:
        change_text: allows you to change the text after initialization,
          if called without specifying a new text, the text is just going to
          re-render the text (updating the tilt)
    """
    def __init__(self,
       text: str = L.TEXT,
       text_size: int = L.TEXTSIZE,
       text_font: Optional[str] = L.TEXTFONT,
       text_style: str = L.TEXTSTYLE,
       color: ColorType = L.COLOR,
       tilt: int = L.TILT,
       *args, **kwargs
       ):
        text_style = set(text_style.split())
        if text_font is not None and path.exists(text_font):
            render_font = pygame.font.Font(text_font, text_size)
        else:
            render_font = pygame.font.SysFont(text_font, text_size)
        if "bold" in text_style:
            render_font.set_bold(True)
        if "italic" in text_style:
            render_font.set_italic(True)
        if "underline" in text_style:
            render_font.set_underline(True)
        self._aa = not "noaa" in text_style
        self._font = render_font
        self.tilt = tilt
        self._color = color
        self._text = text
        texture = self._font.render(text, self._aa, self._color)
        texture = pygame.transform.rotate(texture, self.tilt)
        texture.convert_alpha()
        size = (texture.get_width(), texture.get_height())

        super().__init__(*args, **kwargs, size=size, texture=texture)

    def change_text(self,
       new_text: Optional[str] = L.CHANGETEXT.NEWTEXT) -> None:
        """
        Changes the text and upadtes the tilt

        Args:
            new_text (str?): text to change the current one to, if set to None,
                the text won't change
        """
        if new_text is None: new_text = self._text
        else: self._text = new_text
        texture = self._font.render(new_text, self._aa, self._color)
        texture = pygame.transform.rotate(texture, self.tilt)
        self.change_size((texture.get_width(), texture.get_height()))
        self.static.frames = [texture]


class StaticLabel(StaticElement, Label):
    """Label that uses the StaticElment rendering"""
    def change_text(self, *args, **kwargs) -> None:
        super().change_text(*args, **kwargs)
        self.texture, = self.static.frames


pygame.quit()
