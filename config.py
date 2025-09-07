import pygame
import sys
from pygame.locals import *

pygame.font.init()
pygame.mixer.init()

FONT = pygame.font.Font("resources/simsun.ttc", 20)
MUSIC = pygame.mixer.Sound("resources/music.mp3")
MUSIC.set_volume(0.1)
MUSIC.play(-1)
DIDA = pygame.mixer.Sound("resources/dida.mp3")
GAME_OVER_IMG = pygame.image.load("resources/game-over.png")
COVER_IMG = pygame.image.load("resources/cover.png")
TEACH_IMG = pygame.image.load("resources/teach.png")
FIREWORKS = pygame.image.load("resources/fireworks.png")

# 游戏场地及砖块参数
FIELD_WIDTH, FIELD_HEIGHT = 10, 16
BRICK_WIDTH, BRICK_HEIGHT = 32, 32
INFO_PANEL_WIDTH = 6

CUR_BLOCK_INIT_POSITION = (4, 0)
NEXT_BLOCK_INIT_POSITION = (FIELD_WIDTH + 1, 5)

SCREEN = pygame.display.set_mode(((FIELD_WIDTH + INFO_PANEL_WIDTH) * BRICK_WIDTH, FIELD_HEIGHT * BRICK_HEIGHT))
FRAME_COLOR = pygame.Color(200, 200, 200)

SCORE_PER_LINE = {1: 100, 2: 200, 3: 400, 4: 600}

KEY_ACTIONS = {
    K_w: "rotate",
    K_UP: "rotate",
    K_a: "left",
    K_LEFT: "left",
    K_d: "right",
    K_RIGHT: "right",
    K_s: "down",
    K_DOWN: "down",
    K_SPACE: "activate_skill"
}

SKILL_ENERGY_PER_LINE = 20
MAX_ENERGY = 60

SkillType = {
    "EXPLOSION": "爆裂冲击",
    "TIME_SLOW": "时空凝滞",
    "CLEAR_LINE": "雷霆扫荡"
}


# 各种方块的布局数据（此处保持原有数据不变）
bricks_layout_0 = (
    ((0, 0), (0, 1), (0, 2), (0, 3)),
    ((0, 1), (1, 1), (2, 1), (3, 1))
)
bricks_layout_1 = (
    ((1, 0), (2, 0), (1, 1), (2, 1)),
)
bricks_layout_2 = (
    ((1, 0), (0, 1), (1, 1), (2, 1)),
    ((0, 1), (1, 0), (1, 1), (1, 2)),
    ((1, 2), (0, 1), (1, 1), (2, 1)),
    ((2, 1), (1, 0), (1, 1), (1, 2)),
)
bricks_layout_3 = (
    ((0, 1), (1, 1), (1, 0), (2, 0)),
    ((0, 0), (0, 1), (1, 1), (1, 2)),
)
bricks_layout_4 = (
    ((0, 0), (1, 0), (1, 1), (2, 1)),
    ((1, 0), (1, 1), (0, 1), (0, 2)),
)
bricks_layout_5 = (
    ((0, 0), (1, 0), (1, 1), (1, 2)),
    ((0, 2), (0, 1), (1, 1), (2, 1)),
    ((1, 0), (1, 1), (1, 2), (2, 2)),
    ((2, 0), (2, 1), (1, 1), (0, 1)),
)
bricks_layout_6 = (
    ((2, 0), (1, 0), (1, 1), (1, 2)),
    ((0, 0), (0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (1, 1), (1, 0)),
    ((2, 2), (2, 1), (1, 1), (0, 1)),
)

colors_for_bricks = (
    pygame.Color(255, 50, 50),
    pygame.Color(50, 255, 50),
    pygame.Color(50, 50, 255),
    pygame.Color(200, 200, 200),
    pygame.Color(255, 255, 0),
    pygame.Color(255, 0, 255),
    pygame.Color(0, 255, 255)
)

BLOCK_TYPES = [
    {"layouts": bricks_layout_0, "color": colors_for_bricks[0], "rotations": 2},
    {"layouts": bricks_layout_1, "color": colors_for_bricks[1], "rotations": 1},
    {"layouts": bricks_layout_2, "color": colors_for_bricks[2], "rotations": 4},
    {"layouts": bricks_layout_3, "color": colors_for_bricks[3], "rotations": 2},
    {"layouts": bricks_layout_4, "color": colors_for_bricks[4], "rotations": 2},
    {"layouts": bricks_layout_5, "color": colors_for_bricks[5], "rotations": 4},
    {"layouts": bricks_layout_6, "color": colors_for_bricks[6], "rotations": 4}
]


def exit_cover() -> None:
    pygame.quit()
    sys.exit(0)


def draw_frame() -> None:
    pygame.draw.line(
        SCREEN, FRAME_COLOR,
        (FIELD_WIDTH * BRICK_WIDTH, 0),
        (FIELD_WIDTH * BRICK_WIDTH, FIELD_HEIGHT * BRICK_HEIGHT),
        3
    )


def get_move_interval(difficulty: str) -> int:
    mapping = {"简单": 800, "普通": 500, "困难": 300}
    return mapping.get(difficulty, 500)


class GameConfig:
    """
    游戏配置类，包含难度、音量等配置
    """
    def __init__(self, difficulty="普通", music_enabled=True):
        self.difficulty = difficulty
        self.music_enabled = music_enabled

    def get_move_interval(self) -> int:
        return get_move_interval(self.difficulty)

    def toggle_music(self) -> None:
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            MUSIC.play(-1)
        else:
            MUSIC.stop()
