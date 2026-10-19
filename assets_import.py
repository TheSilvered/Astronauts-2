import pygame
import os.path

from constants import SIZE, TILE_SIZE, LOCAL_DIR

pygame.init()


def load_image(path, has_alpha=False):
    img = pygame.image.load(os.path.join(LOCAL_DIR, path))
    if has_alpha:
        img.convert_alpha()
    else:
        img.convert()
    return img


checkbox_image_size = (int(min(SIZE.h, SIZE.w) // 16), int(min(SIZE.h, SIZE.w) // 16))
arrow_size = (int(min(SIZE.h, SIZE.w) // 27), int(min(SIZE.h, SIZE.w) // 27))

# ---------------------- TEXTURES ----------------------

# Player
IDLE  = load_image("assets/textures/player/still.png")
WALK1 = load_image("assets/textures/player/walk_1.png")
WALK2 = load_image("assets/textures/player/walk_2.png")
JUMP  = load_image("assets/textures/player/jump.png")
LAND  = load_image("assets/textures/player/land.png")

# Door frame
DOOR_FRAME = load_image("assets/textures/door/frame.png", True)
DOOR_FRAME = pygame.transform.scale(DOOR_FRAME, TILE_SIZE * (4, 3))
DOOR_FRAME_FLIPPED = load_image("assets/textures/door/frame_flipped.png", True)
DOOR_FRAME_FLIPPED = pygame.transform.scale(DOOR_FRAME_FLIPPED, TILE_SIZE * (4, 3))

# Door
DOOR_ANI_0 = load_image("assets/textures/door/door_opening_0.png")
DOOR_ANI_1 = load_image("assets/textures/door/door_opening_1.png")
DOOR_ANI_2 = load_image("assets/textures/door/door_opening_2.png")
DOOR_ANI_3 = load_image("assets/textures/door/door_opening_3.png")
DOOR_ANI_4 = load_image("assets/textures/door/door_opening_4.png")

# Buttons
BACK_BUTTON = load_image("assets/textures/buttons/back.png")
BACK_BUTTON = pygame.transform.smoothscale(BACK_BUTTON, (int(SIZE.w/9.84), int(SIZE.w/32)))
CLOSE_BUTTON = load_image("assets/textures/buttons/close.png")
CLOSE_BUTTON = pygame.transform.smoothscale(CLOSE_BUTTON, (int(SIZE.w // 32), int(SIZE.w // 32)))
MINIMIZE_BUTTON = load_image("assets/textures/buttons/minimize.png")
MINIMIZE_BUTTON = pygame.transform.smoothscale(MINIMIZE_BUTTON, (int(SIZE.w // 32), int(SIZE.w // 32)))
LEFT_ARROW = load_image("assets/textures/buttons/left_arrow.png")
LEFT_ARROW = pygame.transform.smoothscale(LEFT_ARROW, checkbox_image_size)
RIGHT_ARROW = load_image("assets/textures/buttons/right_arrow.png")
RIGHT_ARROW = pygame.transform.smoothscale(RIGHT_ARROW, checkbox_image_size)
UP_ARROW = load_image("assets/textures/buttons/up_arrow.png")
UP_ARROW = pygame.transform.smoothscale(UP_ARROW, arrow_size)
DOWN_ARROW = load_image("assets/textures/buttons/down_arrow.png")
DOWN_ARROW = pygame.transform.smoothscale(DOWN_ARROW, arrow_size)
SAVE_ICON = load_image("assets/textures/buttons/save.png")
SAVE_ICON = pygame.transform.smoothscale(SAVE_ICON, checkbox_image_size)
OPEN_ICON = load_image("assets/textures/buttons/open.png")
OPEN_ICON = pygame.transform.smoothscale(OPEN_ICON, checkbox_image_size)
NEW_ICON = load_image("assets/textures/buttons/new.png")
NEW_ICON = pygame.transform.smoothscale(NEW_ICON, checkbox_image_size)
UNDO_ICON = load_image("assets/textures/buttons/undo.png")
UNDO_ICON = pygame.transform.smoothscale(UNDO_ICON, checkbox_image_size)
REDO_ICON = load_image("assets/textures/buttons/redo.png")
REDO_ICON = pygame.transform.smoothscale(REDO_ICON, checkbox_image_size)
DEL_ICON  = load_image("assets/textures/buttons/delete.png")
DEL_ICON = pygame.transform.smoothscale(DEL_ICON, checkbox_image_size)
THUMBNAIL_ICON  = load_image("assets/textures/buttons/make_thumbnail.png")
THUMBNAIL_ICON = pygame.transform.smoothscale(THUMBNAIL_ICON, checkbox_image_size)
BACK2_ICON  = load_image("assets/textures/buttons/back2.png")
BACK2_ICON = pygame.transform.smoothscale(BACK2_ICON, checkbox_image_size)

# Other
NO_BLOCK = load_image("assets/textures/misc/no_block.png")
NO_BLOCK = pygame.transform.smoothscale(NO_BLOCK, TILE_SIZE * 2)
BLOCK_SELECTED = load_image("assets/textures/misc/block_selected.png")
BLOCK_SELECTED = pygame.transform.smoothscale(BLOCK_SELECTED, TILE_SIZE)

# ---------------------- SOUNDS ----------------------
SWITCH_GRAV = pygame.mixer.Sound(os.path.join(LOCAL_DIR, "assets/sfx/gravity_switch.wav"))
DEATH = pygame.mixer.Sound(os.path.join(LOCAL_DIR, "assets/sfx/death.wav"))
BUTTON_CLICK = pygame.mixer.Sound(os.path.join(LOCAL_DIR, "assets/sfx/button_click.wav"))
