#!/usr/bin/env python3
import pygame

from typing import Optional, Any

from .position import *
from .colors import MAGENTA
from .errors import *
from .animations import *
from .defalut_values import *

pygame.init()


class AncType:
    """
    Anchor types:
        UL: up-left
        UC: up-centre
        UR: up-right

        CL: centre-left
        CC: centre
        CR: centre-right

        DL: down-left
        DC: down-centre
        DR: down-right

    Scheme:
        UL===UC===UR
        ||   ||   ||
        CL===CC===CR
        ||   ||   ||
        DL===DC===DR
    """

    UL = "_lu"
    UC = "_cu"
    UR = "_ru"
    CL = "_cl"
    CC = "_c"
    CR = "_cr"
    DL = "_ld"
    DC = "_cd"
    DR = "_rd"


class Element (pygame.sprite.Sprite):
    """This is the basic instance of every object in the scene.

    Size is gameassets.position.Size
    Pos is gameassets.position.Pos
    Surface is pygame.Surface
    Element is gameassets.element.Element
    AncType is gameassets.element.AncType

    Anything that accept Pos or Size as a parameter accepts:
        tuple[int, int], list[int, int], bytes (length 2), IntPos, IntSize, Pos,
        Size, float, int

    Args:
        pos (Pos?): position of the upper left corner, if set c_pos is ignored
        c_pos (Pos?): position of the center
        size (Size?): size of the element
        c_size (Size?): size from the centre of the element
        texture (Surface?): texture of the element
        parent (Element?): element to which this instance is anchored to
        anchor (AncType): anchored position of the upper left corner, if set
            c_anchor is ignored
        c_anchor (AncType): anchored position of the centre
        offset (Pos): offset of the anchoring
        animations (list?): list of animation instances already initialized
        texture_ani (dict?): dictionary of kwargs to create a TextureAni
            instance, more on this later
        size_ani (dict?): dictionary of kwargs to create a SizeAni
            instance, more on this later
        pos_ani (dict?): dictionary of kwargs to create a PosAni instance,
            more on this later
        alpha_ani (dict?): dictionary of kwargs to create an AlphaAni instance,
            more on this later
        transparency (int): transparency of the element where 0 is fully
            transparent and 255 fully visible, if set to 0 self.visible will
            return False
        visible (bool): if the element is visible

    Attrs:
        size (Size): size of the element
        _anc (bool): if the element is anchored
        _c_anc (bool): if the element is c_anchored
        _anc_type (str): the type of anchoring, names differs from the names of
            the AncType class
        offset (Pos): offset of the element
        _p (Element?): parent of the element
        _c_pos (Pos): position of the centre of the element, is None if c_pos is
            not given upon initialization
        _pos (Pos): position of the upper left corner of the element, is set
            even if pos is not set but c_pos is, it's None if the element is
            anchored
        visible (bool): if the element is currently visible
        _current_ani0 (str?): name of the TextureAni that is currently being
            played, never none, if no animation is started returns "static"
        _current_ani1 (str?): name of the SizeAni that is currently being
            played, is None if no animation is playing
        _current_ani2 (str?): name of the PosAni that is currently being played,
            is None if no animation is playing
        _texure_ani (list): names of the texture animations of the element
        transparency (int): current transparency of the element

        Other attributes are all the animations of the element. An animation
        called "static" is always generated and can be overwritten with an
        animation that has the same name

    Properties:
        x (int): x position of the upper left corner of the element
        y (int): y position of the upper left corner of the element
        pos (Pos): position of the upper left corner of the element
        w (int): width of the element
        h (int): height of the element
        _l (int): exactly like gameassets.element.Element.x
        _u (int): exactly like gameassets.element.Element.y
        _r (int): x position of the right side of the element
        _d (int): y position of the bottom side of the element
        _c (Pos): position of the centre
        _lu (Pos): left-up position of the element
        _ld (Pos): left-down position of the element
        _ru (Pos): right-up position of the element
        _rd (Pos): right-down position of the element
        _cu (Pos): centre-up position of the element
        _cd (Pos): centre-down position of the element
        _cl (Pos): centre-left position of the element
        _cr (Pos): centre-right position of the element

    Methods:
        pos_as (rtype: Pos): returns the position of the element if it had a
            certain size (it differs from gameassets.element.Element.pos if
            c_pos or c_anchor were set instead of pos or anchor)
        colliding (rtype: bool): returns if the element is colliding with
            another element
        change_size (rtype: None): changes the size of the element and of all
            the animations inside Element._texture_ani
        add_ani (rtype: None): adds an animation from an already initialized one
        add_ani_from_dict (rtype: None): adds a single type of animation
            from a dictionary that follows the same rules as texture_ani,
            size_ani and pos_ani arguments
        update_ani (rtype: None): updates the animations, if there is a PosAni
            running, the position is changed
        get_texture (rtype: Surface): returns the current texture of the
            element after updating all the animations running
        render (rtype: None): draws the current texture at the specified
            position (if not set the surface blits at the element's position)
            and with an optional offset

    Animations dictionaries contain the name of the animation as the key to
    another dictionary that contains all the keyword arguments.
    Example for texture_ani:
        texture_ani = {
            "walk": {
                "frames": [walk1, walk2],
                "loop": True,
                "time": 0.01
            },
            "jump_start": {
                "frames": [jmp_start, jmp_air],
                "loop": False,
                "time": 0.01
            },
            "jump_air": {
                "frames": [jmp_air],
                "loop": True
            },
            "jump_end": {
                "frames": [jmp_air, jmp_end],
                "loop": False,
                "time": 0.01
            }
        }
    Now you can call Element.walk.start() to start the walking animation,
    similarly you can call Element.jump_start.start() etc.
    """

    def __init__(self,
       pos: Optional[Pos] = E.POS,
       c_pos: Optional[Pos] = E.CPOS,
       size: Optional[Size] = E.SIZE,
       c_size: Optional[Size] = E.CSIZE,
       texture: Optional[pygame.Surface] = E.TEXTURE,
       parent: Any = E.PARENT,
       anchor: str = E.ANCHOR,
       c_anchor: str = E.CANCHOR,
       offset: Pos = E.OFFSET,
       animations: Optional[list] = E.ANIMATIONS,
       texture_ani: Optional[dict] = E.TEXTUREANI,
       size_ani: Optional[dict] = E.SIZEANI,
       pos_ani: Optional[dict] = E.POSANI,
       alpha_ani: Optional[dict] = E.ALPHAANI,
       transparency: int = E.TRANSPARENCY,
       visible: bool = E.VISIBLE):
        pygame.sprite.Sprite.__init__(self)
        if parent is None and (anchor != "" or c_anchor != ""):
            raise NoParentError("element anchored without parent")

        if pos is None and c_pos is None and parent is None:
            raise NoPositionError("element missing one positional argument")

        if size is None and c_size is None:
            size = (0, 0)

        if size is not None:
            self.__size = IntSize(size)
        else:
            self.__size = IntSize(c_size) * 2

        if texture is None:
            texture = pygame.Surface((2, 2))
            texture.set_at((0, 0), MAGENTA)
            texture.set_at((1, 1), MAGENTA)

        if self.__size != (0, 0):
            texture = pygame.transform.scale(texture, self.__size)
        else:
            texture = texture
            self.__size = IntSize(texture.get_width(), texture.get_height())

        self._anc = False
        self._c_anc = False
        self._anc_type = ""
        self.offset = Pos(offset)
        self._p = parent
        self._c_pos = Pos(c_pos) if c_pos is not None else None
        if pos is not None:
            self._pos = Pos(pos)
        elif c_pos is not None:
            self._pos = Pos(c_pos) - self.__size/2
        elif anchor != "":
            self._pos = None
            self._anc = True
            self._anc_type = anchor
        elif c_anchor != "":
            self._pos = None
            self._c_anc = True
            self._anc_type = c_anchor

        self.__transparency = transparency

        self.visible = visible if transparency != 0 else False

        if texture_ani is None: texture_ani = {"static": {"frames": [texture]}}

        if animations is None: animations = []
        if size_ani is None: size_ani = {}
        if pos_ani is None: pos_ani = {}
        if alpha_ani is None: alpha_ani = {}

        if "static" not in texture_ani:
            texture_ani["static"] = {"frames": [texture]}

        texture_ani["static"]["loop"] = True

        self._texture_ani = set()


        for i in animations:
            if i.name == "static": del texture_ani["static"]
            self.add_ani(i)

        self.add_ani_from_dict(texture_ani, TextureAni)
        self.add_ani_from_dict(size_ani   , SizeAni   )
        self.add_ani_from_dict(pos_ani    , PosAni    )
        self.add_ani_from_dict(alpha_ani  , AlphaAni  )

        for i in range(AnimType.tf[1]):
            setattr(self, f"_current_ani{i}", None)

        # Necessary for a pygame.sprite.Sprite instance
        self.image = texture
        self.rect = pygame.Rect(self.pos, self.size)

        self.static.start()

    def __del__(self):
        for i in dir(self):
            try:
                delattr(self, i)
            except (TypeError, AttributeError):
                pass
        del self

    @property
    def x(self):
        return self.pos.x
    @x.setter
    def x(self, value: int):
        self.pos = (value, self.pos.y)

    @property
    def y(self):
        return self.pos.y
    @y.setter
    def y(self, value: int):
        self.pos = (self.pos.x, value)

    @property
    def pos(self):
        if self._pos is not None:
            return round(self._pos)
        elif self._anc:
            return getattr(self._p, self._anc_type) + self.offset
        else:
            return getattr(self._p, self._anc_type) - self.size/2 + self.offset
    @pos.setter
    def pos(self, value: Pos):
        value = Pos(value)

        if self._anc or self._c_anc:
            self.offset = value - self.pos
        else:
            self._pos = value

        if self._c_pos is not None:
            self._c_pos = self._pos + self.size / 2

        self.rect.topleft = self.pos


    @property
    def transparency(self):
        return self.__transparency
    @transparency.setter
    def transparency(self, value: int):
        if value <= 0:
            self.visible = False
            value = 0
        else:
            self.visible = True

        if value > 255:
            value = 255

        self.__transparency = value

    def pos_as(self, size: Size) -> Pos:
        """
        Calculates the position of upper-left corner the object if it had
        a certain size, without actually changing it

        Args:
            size (Size): size to use for the comparison
        """
        if self._c_pos is not None:
            return self._c_pos - size/2
        elif self._c_anc:
            return getattr(self._p, self._anc_type) - size/2 + self.offset
        else:
            return self.pos

    @property
    def size(self):
        return self.__size

    @property
    def w(self):
        return self.size.w

    @property
    def h(self):
        return self.size.h

    @property
    def _l(self): return round(self.pos.x)
    @property
    def _u(self): return round(self.pos.y)
    @property
    def _r(self): return round(self.pos.x + self.w)
    @property
    def _d(self): return round(self.pos.y + self.h)
    @property
    def _c(self): return round(self.pos + self.size/2)
    @property
    def _lu(self): return IntPos(self._l, self._u)
    @property
    def _ld(self): return IntPos(self._l, self._d)
    @property
    def _ru(self): return IntPos(self._r, self._u)
    @property
    def _rd(self): return IntPos(self._r, self._d)
    @property
    def _cu(self): return IntPos(self._c.x, self._u)
    @property
    def _cd(self): return IntPos(self._c.x, self._d)
    @property
    def _cl(self): return IntPos(self._l, self._c.y)
    @property
    def _cr(self): return IntPos(self._r, self._c.y)

    def colliding(self, other: pygame.sprite.Sprite) -> bool:
        """
        Checks for collisions with elements, sprites, rects or groups

        Args:
            other (pygame.sprite.Sprite, pygame.sprite.Group, pygame.Rect):
                the object of which the collisions are checked
        """
        if isinstance(other, pygame.sprite.Sprite):
            return bool(self.rect.colliderect(other.rect))
        elif isinstance(other, pygame.Rect):
            return bool(self.rect.colliderect(other))
        elif isinstance(other, pygame.sprite.Group):
            r = pygame.sprite.spritecollideany(self, other)
            if r is None: return False
            else:         return True

    def change_size(self,
       size: Optional[Size] = E.CHANGESIZE.SIZE,
       c_size: Optional[Size] = E.CHANGESIZE.CSIZE,
       anim_to_scale: Optional[set] = E.CHANGESIZE.ANIMTOSCALE) -> None:
        """
        Changes the size of the element

        Args:
            size (Size?): size to set the element to
            c_size (Size?): size from the centre to set the element to
            anim_to_scale (iterable?): the names of the animations to scale,
                if set to None all of them will be scaled
        """

        if size is None and c_size is None:
            return

        if size is not None:
            self.__size = IntSize(size)
        elif c_size is not None:
            self.__size = IntSize(c_size) * 2
        else:
            return

        if self._c_pos is not None:
            self.pos = self._c_pos - self.__size/2

        if anim_to_scale is None:
            anim_to_scale = self._texture_ani

        if self.__size != (0, 0):
            for i in anim_to_scale:
                getattr(self, i).scale_frames()

        self.rect.size = self.size

    def add_ani(self,
       ani: (TextureAni, SizeAni, PosAni),
       overwrite: bool = E.ADDANI.OVERWRITE,
       add_to_texture_ani: bool = E.ADDANI.ADDTOTEXTUREANI) -> None:
        """
        Adds an animation to the element

        Args:
            ani (TextureAni, SizeAni, PosAni, ...): the animation to add
            overwrite (bool): if an animation with the same name is found,
                set it anyway
            add_to_texture_ani (bool): if the animation is a texture animation,
                should it be added to self._texture_ani
        """
        ani.e = self
        if hasattr(self, ani.name) and not overwrite:
            raise DuplicateAnimationError(f"Duplicate name: {ani.name}")
        if ani.type == AnimType.TEXTURE and add_to_texture_ani:
            self._texture_ani.add(ani.name)
        setattr(self, ani.name, ani)

    def add_ani_from_dict(self,
       ani: dict,
       ani_class: (TextureAni, SizeAni, PosAni),
       overwrite: bool = E.ADDANIFROMDICT.OVERWRITE,
       add_to_texture_ani: bool = E.ADDANIFROMDICT.ADDTOTEXTUREANI) -> None:
        """
        Adds more animations of the same type from a dictionary

        Args:
            ani (dict): dictionary containing all the animations, the key is
                the name of the animation that refers to another dictionary
                containing the keyword arguments, see
                gameassets.element.Element.__doc__ for an example
            ani_class (TextureAni, SizeAni, PosAni): class used to build the
                animation from the dictionary, all the animations have the
                same class
            overwrite (bool): if an animation with the same name is found,
                set it anyway
            add_to_texture_ani (bool): if the animation is a texture animation,
                should it be added to self._texture_ani
        """
        for i in ani:
            if "frames" not in ani[i]:
                raise NoFramesError(f"Animation {i!r} has no frames")
            if hasattr(self, i):
                raise DuplicateAnimationError(f"Duplicate name: {i}")
            setattr(self, i, ani_class(name=i, element=self, **ani[i]))
            if ani_class is TextureAni and add_to_texture_ani:
                self._texture_ani.add(i)

    def update_ani(self):
        """Call next() for every running animation, calls get_frame() for any
        functional animation
        """
        if self._current_ani0 is not None:
            getattr(self, self._current_ani0).next()
        else:
            self.static.next()

        for i in range(*AnimType.f):
            ani_name = getattr(self, f"_current_ani{i}")
            if ani_name is None: continue
            getattr(self, ani_name).get_frame()
            getattr(self, ani_name).next()

        for i in range(*AnimType.tf):
            ani_name = getattr(self, f"_current_ani{i}")
            if ani_name is None: continue
            getattr(self, ani_name).next()

    def get_texture(self,
       update: bool = E.GETTEXTURE.UPDATE,
       skip_texture_func_ani: Optional[list] = None) -> pygame.Surface:
        """
        Returns the current texture of the element, returns the texture of an
        animation if it is running

        Args:
            update (bool): if the animations should be updated
            skip_texture_func_ani (bool): which texture-functional animations
                should be skipped (valid numbers: 0, 1, 2)
        """
        if update: self.update_ani()
        if skip_texture_func_ani is None:
            skip_texture_func_ani = []

        for i in range(AnimType.tf[1] - 1, AnimType.tf[0] - 1, -1):
            if i - AnimType.tf[0] in skip_texture_func_ani:
                continue
            ani_name = getattr(self, f"_current_ani{i}")
            if ani_name is None:
                continue
            return getattr(self, ani_name).get_frame()

        if self._current_ani0 is not None:
            return getattr(self, self._current_ani0).get_frame()
        else:
            return self.static.get_frame()

    def render(self,
       surface: pygame.Surface,
       pos: Optional[Pos] = E.RENDER.POS,
       offset: Pos = E.RENDER.OFFSET,
       update_ani: bool = E.RENDER.UPDATEANI) -> None:
        """
        Renders the element to the surface

        Args:
            surface (Surface): the surface where the element should be drawn
            pos (Pos?): the position at which the element should be drawn,
                deafaults to the element's position
            offset (Pos): offset from the position, defaults to Pos(0, 0)
            update_ani (bool): if when calling get frame update_ani() should be
                called
        """
        frame = self.get_texture(update_ani)
        frame.set_alpha(self.transparency)

        if not self.visible: return

        if pos is None:
            pos = self.pos_as(Size(frame.get_width(), frame.get_height()))
        surface.blit(frame, pos + IntPos(offset))
        # pygame.draw.rect(surface, MAGENTA, self.rect)


class StaticElement(Element):
    """
    Element class that doesn't use animations, better for performance.
    The texture of the element is the texture argument.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.texture = self.static.frames[0]

    def render(self,
       surface: pygame.Surface,
       pos: Pos = SE.RENDER.POS,
       offset: Pos = SE.RENDER.OFFSET) -> None:
        if not self.visible: return
        self.texture.set_alpha(self.transparency)
        if pos is None:
            pos = self.pos
        surface.blit(self.texture, pos + IntPos(offset))


pygame.quit()
