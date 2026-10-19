#!/usr/bin/env python3
import pygame

from .position import IntSize

pygame.init()


def get_size(surface) -> IntSize:
    """
    Returs the size of a pygame surface as a IntSize instance

    Args:
        surface (Surface): surface to get the size of
    """
    return IntSize(surface.get_width(), surface.get_height())


def get_possible_dim(buffer: bytes) -> list[tuple[int, int]]:
    """
    Returs the possible dimensions of a buffer texture

    Args:
        buffer (bytes): buffer to get the pixel size of
    """
    size = len(buffer)
    print(size)
    size //= 4

    dims = [(x, size // x) for x in range(1, size) if size // x == size / x]
    return dims


def save_surface_to_t2(surface, path: str) -> None:
    w = surface.get_width()
    h = surface.get_height()

    bw = w.to_bytes((w.bit_length()+7) // 8, byteorder="big")
    bh = h.to_bytes((h.bit_length()+7) // 8, byteorder="big")

    with open(f"{path}.t2", "wb") as t2:
        t2.write(((w.bit_length()+7) // 8).to_bytes(1, byteorder="big"))
        t2.write(((h.bit_length()+7) // 8).to_bytes(1, byteorder="big"))
        t2.write(bw)
        t2.write(bh)
        t2.write(pygame.image.tostring(surface, "RGBA"))


def load_surface_from_t2(path: str) -> pygame.Surface:
    with open(f"{path}.t2", "rb") as t2:
        info = t2.read()

    wb = info[0]
    hb = info[1]

    w = int.from_bytes(info[2:wb + 2], byteorder="big")
    h = int.from_bytes(info[2 + wb:hb + 2 + wb], byteorder="big")

    return pygame.image.frombuffer(info[2 + wb + hb:], (w, h), "RGBA")


pygame.quit()
