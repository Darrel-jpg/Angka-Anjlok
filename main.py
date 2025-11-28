import pygame
import random
import math

from assets import render_bins_cairo, render_falling_block
from assets import render_menu_button
from assets import create_cairo_background


#config
WIDTH, HEIGHT = int(480*1.2), int(640*1.2)
FPS = 60
BIN_COUNT = 4
BASE_FALL_SPEED = 90
FALL_SPEED = BASE_FALL_SPEED
MOVE_SPEED = 300
NEW_FALL_INTERVAL = 1.2

BG_COLOR = (24, 24, 30)
TEXT_COLOR = (240, 240, 240)
BIN_COLOR = (40, 40, 48)
BIN_BORDER = (100, 100, 110)
BUTTON_COLOR = (50, 50, 60)
BUTTON_HOVER = (80, 80, 100)
GOOD_COLOR = (88, 214, 141)
BAD_COLOR = (235, 87, 87)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Tetris Angka")

HUD_FONT = pygame.font.SysFont('Arial', 18)
TITLE_FONT = pygame.font.SysFont('Arial', 36, bold=True)
BTN_FONT = pygame.font.SysFont('Arial', 22, bold=True)
SMALL_FONT = pygame.font.SysFont('Arial', 16)

#logic
class Problem:
    def __init__(self, expr, answer):
        self.expr = expr
        self.answer = answer

class FallingNumber:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y

        # gunakan asset
        self.image = render_falling_block(value)
        self.w = self.image.get_width()
        self.h = self.image.get_height()

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, dt, move_dir=0):
        global FALL_SPEED
        self.x += move_dir * MOVE_SPEED * dt
        self.x = max(0, min(WIDTH - self.w, self.x))
        self.y += FALL_SPEED * dt

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))

