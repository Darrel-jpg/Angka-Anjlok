import random
import math
import sys
import pygame
import cairo


WIDTH, HEIGHT = 480, 640
FPS = 60
BIN_COUNT = 4            # jumlah tempat soal di bawah
BASE_FALL_SPEED = 90     # px/sec dasar (dipakai untuk reset)
FALL_SPEED = BASE_FALL_SPEED
MOVE_SPEED = 300         # px/sec untuk memindahkan blok saat menahan kiri/kanan
NEW_FALL_INTERVAL = 1.2  # detik antar munculnya angka baru

# Warna (pygame uses 0..255)
BG_COLOR = (24, 24, 30)
TEXT_COLOR = (240, 240, 240)
BIN_COLOR = (40, 40, 48)
BIN_BORDER = (100, 100, 110)
GOOD_COLOR = (88, 214, 141)
BAD_COLOR = (235, 87, 87)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Tetris Angka - Simple")

# font fallback untuk teks pygame (dipakai untuk HUD)
HUD_FONT = pygame.font.SysFont('Arial', 18)

# -----------------------
# Utility: render dengan pycairo -> pygame.Surface
# -----------------------
def cairo_surface_to_pygame(surf: cairo.ImageSurface) -> pygame.Surface:
    """Konversi cairo.ImageSurface ke pygame.Surface"""
    buf = surf.get_data()
    py_surf = pygame.image.frombuffer(buf, (surf.get_width(), surf.get_height()), 'ARGB')
    return py_surf.convert_alpha()

def render_bins_cairo(width, height, bin_rects, bin_labels):
    """Render area bottom dengan pycairo"""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    for r, label in zip(bin_rects, bin_labels):
        x, y, w, h = r
        ctx.set_source_rgb(BIN_COLOR[0]/255, BIN_COLOR[1]/255, BIN_COLOR[2]/255)
        ctx.rectangle(x, y, w, h)
        ctx.fill_preserve()
        ctx.set_line_width(2)
        ctx.set_source_rgb(BIN_BORDER[0]/255, BIN_BORDER[1]/255, BIN_BORDER[2]/255)
        ctx.stroke()

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18)
        tx = ctx.text_extents(label)
        tx_x = x + (w - tx.x_advance) / 2
        tx_y = y + h/2 + tx.height/2
        ctx.set_source_rgb(TEXT_COLOR[0]/255, TEXT_COLOR[1]/255, TEXT_COLOR[2]/255)
        ctx.move_to(tx_x, tx_y)
        ctx.show_text(label)

    return cairo_surface_to_pygame(surf)

# -----------------------
# Game object classes
# -----------------------
class Problem:
    def __init__(self, expr, answer):
        self.expr = expr
        self.answer = answer

class FallingNumber:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.w = 56
        self.h = 40
        self.font = pygame.font.SysFont('Arial', 20, bold=True)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, dt, move_dir=0):
        self.x += move_dir * MOVE_SPEED * dt
        self.x = max(0, min(WIDTH - self.w, self.x))
        # gunakan variabel global FALL_SPEED (sudah di-reset saat Game dibuat)
        self.y += FALL_SPEED * dt

    def draw(self, surf):
        r = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surf, (60,60,72), r, border_radius=6)
        pygame.draw.rect(surf, (110,110,130), r, 2, border_radius=6)
        txt = self.font.render(str(self.value), True, TEXT_COLOR)
        surf.blit(txt, txt.get_rect(center=r.center))

