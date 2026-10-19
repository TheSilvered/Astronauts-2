#!/usr/bin/env python3
BLACK       = (0  , 0  , 0  )
WHITE       = (255, 255, 255)

# Full colors
RED         = (255, 0  , 0  )
GREEN       = (0  , 255, 0  )
BLUE        = (0  , 0  , 255)
YELLOW      = (255, 255, 0  )
CYAN        = (0  , 255, 255)
MAGENTA     = (255, 0  , 255)

# Half-full colors
MAROON      = (127, 0  , 0  )
EMERALD     = (0  , 127, 0  )
NAVY        = (0  , 0  , 127)
OLIVE       = (127, 127, 0  )
TEAL        = (0  , 127, 127)
PURPURA     = (127, 0  , 127)

# (Half-)full colors
ORANGE      = (255, 127, 0  )
LIME        = (127, 255, 0  )
AQUA        = (0  , 255, 127)
LIGHT_BLUE  = (0  , 127, 255)
PURPLE      = (127, 0  , 255)
FUCHSIA     = (255, 0  , 127)

# Others
SALMON      = (255, 127, 127)
LIGHT_GREEN = (127, 255, 127)
COBALT      = (127, 127, 255)


ColorType = tuple[int, int, int]


def GRAY(grade: int) -> ColorType:
    """Returns a color with all values eqal to grade"""
    return grade, grade, grade

def R(grade: int) -> ColorType:
    """Returns a color with the red value eqal to grade"""
    return grade, 0, 0

def G(grade: int) -> ColorType:
    """Returns a color with the green value eqal to grade"""
    return 0, grade, 0

def B(grade: int) -> ColorType:
    """Returns a color with the blue value eqal to grade"""
    return 0, grade, 0

def P(color: ColorType, percentage: float) -> ColorType:
    """Returns the color multiplied by the percentage"""
    return int(color[0] * percentage),\
           int(color[1] * percentage),\
           int(color[2] * percentage)
