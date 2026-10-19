import random
import time

import pygame
import gameassets as ga

from constants import PIXEL, TILE_SIZE, LEVEL_OFFSET_LEFT, \
                      LEVEL_OFFSET_RIGHT, LEVEL_SIZE
from assets_import import IDLE, WALK1, WALK2, JUMP, LAND, DEATH

scaling = TILE_SIZE.x / 16

player_speed = 4 * scaling
falling_speed = 10 * scaling
gravity = .44 * scaling
jump_height = 6 * scaling
decel = 1.4
air_decel = 1.05
accel = 1.0 * scaling


class Physics(ga.FuncAniBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = ga.AnimType.FUNC2

        def collision_function(x):
            self.e.speed.y += gravity * self.e.grav

            keys = pygame.key.get_pressed()

            up_key = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
            right_key = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            left_key = keys[pygame.K_LEFT] or keys[pygame.K_a]

            if right_key and not left_key and self.e.in_game:
                # Makes changing direction instantaneous
                if self.e.speed.x * self.e.grav < 0: self.e.speed.x = 0

                if self.e.can_jump: self.e.speed.x += accel * self.e.grav
                else: self.e.speed.x += accel * self.e.grav / 10

            elif left_key and not right_key and self.e.in_game:
                # Makes changing direction instantaneous
                if self.e.speed.x * self.e.grav > 0: self.e.speed.x = 0

                if self.e.can_jump: self.e.speed.x -= accel * self.e.grav
                else: self.e.speed.x -= accel * self.e.grav / 3

            else:
                if self.e.can_jump: self.e.speed.x /= decel
                else:               self.e.speed.x /= air_decel

            if   self.e.speed.x > 0: self.e.facing = "right"
            elif self.e.speed.x < 0: self.e.facing = "left"

            if abs(self.e.speed.x) > player_speed:
                if self.e.speed.x > 0: self.e.speed.x = player_speed
                else:                  self.e.speed.x = -player_speed

            if abs(self.e.speed.y) > falling_speed:
                if self.e.speed.y > 0: self.e.speed.y = falling_speed
                else:                  self.e.speed.y = -falling_speed

            if abs(self.e.speed.x) >= player_speed / 2:
                if self.e.can_jump: self.e.walk.start()
                else:               self.e.walk.end()
            else: self.e.walk.end()

            if up_key and \
               self.e.can_jump and \
               self.e.is_jump_reset and \
               self.e.in_game:
                self.e.speed.y = -jump_height * self.e.grav
                self.e.jump.start()
                self.e.is_jump_reset = False
            elif not keys[pygame.K_UP]:
                self.e.is_jump_reset = True

            self.e.x += round(self.e.speed.x)
            for layer in self.e.level.solid:
                if self.e.colliding(layer):
                    while self.e.colliding(layer):
                        self.e.x += 1 if self.e.speed.x < 0 else -1
                    self.e.speed.x = 0
                    break

            self.e.y += round(self.e.speed.y)
            for layer in self.e.level.solid:
                if self.e.colliding(layer):
                    self.e.can_jump = True
                    while self.e.colliding(layer):
                        self.e.y += 1 if self.e.speed.y < 0 else -1
                    self.e.speed.y = 0
                    break
                else: self.e.can_jump = False

            if self.e.speed.y * self.e.grav > falling_speed / 8:
                self.e.land.start()
            else:
                self.e.land.end()

            if self.e.speed.y * self.e.grav < -falling_speed:
                self.e.jump.start()
            else:
                self.e.jump.end()

            self.e.damage_hitbox.rect.x = self.e.rect.x + 2*PIXEL
            self.e.damage_hitbox.rect.y = self.e.rect.y

            for layer in self.e.level.damaging:
                if pygame.sprite.spritecollideany(self.e.damage_hitbox, layer):
                    self.e.die()


        self.frames = {
            "function": collision_function,
            "frames": 1
        }
        self.loop = True
        self.reset_on_loop = False
        self.change_end = True
        self.time = 0.01

    def change_end_func(self):
        pass


class DeathAni(ga.TextureFuncAniBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = ga.AnimType.TFUNC1

        def death(x):
            self.e.pos += self.e.speed
            self.e.speed.y += gravity * self.e.grav / 1.7
            return x - 5

        self.frames = {
            "function": death,
            "frames": 90
        }
        self.time = 0.005
        self.starting_val = 0
        # self.loop = True
        # self.reset_on_loop = False

    def start(self):
        self.e.speed = ga.Pos(random.randint(-5, 5), -jump_height * self.e.grav)
        if self.e.speed.x == 0: self.e.speed.x = 1
        super().start()

    def get_frame(self, *args, **kwargs):
        super().get_frame(*args, **kwargs)
        frame = self.get_element_frame()
        return pygame.transform.rotate(frame, self._prev_val)


class FlipTexture(ga.TextureFuncAniBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = ga.AnimType.TFUNC2
        self.frames = {
            "function": lambda x: x,
            "frames": 1
        }
        self.loop = True
        self.time = 0.01

    def get_frame(self, *args, **kwargs):
        super().get_frame(*args, **kwargs)
        texture = self.get_element_frame()
        if self.e.facing == "left":
            texture = pygame.transform.flip(texture, True, False)

        if not self.e.grav + 1:
            texture = pygame.transform.flip(texture, False, True)

        return texture


class EnterDoorAni(ga.TextureFuncAniBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = ga.AnimType.TFUNC3

        def shrink_func(x):
            size = x - x // (5 - self.frame)
            if size == (0, 0):
                self.e.visible = False
                return self.starting_val
            return size

        self.frames = {
            "function": shrink_func,
            "frames": 5
        }

        self.time = 0.01

    def start(self):
        if not self.ended: return
        self.starting_val = self.e.size
        super().start()

    def get_frame(self, *args, **kwargs):
        super().get_frame(*args, **kwargs)
        self.e.change_size(self._prev_val)
        return self.get_element_frame()
        # return pygame.transform.rotate(self.get_element_frame(), self.frame * 10)

    def _finish_end(self):
        super()._finish_end()
        self.e.pos = -self.e.size


class DamageHitbox(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.rect = pygame.Rect(0, 0, PIXEL*9, PIXEL*15)


class Player(ga.Draggable):
    def __init__(self, level, grav, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_jump = False
        self.is_jump_reset = True
        self.speed = ga.Pos(0)
        self.level = level
        self.grav = grav
        self.starting_bounds = [self.b0, self.b1]
        self.starting_grav = grav
        self.facing = "right" if self.grav + 1 else "left"
        self.dead = False
        self.add_ani(Physics(name="physics", frames={}))
        self.add_ani(FlipTexture(name="flip_texture", frames={}))
        self.add_ani(DeathAni(name="death", frames={}))
        self.add_ani(EnterDoorAni(name="shrink", frames={}))
        self.add_ani_from_dict(
            {
                "walk": {
                    "frames": [WALK1, WALK2],
                    "time": 0.1,
                    "loop": True
                },
                "jump": {
                    "frames": [JUMP, IDLE],
                    "time": 0.2
                },
                "land": {
                    "frames": [LAND],
                    "loop": True
                }
            },
            ga.TextureAni
        )
        self.physics.start()
        self.flip_texture.start()
        self.damage_hitbox = DamageHitbox()
        self.in_game = False
        self.death_sound_start = time.time()

    def reset(self):
        self.death._finish_end()
        self.shrink._finish_end()
        self.change_size((PIXEL*13, PIXEL*15))
        self.speed = ga.Pos(0)
        self.facing = "right" if self.starting_grav + 1 else "left"
        self.physics._finish_end()
        self.physics.start()
        self.flip_texture.start()
        self.grav = self.starting_grav
        self.dead = False
        self.pos = self.level.player_starting_pos
        self.visible = True
        self.in_game = True
        self.b0 = self.starting_bounds[0]
        self.b1 = self.starting_bounds[1]
        self.locked = True

    def die(self):
        if DEATH.get_length() + 0.2 < time.time() - self.death_sound_start:
            self.death_sound_start = time.time()
            pygame.mixer.Sound.play(DEATH)
        if not self.locked: return
        self.physics._finish_end()
        self.can_jump = False
        self.death.start()
        self.dead = True
        self.b0 = None
        self.b1 = None

    def enter_door(self):
        self.physics._finish_end()
        self.shrink.start()
        self.b0 = None
        self.b1 = None

    def flip_grav(self):
        if self.dead: return
        self.grav *= -1


    def render(self, *args, **kwargs):
        super().render(*args, **kwargs)
        if self.dragging: self.damage_hitbox.topleft = self.pos + (PIXEL * 2, 0)


player1 = Player(
    level=None,
    grav=1,
    c_pos=(0, 0),
    size=(PIXEL*13, PIXEL*15),
    texture=IDLE,
    # locked=True,
    bounds=[LEVEL_OFFSET_LEFT, LEVEL_OFFSET_LEFT + LEVEL_SIZE]
)

player2 = Player(
    level=None,
    grav=-1,
    c_pos=(0, 0),
    size=(PIXEL*13, PIXEL*15),
    texture=IDLE,
    # locked=True,
    bounds=[LEVEL_OFFSET_RIGHT, LEVEL_OFFSET_RIGHT + LEVEL_SIZE]
)