class Game:
    def __init__(self):
        # reset FALL_SPEED global saat membuat objek Game baru
        global FALL_SPEED
        FALL_SPEED = BASE_FALL_SPEED

        self.running = True
        self.score = 0
        self.lives = 3
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
        ops = ['+', '-', '*', '/']
        while len(answers) < BIN_COUNT:
            a, b = random.randint(1, 12), random.randint(1, 12)
            op = random.choice(ops)
            if op == '/':
                b = random.randint(1, 12)
                a = b * random.randint(1,6)
            expr = f"{a} {op} {b}"
            ans = eval(expr)
            if isinstance(ans, float) and abs(ans - round(ans)) < 1e-8:
                ans = int(round(ans))
            if ans in answers: continue
            answers.append(ans)
            self.problems.append(Problem(expr, ans))

        bin_labels = []
        for i, p in enumerate(self.problems):
            x = i * bin_w + 8
            w = bin_w - 16
            self.bins.append((x, bin_y, w, bin_h))
            bin_labels.append(str(p.answer))

        self.bin_surface = render_bins_cairo(WIDTH, bottom_h, self.bins, bin_labels)

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
                if math.isclose(self.falling.value, expected, rel_tol=1e-9):
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
        self.time_since_last += dt
        if not self.falling and self.time_since_last >= NEW_FALL_INTERVAL:
            self.spawn_falling()
            self.time_since_last = 0

        if self.falling:
            self.falling.update(dt, move_dir)
            self.check_bin_collision()

        # naikkan speed setiap kelipatan 5 skor
        global FALL_SPEED
        if self.score > 0 and self.score % 5 == 0:
            new_level = 1 + self.score // 5
            if new_level > self.speed_level:
                self.speed_level = new_level
                FALL_SPEED = BASE_FALL_SPEED + (self.speed_level - 1) * 50
                self.speed_message_timer = 2.0  # tampilkan 2 detik

        if self.speed_message_timer > 0:
            self.speed_message_timer -= dt

    def draw(self, surf):
        surf.fill(BG_COLOR)
        score_s = HUD_FONT.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_s = HUD_FONT.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        surf.blit(score_s, (12, 10))
        surf.blit(lives_s, (WIDTH-100, 10))

        if self.falling:
            self.falling.draw(surf)
        surf.blit(self.bin_surface, (0, HEIGHT - self.bin_surface.get_height()))

        small_font = pygame.font.SysFont('Arial', 16)
        for i, p in enumerate(self.problems):
            x, y, w, h = self.bins[i]
            expr_txt = small_font.render(p.expr, True, TEXT_COLOR)
            surf.blit(expr_txt, expr_txt.get_rect(center=(x + w/2, y - 18)))

        # tampilkan pesan speed-up
        if self.speed_message_timer > 0:
            msg_font = pygame.font.SysFont('Arial', 22, bold=True)
            msg = msg_font.render(f"Speed Up! ({FALL_SPEED:.0f}px/s)", True, (255, 220, 80))
            surf.blit(msg, msg.get_rect(center=(WIDTH//2, 60)))

    def is_game_over(self):
        return self.lives <= 0

# -----------------------
# Main loop
# -----------------------
def main():
    game = Game()
    move_dir = 0
    hold_left = False
    hold_right = False

    while game.running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    hold_left = True
                elif event.key == pygame.K_RIGHT:
                    hold_right = True
                elif event.key == pygame.K_SPACE and game.falling:
                    game.falling.y = HEIGHT
                elif event.key == pygame.K_r:
                    # restart: buat Game baru -> Game.__init__ akan mereset FALL_SPEED
                    game = Game()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    hold_left = False
                elif event.key == pygame.K_RIGHT:
                    hold_right = False

        move_dir = -1 if hold_left and not hold_right else (1 if hold_right and not hold_left else 0)
        game.update(dt, move_dir)
        game.draw(screen)

        if game.is_game_over():
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            screen.blit(ov, (0,0))
            go_font = pygame.font.SysFont('Arial', 36, bold=True)
            t = go_font.render('GAME OVER', True, (255,255,255))
            tt = HUD_FONT.render('Tekan R untuk main lagi', True, (200,200,200))
            screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))
            screen.blit(tt, tt.get_rect(center=(WIDTH//2, HEIGHT//2 + 28)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

main()