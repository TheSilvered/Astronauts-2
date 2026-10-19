#!/usr/bin/env python3
class NoParentError(Exception):
    """Exception raised when an element is anchored without a parent
    or a draggable element is anchored to an element
    """
    pass


class NoPositionError(Exception):
    """Exception raised when there is no way of getting the position"""
    pass


class NoSizeError(Exception):
    """Exception raised when is impossible to resemble the size of an element"""
    pass


class NoFramesError(Exception):
    """Exception raised when there are no frames in an animation"""
    pass


class DuplicateAnimationError(Exception):
    """Exception raised when an element has two animations with the same name"""


class InvalidPosValueError(Exception):
    """Exception raised when the value of a Pos object is not valid"""
    pass
