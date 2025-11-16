# ----------------------------
# game_logic.py
# ----------------------------
import pygame
import random
import math

from assets import (
    render_bins_cairo,
    render_falling_block
)

WIDTH, HEIGHT = 480, 640
FPS = 60
BIN_COUNT = 4

BASE_FALL_SPEED = 90
FALL_SPEED = BASE_FALL_SPEED
NEW_FALL_INTERVAL = 1.2
MOVE_SPEED = 300

BG_COLOR = (24, 24, 30)
TEXT_COLOR = (240, 240, 240)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris Angka - Anak Awan Pastel")

clock = pygame.time.Clock()
HUD_FONT = pygame.font.SysFont('Arial', 18)


# ---------------------------------------------------
# PROBLEM & FALLING OBJECT
# ---------------------------------------------------
class Problem:
    def __init__(self, expr, answer):
        self.expr = expr
        self.answer = answer


class FallingNumber:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.w = 64
        self.h = 52
        self.surface = render_falling_block(value)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, dt, move_dir=0):
        # gerak horizontal
        self.x += move_dir * MOVE_SPEED * dt
        self.x = max(0, min(WIDTH - self.w, self.x))

        # jatuh vertikal
        global FALL_SPEED
        self.y += FALL_SPEED * dt

    def draw(self, surf):
        surf.blit(self.surface, (self.x, self.y))


# ---------------------------------------------------
# GAME
# ---------------------------------------------------
class Game:
    def __init__(self):
        global FALL_SPEED
        FALL_SPEED = BASE_FALL_SPEED

        self.score = 0
        self.lives = 3
        self.falling = None
        self.time_since_last = 0

        self.bins = []
        self.problems = []
        self.bin_surface = None

        self.speed_level = 1
        self.speed_message_timer = 0

        self.make_problems_and_bins()

    # ---------------------------------------------------
    # CREATE NEW MATH PROBLEMS AND BINS
    # ---------------------------------------------------
    def make_problems_and_bins(self):
        bottom_h = 120
        bin_h = 84
        bin_w = WIDTH // BIN_COUNT
        bin_y = HEIGHT - bottom_h + (bottom_h - bin_h) // 2

        self.bins.clear()
        self.problems.clear()

        ops = ['+', '-', '*', '/']
        answers = []

        while len(answers) < BIN_COUNT:
            a = random.randint(1, 12)
            b = random.randint(1, 12)
            op = random.choice(ops)

            if op == '/':
                b = random.randint(1, 12)
                a = b * random.randint(1, 6)

            expr = f"{a} {op} {b}"
            ans = eval(expr)

            if isinstance(ans, float) and abs(ans - int(ans)) < 1e-8:
                ans = int(ans)

            if ans in answers:
                continue

            answers.append(ans)
            self.problems.append(Problem(expr, ans))

        bin_labels = []

        for i, p in enumerate(self.problems):
            x = i * bin_w + 8
            w = bin_w - 16
            rect = (x, bin_y, w, bin_h)

            self.bins.append(rect)
            bin_labels.append(str(p.answer))

        self.bin_surface = render_bins_cairo(WIDTH, bottom_h, self.bins, bin_labels)

    # ---------------------------------------------------
    # SPAWN ITEM JATUH
    # ---------------------------------------------------
    def spawn_falling(self):
        p = random.choice(self.problems)
        self.falling = FallingNumber(p.answer, (WIDTH - 64) / 2, -60)

    # ---------------------------------------------------
    # CHECK COLLISION
    # ---------------------------------------------------
    def check_bin_collision(self):
        if not self.falling:
            return

        cx = self.falling.x + self.falling.w / 2
        cy = self.falling.y + self.falling.h / 2

        for idx, (x, y, w, h) in enumerate(self.bins):
            if x <= cx <= x + w and y <= cy <= y + h:
                expected = self.problems[idx].answer

                if math.isclose(self.falling.value, expected):
                    self.score += 1
                else:
                    self.lives -= 1

                self.falling = None
                self.make_problems_and_bins()
                return

        if self.falling.y > HEIGHT:
            self.lives -= 1
            self.falling = None

    # ---------------------------------------------------
    # UPDATE GAME
    # ---------------------------------------------------
    def update(self, dt, move_dir):
        self.time_since_last += dt

        if not self.falling and self.time_since_last >= NEW_FALL_INTERVAL:
            self.spawn_falling()
            self.time_since_last = 0

        if self.falling:
            self.falling.update(dt, move_dir)
            self.check_bin_collision()

        # Speed up
        global FALL_SPEED
        if self.score > 0 and self.score % 5 == 0:
            new_lv = 1 + self.score // 5
            if new_lv > self.speed_level:
                self.speed_level = new_lv
                FALL_SPEED = BASE_FALL_SPEED + 50 * (self.speed_level - 1)
                self.speed_message_timer = 2.0

        if self.speed_message_timer > 0:
            self.speed_message_timer -= dt

    # ---------------------------------------------------
    # DRAW GAME
    # ---------------------------------------------------
    def draw(self, surf):
        surf.fill(BG_COLOR)

        surf.blit(HUD_FONT.render(f"Score: {self.score}", True, TEXT_COLOR), (10, 10))
        surf.blit(HUD_FONT.render(f"Lives: {self.lives}", True, TEXT_COLOR), (WIDTH - 100, 10))

        if self.falling:
            self.falling.draw(surf)

        surf.blit(self.bin_surface, (0, HEIGHT - self.bin_surface.get_height()))

        # draw expressions above bins
        small_font = pygame.font.SysFont('Arial', 16)
        for i, p in enumerate(self.problems):
            x, y, w, h = self.bins[i]
            expr_s = small_font.render(p.expr, True, TEXT_COLOR)
            surf.blit(expr_s, expr_s.get_rect(center=(x + w/2, y - 20)))

        if self.speed_message_timer > 0:
            msg = pygame.font.SysFont('Arial', 22, bold=True).render(
                f"Speed Up! ({FALL_SPEED:.0f}px/s)", True, (255, 220, 80)
            )
            surf.blit(msg, msg.get_rect(center=(WIDTH // 2, 60)))


# ---------------------------------------------------
# MAIN LOOP — NO SYS
# ---------------------------------------------------
def main():
    game = Game()
    hold_left = hold_right = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    hold_left = True
                if e.key == pygame.K_RIGHT:
                    hold_right = True
                if e.key == pygame.K_r:
                    game = Game()
                if e.key == pygame.K_SPACE and game.falling:
                    game.falling.y = HEIGHT

            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT:
                    hold_left = False
                if e.key == pygame.K_RIGHT:
                    hold_right = False

        move_dir = (-1 if hold_left else 0) + (1 if hold_right else 0)
        game.update(dt, move_dir)
        game.draw(screen)

        if game.lives <= 0:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            screen.blit(ov, (0, 0))

            go = pygame.font.SysFont('Arial', 36, bold=True).render("GAME OVER", True, (255,255,255))
            screen.blit(go, go.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))

        pygame.display.flip()

    pygame.quit()


main()
