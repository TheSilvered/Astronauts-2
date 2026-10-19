#!/usr/bin/env python3
from typing import Optional, Union

from .errors import InvalidPosValueError

class Pos:
    """
    A class to deal with positions more easily

    Args:
        x (float, iterable): first value of the pos or an iterable of two
            elements containing the first and second value
        y (float): second value of the position, if not set and x is a float,
            this will be equal to x

    Attrs:
        x (float): position x
        y (float): position y

    Functions:
        xa: returns itself adding "value" to x
        yx: returns itself adding "value" to y
        xay: adds "value" to x and returns it with "y"
        xya: adds "value" to y and returns it with "x"
        list: returns a list of itself
    """
    def __init__(self, x: Optional[float], y: Optional[float] = None):
        if y is None:
            self.is_good_type(x, True)
            try:
                x, y = x
            except:
                y = x

        if not isinstance(x, (int, float)):
            raise InvalidPosValueError(f"the type of x must be int or float")

        if not isinstance(y, (int, float)):
            raise InvalidPosValueError(f"the type of y must be int or float")

        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Pos{str(self)}"

    def __add__(self, other):
        if isinstance(other, (int, float)):
            x = self.x + other
            y = self.y + other
        else:
            self.is_good_type(other, False)
            x = self.x + other[0]
            y = self.y + other[1]
        return self.C(x, y)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            x = self.x - other
            y = self.y - other
        else:
            self.is_good_type(other, False)
            x = self.x - other[0]
            y = self.y - other[1]
        return self.C(x, y)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            x = self.x * other
            y = self.y * other
        else:
            self.is_good_type(other, False)
            x = self.x * other[0]
            y = self.y * other[1]
        return self.C(x, y)

    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            x = self.x // other
            y = self.y // other
        else:
            self.is_good_type(other, False)
            x = self.x // other[0]
            y = self.y // other[1]
        return self.C(x, y)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            x = self.x / other
            y = self.y / other
        else:
            self.is_good_type(other, False)
            x = self.x / other[0]
            y = self.y / other[1]
        return self.C(x, y)

    def __pow__(self, power):
        if isinstance(power, (int, float)):
            x = self.x ** power
            y = self.y ** power
        else:
            self.is_good_type(power, False)
            x = self.x ** power[0]
            y = self.y ** power[1]
        return self.C(x, y)

    def __int__(self):
        return self.C(int(self.x), int(self.y))

    def __round__(self, ndigits=None):
        return self.C(round(self.x, ndigits), round(self.y, ndigits))

    def __neg__(self):
        return self.C(-self.x, -self.y)

    def __len__(self):
        return len(self.list())

    def __getitem__(self, index):
        return self.list()[index]

    def __eq__(self, other):
        try: self.is_good_type(other)
        except: return False

        return self.x == other[0] and self.y == other[1]

    def __lt__(self, other):
        try: self.is_good_type(other)
        except: return False

        return self.x < other[0] and self.y < other[1]

    def __gt__(self, other):
        try: self.is_good_type(other)
        except: return False

        return self.x > other[0] and self.y > other[1]

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __abs__(self):
        return self.C(abs(self.x), abs(self.y))

    def xa(self, value: float):
        """
        Adds the value to x, uses the current y

        Args:
            value (float): value to add
        """
        return self.C(self.x + value, self.y)

    def ya(self, value: float):
        """
        Adds the value to y, uses the current x

        Args:
            value (float): value to add
        """
        return self.C(self.x, self.y + value)

    def xay(self, value: float, y: float):
        """
        Adds the value to x, sets a new y

        Args:
            value (float): value to add
            y (float): new value for y
        """
        return self.C(self.x + value, y)

    def xya(self, value: float, x: float):
        """
        Adds the value to y, sets a new x

        Args:
            value (float): value to add
            x (float): new value for x
        """
        return self.C(x, self.y + value)

    def list(self):
        """Retuns a list of itself"""
        return [self.x, self.y]

    @classmethod
    def C(cls, *args):
        """Creates a new instance of the current class"""
        return cls(*args)

    @staticmethod
    def is_good_type(variable, allow_nums: bool = False) -> None:
        """
        Raises an error if the passed type can't build a Pos, IntPos, Size or
        IntSize instance

        Args:
            allow_nums (bool): if integers and floats should'n raise an error
        """

        allowed_iters = (tuple, list, bytes, Pos, Size, IntPos, IntSize)

        if isinstance(variable, (int, float)) and allow_nums:
            return

        if not isinstance(variable, allowed_iters):
            raise InvalidPosValueError(f"invalid pos value: {variable}, "\
                                       f"type: {type(variable)}")

        if len(variable) != 2:
            raise InvalidPosValueError(f"invalid pos value: {variable}, "\
                                       f"type: {type(variable)}")

        if not isinstance(variable[0], (int, float)):
            raise InvalidPosValueError(f"invalid pos value: {variable}, "\
                                       f"type: {type(variable)}")

        if not isinstance(variable[1], (int, float)):
            raise InvalidPosValueError(f"invalid pos value: {variable}, "\
                                       f"type: {type(variable)}")

        return


class Size(Pos):
    """
    Has the same methods as the Pos class

    Added properties:
        w (float): width
        h (float): heigth
    """
    @property
    def w(self):
        return self.x
    @w.setter
    def w(self, value: float):
        self.x = value

    @property
    def h(self):
        return self.y
    @h.setter
    def h(self, value: float):
        self.y = value


class IntPos(Pos):
    """A Pos class that keeps x and y integers"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = int(self.x)
        self.y = int(self.y)

class IntSize(IntPos, Size):
    """A Size class that keeps w and h integers"""
    pass
