import time

from config import *
from block import get_block
from utils import Leaderboard, Settings, Button, Skill, SkillType
import random


class TetrisGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.running: bool = True
        self.score: int = 0
        self.field_bricks = []
        self.grid = [[0 for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
        self.next_block = None
        self.last_end = 0  # 记录上一次
        self.firework_active = False
        self.leaderboard = Leaderboard()
        self.config = GameConfig()
        self.skill = Skill(self.config)
        self.settings = Settings(self.leaderboard, self.config, self.set_difficulty)

    def show_cover(self) -> None:
        """
        显示封面界面，包含开始游戏、排行榜、设置和退出按钮
        """
        width, height = 150, 37.5
        spacing = 15
        total_height = 4 * height + 3 * spacing
        y = (SCREEN.get_height() - total_height) // 2 + 50
        x = SCREEN.get_width() // 2

        buttons = [
            Button((x - width // 2, y, width, height), "开始游戏", self.start_game),
            Button((x - width // 2, y + (height + spacing), width, height), "排行榜",
                   self.leaderboard.show_leaderboard),
            Button((x - width // 2, y + 2 * (height + spacing), width, height), "设置", self.settings.show_settings),
            Button((x - width // 2, y + 3 * (height + spacing), width, height), "退出", exit_cover)
        ]

        while True:
            SCREEN.fill((0, 0, 0))
            cover_rect = COVER_IMG.get_rect(center=(SCREEN.get_width() // 2, SCREEN.get_height() // 2))
            SCREEN.blit(COVER_IMG, cover_rect)
            for btn in buttons:
                btn.draw(SCREEN)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    exit_cover()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    for btn in buttons:
                        if btn.is_hovered(pos):
                            btn.callback()

    def start_game(self) -> None:
        self.game_loop()

    def set_difficulty(self, new_diff: str) -> None:
        self.config.difficulty = new_diff

    def draw_field(self) -> None:
        # Draw the grid
        for x in range(FIELD_WIDTH + 1):  # +1 to draw the boundary lines
            pygame.draw.line(SCREEN, (50, 50, 50), (x * BRICK_WIDTH, 0), (x * BRICK_WIDTH, FIELD_HEIGHT * BRICK_HEIGHT))
        for y in range(FIELD_HEIGHT + 1):
            pygame.draw.line(SCREEN, (50, 50, 50), (0, y * BRICK_HEIGHT), (FIELD_WIDTH * BRICK_WIDTH, y * BRICK_HEIGHT))

        # Draw all the bricks in the field
        for brick in self.field_bricks:
            brick.draw(SCREEN)

        # Draw active skill
        self.skill.draw_skill()

    def draw_info_panel(self) -> None:
        # 显示得分信息
        score_text = FONT.render(f'得分: {self.score}', True, (255, 255, 255))
        SCREEN.blit(score_text, (FIELD_WIDTH * BRICK_WIDTH + 10, 20))

        # 显示下一个方块提示
        next_text = FONT.render('下一个:', True, (255, 255, 255))
        SCREEN.blit(next_text, (FIELD_WIDTH * BRICK_WIDTH + 10, 100))
        if self.next_block:
            for brick in self.next_block.bricks:
                brick.draw(SCREEN)

    def eliminate_lines(self) -> int:
        eliminated = 0
        y = FIELD_HEIGHT - 1
        while y >= 0:
            if 0 not in self.grid[y]:
                eliminated += 1
                del self.grid[y]
                self.grid.insert(0, [0] * FIELD_WIDTH)

                new_field_bricks = []
                for brick in self.field_bricks:
                    bx, by = brick.position
                    if by == y:
                        continue
                    elif by < y:
                        brick.position = (bx, by + 1)
                    new_field_bricks.append(brick)
                self.field_bricks = new_field_bricks
            else:
                y -= 1
        return eliminated

    def game_loop(self) -> None:
        restart = Button(
            (BRICK_WIDTH * (FIELD_WIDTH + 0.5 * INFO_PANEL_WIDTH) - 50,
             SCREEN.get_height() // 2 + 2 * 37.5,
             100, 37.5),
            "重新开始",
            self.reset_game_state_and_restart
        )
        exit_game = Button(
            (BRICK_WIDTH * (FIELD_WIDTH + 0.5 * INFO_PANEL_WIDTH) - 50,
             SCREEN.get_height() // 2 + 4 * 37.5,
             100, 37.5),
            "退出",
            self.show_cover
        )
        while self.running:
            if self.next_block is None:
                cur_block = get_block(self.config)
                cur_block.set_position(CUR_BLOCK_INIT_POSITION)
            else:
                cur_block = self.next_block
                cur_block.set_position(CUR_BLOCK_INIT_POSITION)
            self.next_block = get_block(self.config)
            self.next_block.set_position(NEXT_BLOCK_INIT_POSITION)

            if not cur_block.is_valid(self.grid):
                self.running = False
                break

            while not cur_block.stopped:
                self.clock.tick(60)

                # 先处理事件，使技能释放立即生效
                for event in pygame.event.get():
                    if event.type == QUIT:
                        exit_cover()
                    if event.type == KEYDOWN:
                        if (event.key == K_SPACE and self.skill.energy >= MAX_ENERGY and
                                self.skill.active_skill is None):
                            self.skill.active_skill = random.choice(list(SkillType))
                            self.skill.energy -= MAX_ENERGY
                            self.skill.activate_skill(self)
                        else:
                            action = KEY_ACTIONS.get(event.key)
                            if action and hasattr(cur_block, action):
                                getattr(cur_block, action)(self.grid)
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        pos = pygame.mouse.get_pos()
                        if restart.is_hovered(pos):
                            self.reset_game_state_and_restart()
                        elif exit_game.is_hovered(pos):
                            self.reset_game_state()
                            exit_game.callback()

                # 更新当前砖块状态
                current_time = pygame.time.get_ticks()
                cur_block.update(self.grid, current_time, self.skill.active_skill)

                # 绘制界面
                SCREEN.fill((0, 0, 0))
                draw_frame()
                restart.draw(SCREEN)
                exit_game.draw(SCREEN)
                self.draw_field()
                self.draw_info_panel()
                cur_block.draw(SCREEN)
                pygame.display.flip()

            for brick in cur_block.bricks:
                x, y = brick.position
                self.grid[y][x] = 1
                self.field_bricks.append(brick)

            eliminated = self.eliminate_lines()
            if eliminated > 0:
                DIDA.play()
            self.skill.energy += eliminated * SKILL_ENERGY_PER_LINE
            self.score += SCORE_PER_LINE.get(eliminated, 0)

            # 计算
            current_end = self.score // 500
            # 结果是否增大
            if current_end > self.last_end:
                self.firework_active = True
                # 更新余数记录
                self.last_end = current_end
            # 在绘制部分添加烟火效果
            if self.firework_active:
                # 在场地中央偏上显示
                center_x = FIELD_WIDTH * BRICK_WIDTH // 2
                cover_rect = FIREWORKS.get_rect(center=(center_x, SCREEN.get_height() // 3))
                SCREEN.blit(FIREWORKS, cover_rect)
                pygame.display.flip()
                time.sleep(1.0)
                self.firework_active = False
        self.leaderboard.add_score(self.score)
        self.game_over_screen(restart, exit_game)

    def reset_game_state(self) -> None:
        self.last_end = 0
        self.firework_active = False
        self.score = 0
        self.field_bricks = []
        self.grid = [[0 for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
        self.next_block = None
        self.running = True
        self.skill.energy = 0
        self.skill.reset_skill()

    def game_over_screen(self, restart: Button, exit_game: Button) -> None:
        while True:
            SCREEN.fill((0, 0, 0))
            SCREEN.blit(GAME_OVER_IMG, (FIELD_WIDTH / 2 * BRICK_WIDTH, (FIELD_HEIGHT / 2 - 2) * BRICK_HEIGHT))
            score_text = FONT.render(f'得分: {self.score}', True, (255, 255, 255))
            SCREEN.blit(score_text, (FIELD_WIDTH * BRICK_WIDTH + 10, 20))
            restart.draw(SCREEN)
            exit_game.draw(SCREEN)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    exit_cover()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if restart.is_hovered(pos):
                        self.reset_game_state_and_restart()
                    elif exit_game.is_hovered(pos):
                        self.reset_game_state()
                        exit_game.callback()

    def reset_game_state_and_restart(self) -> None:
        self.reset_game_state()
        self.game_loop()


if __name__ == "__main__":
    game = TetrisGame()
    game.show_cover()
    exit_cover()