class Game:
    def __init__(self, allowed_ops):
        global FALL_SPEED
        FALL_SPEED = BASE_FALL_SPEED

        self.allowed_ops = allowed_ops
        self.running = True
        self.score = 0
        self.lives = 3
        
        self.background_img = create_cairo_background(WIDTH, HEIGHT)
        self.bins = []
        self.problems = []
        self.falling = None
        self.time_since_last = 0
        self.bin_surface = None
        self.speed_level = 1
        self.speed_message_timer = 0
        self.make_problems_and_bins()

    def make_problems_and_bins(self):
        bottom_h = 120
        bin_h = 84
        bin_w = WIDTH // BIN_COUNT
        bin_y = HEIGHT - bottom_h + (bottom_h - bin_h)//2

        self.bins = []
        self.problems = []

        answers = []

        while len(answers) < BIN_COUNT:
            a, b = random.randint(1, 12), random.randint(1, 12)
            op = random.choice(self.allowed_ops)

            if op == '/':
                b = random.randint(1, 12)
                a = b * random.randint(1, 6)

            expr = f"{a} {op} {b}"
            ans = eval(expr)

            if isinstance(ans, float) and abs(ans - round(ans)) < 1e-8:
                ans = int(round(ans))

            if ans in answers:
                continue

            answers.append(ans)
            self.problems.append(Problem(expr, ans))

        bin_labels = []
        local_rects = []

        for i, p in enumerate(self.problems):
            x = i * bin_w + 8
            w = bin_w - 16
            rect = (x, bin_y, w, bin_h)
            self.bins.append(rect)
            
            local_y = bin_y - (HEIGHT - bottom_h)
            local_rects.append((x, local_y, w, bin_h))
            bin_labels.append(p.expr)

        self.bin_surface = render_bins_cairo(WIDTH, bottom_h, local_rects, bin_labels)


    def spawn_falling(self):
        target = random.choice(self.problems)
        fn = FallingNumber(value=target.answer, x=(WIDTH-56)/2, y=-48)
        self.falling = fn

    def check_bin_collision(self):
        if not self.falling:
            return

        cx = self.falling.x + self.falling.w/2
        cy = self.falling.y + self.falling.h/2

        for idx, r in enumerate(self.bins):
            x, y, w, h = r
            if x <= cx <= x+w and y <= cy <= y+h:
                expected = self.problems[idx].answer
                if self.falling.value == expected:
                    self.score += 1
                else:
                    self.lives -= 1

                self.falling = None
                self.make_problems_and_bins()
                return

        if self.falling.y > HEIGHT:
            self.lives -= 1
            self.falling = None

    def update(self, dt, move_dir):
        global FALL_SPEED

        self.time_since_last += dt
        if not self.falling and self.time_since_last >= NEW_FALL_INTERVAL:
            self.spawn_falling()
            self.time_since_last = 0

        if self.falling:
            self.falling.update(dt, move_dir)
            self.check_bin_collision()

        if self.score > 0 and self.score % 5 == 0:
            new_level = 1 + self.score // 5
            if new_level > self.speed_level:
                self.speed_level = new_level
                FALL_SPEED = BASE_FALL_SPEED + (self.speed_level - 1) * 50
                self.speed_message_timer = 2.0

        if self.speed_message_timer > 0:
            self.speed_message_timer -= dt

    def draw(self, surf):
        surf.blit(self.background_img, (0, 0))


        lives_s = HUD_FONT.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        surf.blit(lives_s, (WIDTH-60, 10))

        score_s = HUD_FONT.render(f"Score: {self.score}", True, TEXT_COLOR)
        surf.blit(score_s, (WIDTH-65, 32))

        if self.falling:
            self.falling.draw(surf)

        surf.blit(self.bin_surface, (0, HEIGHT - self.bin_surface.get_height()))

        if self.speed_message_timer > 0:
            msg_font = pygame.font.SysFont('Arial', 22, bold=True)
            msg = msg_font.render(f"Speed Up!", True, (255, 220, 80))
            surf.blit(msg, msg.get_rect(center=(WIDTH//2, 60)))

    def is_game_over(self):
        return self.lives <= 0

#menu ui
def draw_button(surface, rect, text, mouse_pos):
    hover = rect.collidepoint(mouse_pos)
    btn_img = render_menu_button(rect.width, rect.height, text, hover=hover)
    surface.blit(btn_img, rect.topleft)


def draw_small_button(surface, rect, text, mouse_pos):
    hover = rect.collidepoint(mouse_pos)
    btn_img = render_menu_button(rect.width, rect.height, text, hover=hover)
    surface.blit(btn_img, rect.topleft)


def main_menu():
    ops_list = [
        ("Penjumlahan (+)", ['+']),
        ("Pengurangan (-)", ['-']),
        ("Perkalian (*)", ['*']),
        ("Pembagian (/)", ['/']),
        ("Kombinasi Semua", ['+','-','*','/'])
    ]

    buttons = []
    start_y = 250
    for i, (label, ops) in enumerate(ops_list):
        rect = pygame.Rect(150, start_y + i*70, 280, 50)
        buttons.append((rect, label, ops))

    while True:
        mouse_pos = pygame.mouse.get_pos()

        screen.fill(BG_COLOR)
        title = TITLE_FONT.render("Pilih Mode Operasi", True, TEXT_COLOR)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 120)))

        for rect, label, ops in buttons:
            draw_button(screen, rect, label, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for rect, label, ops in buttons:
                        if rect.collidepoint(mouse_pos):
                            return ops

        pygame.display.flip()
        clock.tick(60)

def pause_popup(surface, center_rect, mouse_pos):
    panel = pygame.Surface((center_rect.width, center_rect.height), pygame.SRCALPHA)
    panel.fill((30, 30, 36, 230))  # slightly transparent panel
    surface.blit(panel, center_rect.topleft)

    title = TITLE_FONT.render("PAUSED", True, (255,255,255))
    surface.blit(title, title.get_rect(center=(center_rect.centerx, center_rect.top + 50)))

    # buttons
    btn_w, btn_h = 220, 44
    gap = 14
    bx = center_rect.centerx - btn_w//2
    by = center_rect.top + 110
    resume_rect = pygame.Rect(bx, by, btn_w, btn_h)
    restart_rect = pygame.Rect(bx, by + (btn_h + gap), btn_w, btn_h)
    menu_rect = pygame.Rect(bx, by + 2*(btn_h + gap), btn_w, btn_h)

    draw_button(surface, resume_rect, "Resume", mouse_pos)
    draw_button(surface, restart_rect, "Restart", mouse_pos)
    draw_button(surface, menu_rect, "Back to Menu", mouse_pos)

    return resume_rect, restart_rect, menu_rect

def blur_surface(surface, scale_factor=0.1):
    w, h = surface.get_size()

    # downscale
    small_w = max(1, int(w * scale_factor))
    small_h = max(1, int(h * scale_factor))
    small = pygame.transform.smoothscale(surface, (small_w, small_h))

    # upscale
    blurred = pygame.transform.smoothscale(small, (w, h))

    # blur
    dark = pygame.Surface((w, h), pygame.SRCALPHA)
    dark.fill((0, 0, 0, 100))
    blurred.blit(dark, (0, 0))

    return blurred


# -----------------------
def main():
    state = "MENU"
    game = None
    move_dir = 0
    hold_left = False
    hold_right = False
    paused = False
    
    pause_btn_rect = pygame.Rect(8, 8, 48, 32)
    
    resume_rect = restart_rect = menu_rect = None

    while True:
        dt = clock.tick(FPS) / 1000.0

        if state == "MENU":
            allowed_ops = main_menu()
            game = Game(allowed_ops)
            paused = False
            state = "GAME"
            # reset popup rects
            resume_rect = restart_rect = menu_rect = None
            continue

        # game loop
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pause_btn_rect.collidepoint(mouse_pos) and not paused and not game.is_game_over():
                    paused = True
                elif paused:
                    if resume_rect and resume_rect.collidepoint(mouse_pos):
                        paused = False
                        resume_rect = restart_rect = menu_rect = None
                    elif restart_rect and restart_rect.collidepoint(mouse_pos):
                        game = Game(game.allowed_ops)
                        paused = False
                        resume_rect = restart_rect = menu_rect = None
                    elif menu_rect and menu_rect.collidepoint(mouse_pos):
                        state = "MENU"
                        paused = False
                        resume_rect = restart_rect = menu_rect = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    hold_left = True
                elif event.key == pygame.K_RIGHT:
                    hold_right = True
                elif event.key == pygame.K_r:
                    state = "MENU"
                    paused = False
                    resume_rect = restart_rect = menu_rect = None
                elif event.key == pygame.K_SPACE and game.falling and not paused:
                    game.falling.y = HEIGHT
                elif event.key == pygame.K_ESCAPE:
                    if not game.is_game_over():
                        paused = not paused
                        if not paused:
                            resume_rect = restart_rect = menu_rect = None

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    hold_left = False
                elif event.key == pygame.K_RIGHT:
                    hold_right = False

        move_dir = -1 if hold_left and not hold_right else (1 if hold_right and not hold_left else 0)

        if not paused and not game.is_game_over():
            game.update(dt, move_dir)

        game.draw(screen)

        # Draw pause
        pygame.draw.rect(screen, (40,40,48), pause_btn_rect, border_radius=6)
        icon_text = SMALL_FONT.render("II", True, (220,220,220))
        screen.blit(icon_text, icon_text.get_rect(center=pause_btn_rect.center))

        if game.is_game_over():
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            screen.blit(ov, (0, 0))

            go_font = pygame.font.SysFont('Arial', 36, bold=True)
            t = go_font.render("GAME OVER", True, (255,255,255))
            tt = HUD_FONT.render("Tekan R untuk kembali ke menu", True, (220,220,220))
            screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))
            screen.blit(tt, tt.get_rect(center=(WIDTH//2, HEIGHT//2 + 28)))
            
        if paused:
            screen_copy = screen.copy()
            blurred_bg = blur_surface(screen_copy, scale_factor=0.08)
            screen.blit(blurred_bg, (0, 0))

            panel_w, panel_h = 360, 320
            panel_rect = pygame.Rect((WIDTH//2 - panel_w//2, HEIGHT//2 - panel_h//2, panel_w, panel_h))
            resume_rect, restart_rect, menu_rect = pause_popup(screen, panel_rect, mouse_pos)

        pygame.display.flip()

main()