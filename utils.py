import json
import random
from config import *


class Button:
    def __init__(self, rect, text, callback) -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback

    def draw(self, surface) -> None:
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        text_surf = FONT.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_hovered(self, pos) -> bool:
        return self.rect.collidepoint(pos)


class Leaderboard:
    def __init__(self, file_path="resources/leaderboard.txt") -> None:
        self.file_path = file_path

    def load_leaderboard(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_leaderboard(self, leader_board) -> None:
        with open(self.file_path, "w") as file:
            json.dump(leader_board, file)

    def add_score(self, score: int) -> None:
        leader_board = self.load_leaderboard()
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        leader_board.append({"score": score, "time": timestamp})
        leader_board = sorted(leader_board, key=lambda x: x["score"], reverse=True)[:10]
        self.save_leaderboard(leader_board)

    def show_leaderboard(self) -> None:
        lb_width, lb_height = 100, 37.5
        lb_x = 0.5 * BRICK_WIDTH * (FIELD_WIDTH + INFO_PANEL_WIDTH) - 0.5 * lb_width
        lb_y = SCREEN.get_height() // 2 + 4 * lb_height
        exit_leaderboard = Button((lb_x, lb_y, lb_width, lb_height), "退出", lambda: None)
        while True:
            SCREEN.fill((0, 0, 0))
            exit_leaderboard.draw(SCREEN)
            leaderboard_data = self.load_leaderboard()
            title_text = FONT.render("排行榜", True, (255, 255, 255))
            SCREEN.blit(title_text, ((SCREEN.get_width() - title_text.get_width()) // 2, 50))
            for i, entry in enumerate(leaderboard_data):
                text = FONT.render(f"{i + 1}. 分数: {entry['score']} 时间: {entry['time']}", True, (255, 255, 255))
                SCREEN.blit(text, (50, 100 + i * 30))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_cover()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_leaderboard.is_hovered(pygame.mouse.get_pos()):
                        return


def show_teaching() -> None:
    exit_game = Button(
        (BRICK_WIDTH * (FIELD_WIDTH + 0.5 * INFO_PANEL_WIDTH) - 50,
         SCREEN.get_height() // 2 + 4 * 37.5,
         100, 37.5),
        "退出",
        lambda: None
    )
    while True:
        SCREEN.fill((0, 0, 0))
        teach_rect = TEACH_IMG.get_rect(center=(SCREEN.get_width() // 2, SCREEN.get_height() // 2))
        SCREEN.blit(TEACH_IMG, teach_rect)
        exit_game.draw(SCREEN)
        pygame.display.flip()
        for et in pygame.event.get():
            if et.type == pygame.QUIT:
                exit_cover()
            if et.type == pygame.MOUSEBUTTONDOWN and et.button == 1:
                if exit_game.text == "退出":
                    return


class Settings:
    def __init__(self, leaderboard: Leaderboard, config: GameConfig, difficulty_callback) -> None:
        self.leaderboard = leaderboard
        self.music_enabled = True
        self.config = config
        self.difficulty_callback = difficulty_callback

    def show_settings(self) -> None:
        width, height = 150, 37.5
        spacing = 15
        total_height = 4 * height + 3 * spacing
        y = (SCREEN.get_height() - total_height) // 2 + 50
        x = SCREEN.get_width() // 2

        buttons = [
            # 使用 lambda 包装，确保按钮点击时才调用方法，而非在创建时立即执行
            Button((x - width // 2, y - (height + spacing), width, height), "玩法教程", show_teaching),
            Button((x - width // 2, y, width, height), "清除排行榜", lambda: self.leaderboard.save_leaderboard([])),
            Button((x - width // 2, y + (height + spacing), width, height), "开关音乐", self.config.toggle_music),
            Button((x - width // 2, y + 2 * (height + spacing), width, height), "调整难度", self.adjust_difficulty),
            Button((x - width // 2, y + 3 * (height + spacing), width, height), "退出", lambda: None)
        ]
        while True:
            SCREEN.fill((0, 0, 0))
            for btn in buttons:
                btn.draw(SCREEN)
            pygame.display.flip()
            for et in pygame.event.get():
                if et.type == pygame.QUIT:
                    exit_cover()
                if et.type == pygame.MOUSEBUTTONDOWN and et.button == 1:
                    for btn in buttons:
                        if btn.is_hovered(pygame.mouse.get_pos()):
                            btn.callback()
                            if btn.text == "退出":
                                return

    def adjust_difficulty(self) -> None:
        difficulties = ["简单", "普通", "困难"]
        width, height = 150, 37.5
        spacing = 15
        total_height = len(difficulties) * height + (len(difficulties) - 1) * spacing
        y = (SCREEN.get_height() - total_height) // 2 + 50
        x = SCREEN.get_width() // 2

        buttons = []
        for diff in difficulties:
            buttons.append(Button(
                (x - width // 2, y, width, height),
                diff,
                lambda d=diff: self.difficulty_callback(d)
            ))
            y += height + spacing

        exit_button = Button((x - width // 2, y, width, height), "退出", lambda: None)
        buttons.append(exit_button)

        while True:
            SCREEN.fill((0, 0, 0))
            title = FONT.render("难度调整", True, (255, 255, 255))
            SCREEN.blit(title, ((SCREEN.get_width() - title.get_width()) // 2, 2 * title.get_height()))
            for btn in buttons:
                btn.draw(SCREEN)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_cover()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    for btn in buttons:
                        if btn.is_hovered(pos):
                            btn.callback()
                            if btn.text == "退出":
                                return
                            else:
                                return


class Skill:
    def __init__(self, config: GameConfig) -> None:
        self.config = config
        self.energy: int = 0
        self.skill_start_time = 0
        self.active_skill = None
        self.duration = 1000

    def activate_skill(self, game) -> None:
        if not game.field_bricks:
            return

        self.skill_start_time = pygame.time.get_ticks()
        random_brick = random.choice(game.field_bricks)
        target_x, target_y = random_brick.position  # 直接作用于选中的砖块，避免随机偏移导致作用无效

        if self.active_skill == 'TIME_SLOW':
            self.duration *= 20
            return
        elif self.active_skill == 'EXPLOSION':
            # 处理爆炸清除 3x3 范围
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    check_x = target_x + dx
                    check_y = target_y + dy
                    if 0 <= check_x < FIELD_WIDTH and 0 <= check_y < FIELD_HEIGHT:
                        game.grid[check_y][check_x] = 0

            # 过滤被炸掉的砖块
            game.field_bricks = [
                b for b in game.field_bricks if not (abs(b.position[0] - target_x) <= 1
                                                     and abs(b.position[1] - target_y) <= 1)
            ]

        elif self.active_skill == 'CLEAR_LINE':
            if 0 <= target_y < FIELD_HEIGHT:
                game.grid[target_y] = [0] * FIELD_WIDTH
                game.field_bricks = [b for b in game.field_bricks if b.position[1] != target_y]

        for y in range(FIELD_HEIGHT - 2, -1, -1):  # 从倒数第二行开始向上
            for x in range(FIELD_WIDTH):
                if game.grid[y][x] == 1:
                    # 计算可以下落的最大距离
                    drop = 0
                    while y + drop + 1 < FIELD_HEIGHT and game.grid[y + drop + 1][x] == 0:
                        drop += 1

                    if drop > 0:
                        # 更新网格数据
                        game.grid[y][x] = 0
                        game.grid[y + drop][x] = 1

                        # 更新砖块对象位置
                        for brick in game.field_bricks:
                            if brick.position == (x, y):
                                brick.position = (x, y + drop)

    def reset_skill(self) -> None:
        self.duration = 1000
        self.skill_start_time = 0
        self.active_skill = None

    def draw_skill(self):
        """绘制能量槽和技能文本"""
        energy_bg_rect = (FIELD_WIDTH * BRICK_WIDTH - 80, 10, 60, 20)
        pygame.draw.rect(SCREEN, (50, 50, 50), energy_bg_rect)

        if self.active_skill is not None:
            skill_text = FONT.render(SkillType[self.active_skill], True, (255, 255, 0))
            text_rect = skill_text.get_rect(
                center=(energy_bg_rect[0] + energy_bg_rect[2] // 2, energy_bg_rect[1] + energy_bg_rect[3] // 2))
            SCREEN.blit(skill_text, text_rect)

            if pygame.time.get_ticks() - self.skill_start_time > self.duration:
                self.reset_skill()
        # 计算能量条宽度（按比例）
        energy_width = int(energy_bg_rect[2] * (min(self.energy, MAX_ENERGY) / 60))  # 背景宽度为80
        pygame.draw.rect(SCREEN, (0, 200, 0),
                         (energy_bg_rect[0], energy_bg_rect[1],
                          energy_width, energy_bg_rect[3]))  # 先绘制能量条
