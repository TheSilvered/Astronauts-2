#!/usr/bin/env python3
"""
Copyright [2021] [TheSilvered]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


This package is intended to be used along-side pygame, not to substitute it.

Classes:
    gameassets.animations._animationBase
    gameassets.animations._funcAnimationBase
    gameassets.animations.PosAnimation
    gameassets.animations.SizeAnimation
    gameassets.animations.TextureAnimation

    gameassets.button.Button

    gameassets.draggable.Draggable

    gameassets.element.AncType
    gameassets.element.Element
    gameassets.element.StaticElement

    gameassets.errors.InvalidPosValueError
    gameassets.errors.NoParentError
    gameassets.errors.NoPositionError
    gameassets.errors.NoFramesError

    gameassets.label.Label
    gameassets.label.StaticLabel

    gameassets.mouse_interaction.MouseInteraction

    gameassets.position.IntPos
    gameassets.position.IntSize
    gameassets.position.Pos
    gameassets.position.Size

    gameassets.slider.Slider


Functions:
    gameassets.functions.get_size
    gameassets.functions.get_possible_dim
    gameassets.functions.save_surface_to_t2
    gameassets.functions.load_surface_from_t2


Variables:

    gameassets.__init__.__author__
    gameassets.__init__.__version__


Docstring structure:

Function of the values (Args, Attrs, Methods, ...):
    value_name (type): descriprtion
    value_name (optional_type?): description
"""

__author__ = "TheSilvered"
__version__ = "Beta 0.3.2"

print(f"Game assets by {__author__}, version: {__version__}")

from .animations import *
from .button import *
from .colors import *
from .draggable import *
from .element import *
from .errors import *
from .functions import *
from .label import *
from .mouse_interaction import *
from .position import *
from .slider import *
