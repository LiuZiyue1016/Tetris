import random
from typing import List, Tuple
from config import *
from utils import Skill
import logging

# 设置日志（如果需要调试可打开调试日志级别）
logging.basicConfig(level=logging.INFO)

# 类型别名
Position = Tuple[int, int]
Layout = List[Position]


class Brick:
    def __init__(self, position: Position, color: pygame.Color) -> None:
        """
        初始化砖块，设置在网格中的位置和颜色
        """
        self.position: Position = position
        self.color: pygame.Color = color
        self.image: pygame.Surface = pygame.Surface((BRICK_WIDTH, BRICK_HEIGHT))
        self.image.fill(self.color)

    def draw(self, surface: pygame.Surface) -> None:
        """
        在给定的 surface 上绘制砖块
        """
        surface.blit(self.image, (self.position[0] * BRICK_WIDTH, self.position[1] * BRICK_HEIGHT))


def is_valid_position(layout: Layout, pos: Position, grid: List[List[int]]) -> bool:
    """
    检查 layout 在指定 pos 位置是否有效：不超出场地边界且没有碰撞
    """
    offset_x, offset_y = pos
    for x, y in layout:
        new_x, new_y = x + offset_x, y + offset_y
        if new_x < 0 or new_y < 0 or new_x >= FIELD_WIDTH or new_y >= FIELD_HEIGHT:
            return False
        if grid[new_y][new_x] != 0:
            return False
    return True


class Block:
    def __init__(self, bricks_layout: List[Layout], direction: int, color: pygame.Color, config: GameConfig) -> None:
        """
        初始化方块
        :param bricks_layout: 所有旋转状态下的砖块布局
        :param direction: 初始方向索引
        :param color: 方块颜色
        :param config: 游戏配置对象，用于获取当前难度等信息
        """
        self.bricks_layout = bricks_layout
        self.direction = direction
        self.cur_layout = self.bricks_layout[self.direction]
        self.position = CUR_BLOCK_INIT_POSITION
        self.stopped = False
        self.move_interval = config.get_move_interval()  # 根据难度获取移动速度
        self.bricks = [Brick((self.position[0] + x, self.position[1] + y), color) for x, y in self.cur_layout]
        self.last_move = 0
        self.skill = Skill(config)

    def set_position(self, position: Position) -> None:
        """
        设置方块位置并刷新砖块位置
        """
        self.position = position
        self.refresh_bricks()

    def refresh_bricks(self) -> None:
        """
        根据当前方块位置刷新所有砖块在网格中的位置
        """
        for brick, (x, y) in zip(self.bricks, self.cur_layout):
            brick.position = (self.position[0] + x, self.position[1] + y)

    def draw(self, surface: pygame.Surface) -> None:
        """
        绘制当前方块所有砖块
        """
        for brick in self.bricks:
            brick.draw(surface)

    def left(self, grid: List[List[int]]) -> None:
        """
        向左移动方块
        """
        new_position: Position = (self.position[0] - 1, self.position[1])
        if is_valid_position(self.cur_layout, new_position, grid):
            self.position = new_position
            self.refresh_bricks()

    def right(self, grid: List[List[int]]) -> None:
        """
        向右移动方块
        """
        new_position: Position = (self.position[0] + 1, self.position[1])
        if is_valid_position(self.cur_layout, new_position, grid):
            self.position = new_position
            self.refresh_bricks()

    def down(self, grid: List[List[int]]) -> None:
        """
        快速下落到不能再下的位置
        """
        x, y = self.position
        while is_valid_position(self.cur_layout, (x, y + 1), grid):
            y += 1
        self.position = (x, y)
        self.refresh_bricks()

    def rotate(self, field_map: List[List[int]]) -> None:
        """
        顺时针旋转方块，并尝试使用简单的“踢墙”机制调整位置
        """
        new_direction = (self.direction + 1) % len(self.bricks_layout)
        new_layout = self.bricks_layout[new_direction]
        offsets = [(0, 0), (-1, 0), (1, 0), (0, -1)]  # 基本偏移列表
        for dx, dy in offsets:
            adjusted_pos = (self.position[0] + dx, self.position[1] + dy)
            if is_valid_position(new_layout, adjusted_pos, field_map):
                self.direction = new_direction
                self.cur_layout = new_layout
                self.position = adjusted_pos
                self.refresh_bricks()
                return

    def update(self, grid: List[List[int]], current_time: int, skill=None) -> None:
        """
        根据时间更新方块下落状态，同时根据技能效果调整速度
        """
        # 根据激活的技能调整下落速度
        move_interval = self.move_interval
        if skill == 'TIME_SLOW':
            move_interval *= 3
            logging.debug("时间凝滞技能激活，移动间隔增加到 %d 毫秒", move_interval)

        if current_time - self.last_move >= move_interval:
            new_position: Position = (self.position[0], self.position[1] + 1)
            if is_valid_position(self.cur_layout, new_position, grid):
                self.position = new_position
                self.refresh_bricks()
                self.last_move = current_time
            else:
                self.stop()

    def stop(self) -> None:
        """
        标记方块为停止状态
        """
        self.stopped = True

    def is_valid(self, grid: List[List[int]]) -> bool:
        """
        检查当前方块位置是否合法
        """
        return is_valid_position(self.cur_layout, self.position, grid)


def get_block(config: GameConfig) -> Block:
    """
    随机生成一个新方块
    """
    block_type = random.choice(BLOCK_TYPES)
    direction = random.randint(0, len(block_type["layouts"]) - 1)
    return Block(block_type["layouts"], direction, block_type["color"], config)
