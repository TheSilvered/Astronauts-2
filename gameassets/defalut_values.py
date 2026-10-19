#!/usr/bin/env python3
from .colors import *
from .position import *

"""
AB -> gameassets.animations._aniBase
FAB -> gameassets.animations._funcAniBase
TA -> gameassets.animations.TextureAni
SA -> gameassets.animations.SizeAni
B -> gameassets.button.Button
D -> gameassets.draggable.Draggable
E -> gameassets.element.Element
SE -> gameassets.element.StaticElement
L -> gameassets.label.Label
M -> gameassets.mouse_interaction.MouseInteraction
S -> gameassets.slider.Slider

Nomenclature:
[class name].[arg name]
[class name].[method name].[arg name]
[class name].[method name].[constant name]
"""

class AB:
    E = None
    TIME = 0
    LOOP = False
    TYPE = None


class FAB:
    CHANGEEND = False
    STARTINGVAL = False
    RESETONLOOP = True


class TA:
    SCALE = True


class SA:
    ANIMTOSCALE = None


class B:
    TN = None
    TH = None
    TC = None
    CN = ( 0, 153, 255)
    CH = (33, 166, 255)
    CC = ( 0, 132, 219)
    MAKETEXTURE = True
    CURVE = 0
    HALO = 0
    OLDHALO = 0
    HALOINTENSITY = 1
    HALOMUL = 1
    HALOCN = (6, 0, 59)
    HALOCH = (33, 166, 255)
    HALOCC = ( 0, 132, 219)
    HALOOFFSET = Pos(0)
    BRUSHSIZE = 10
    EDGE = 0
    EDGECN = None
    EDGECH = None
    EDGECC = None
    SOUND = None
    TEXTKWARGS = None
    TEXTUREDEBUG = False
    FUNCTION = None
    FARGS = None
    FKWARGS = None

    class TEXTURE:
        IMAGE = None

    class BUFFERTEXTURE:
        TH = None
        TC = None

    class RENDER:
        FORCEN = False
        FORCEH = False
        FORCEC = False
        POS = None
        OFFSET = Pos(0)
        UPDATE = True


class D:
    SNAPPOS = None
    SPEED = 2
    BOUNDS = None

    class RENDER:
        UPDATE = True
        UPDATEANI = True


class E:
    POS = None
    CPOS = None
    SIZE = None
    CSIZE = None
    TEXTURE = None
    PARENT = None
    ANCHOR = ""
    CANCHOR = ""
    OFFSET = Pos(0)
    ANIMATIONS = None
    TEXTUREANI = None
    SIZEANI = None
    POSANI = None
    ALPHAANI = None
    TRANSPARENCY = 255
    VISIBLE = True

    class CHANGESIZE:
        SIZE = None
        CSIZE = None
        ANIMTOSCALE = None

    class ADDANI:
        OVERWRITE = False
        ADDTOTEXTUREANI = True

    class ADDANIFROMDICT(ADDANI):
        OVERWRITE = False
        ADDTOTEXTUREANI = True

    class GETTEXTURE:
        UPDATE = True

    class RENDER:
        POS = None
        OFFSET = Pos(0)
        UPDATEANI = True


class SE:
    class RENDER:
        POS = E.RENDER.POS
        OFFSET = E.RENDER.OFFSET


class L:
    TEXT = ""
    TEXTSIZE = 15
    TEXTFONT = None
    TEXTSTYLE = ""
    COLOR = WHITE
    TILT = 0

    class CHANGETEXT:
        NEWTEXT = None


class M:
    BUTTON = 0
    PRESSED = 3
    ORIGINALSIZE = Size(1)
    SCALEDSIZE = Size(1)
    SCALEDOFFSET = Pos(0)
    ALWAYSCLICK = False


class S:
    INDICATORCLASS = None
    BARCLASS = None
    MINVALUE = 0
    MAXVALUE = 1
    INDICATORPOS = None
    ARGNUM = 0
    SNAPSPEED = D.SPEED
