import pygame
import random
import math

from assets import (
    draw_coin_sack, draw_falling_coin, draw_background_game, draw_hud_panel, draw_heart_icon, draw_pause_icon, 
    draw_popup_menu, draw_colored_button 
)

WIDTH, HEIGHT = int(480*1.2), int(640*1.2)
FPS = 60
BIN_COUNT = 4
BASE_FALL_SPEED = 90
FALL_SPEED = BASE_FALL_SPEED
MOVE_SPEED = 300
NEW_FALL_INTERVAL = 1.2

TEXT_COLOR = (240, 230, 210) 
TEXT_SHADOW = (20, 10, 5)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Angka Anjlok")

HUD_FONT = pygame.font.SysFont('Georgia', 20, bold=True)
TITLE_FONT = pygame.font.SysFont('Georgia', 42, bold=True)
SUBTITLE_FONT = pygame.font.SysFont('Georgia', 24, italic=True)

class Problem:
    def __init__(self, expr, answer):
        self.expr = expr
        self.answer = answer

class FallingNumber:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.image = draw_falling_coin(value)
        self.w = self.image.get_width()
        self.h = self.image.get_height()

    # def update(self, dt, move_dir=0):
    #     global FALL_SPEED
    #     self.x += move_dir * MOVE_SPEED * dt
    #     self.x = max(0, min(WIDTH - self.w, self.x))
    #     self.y += FALL_SPEED * dt

    def update(self, dt, move_dir=0, speed_multiplier=1):
        global FALL_SPEED
        self.x += move_dir * MOVE_SPEED * dt
        self.x = max(0, min(WIDTH - self.w, self.x))        
        self.y += (FALL_SPEED * speed_multiplier) * dt

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))

class Game:
    def __init__(self, allowed_ops, difficulty):
        global FALL_SPEED
        FALL_SPEED = BASE_FALL_SPEED
        self.allowed_ops = allowed_ops
        self.difficulty = difficulty
        self.score = 0
        self.lives = 3
        
        self.background_img = draw_background_game(WIDTH, HEIGHT)
        
        self.score_panel = draw_hud_panel(140, 40)
        self.heart_icon = draw_heart_icon(32)
        
        self.pause_btn_normal = draw_pause_icon(48, hover=False)
        self.pause_btn_hover = draw_pause_icon(48, hover=True)
        self.pause_rect = pygame.Rect(WIDTH - 60, 10, 48, 48)
        
        self.bins = []
        self.problems = []
        self.falling = None
        self.time_since_last = 0
        self.bin_surface = None
        self.speed_level = 1
        self.speed_message_timer = 0
        
        self.make_problems_and_bins()

    def generate_expression(self, is_complex):
        while True:
            ops = self.allowed_ops
            nums = [random.randint(1, 12) for _ in range(3 if is_complex else 2)]
            selected_ops = [random.choice(ops) for _ in range(2 if is_complex else 1)]
            
            if not is_complex:
                a, b = nums[0], nums[1]
                op = selected_ops[0]
                
                if op == '/':
                    a = b * random.randint(1, 10)
                
                expr = f"{a} {op} {b}"
            
            else:
                expr = f"{nums[0]} {selected_ops[0]} {nums[1]}"
                expr += f" {selected_ops[1]} {nums[2]}"

            try:
                ans = eval(expr)
                
                if ans == int(ans) and 0 <= ans <= 100:
                    display_expr = expr.replace('*', 'x').replace('/', ':')
                    
                    return display_expr, int(ans)
            except ZeroDivisionError:
                continue

    def make_problems_and_bins(self):
        bottom_h = 120
        bin_h = 84
        bin_w = WIDTH // BIN_COUNT
        bin_y = HEIGHT - bottom_h + (bottom_h - bin_h)//2
        
        self.bins = []
        self.problems = []
        answers = []
        complex_indices = []
        
        if self.difficulty == "MEDIUM":
            complex_indices = random.sample(range(BIN_COUNT), 2)
        elif self.difficulty == "HARD":
            complex_indices = list(range(BIN_COUNT))

        while len(self.problems) < BIN_COUNT:
            current_idx = len(self.problems)
            is_complex = current_idx in complex_indices            
            expr, ans = self.generate_expression(is_complex)
            
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
        
        self.bin_surface = draw_coin_sack(WIDTH, bottom_h, local_rects, bin_labels)

    def spawn_falling(self):
        target = random.choice(self.problems)
        fn = FallingNumber(value=target.answer, x=(WIDTH-56)/2, y=-60)
        self.falling = fn

    def check_bin_collision(self):
        if not self.falling: return
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

    def update(self, dt, move_dir, is_fast_drop=False):
        global FALL_SPEED
        self.time_since_last += dt        
        speed_mult = 4 if is_fast_drop else 1

        if not self.falling and self.time_since_last >= NEW_FALL_INTERVAL:
            self.spawn_falling()
            self.time_since_last = 0
            
        if self.falling:
            self.falling.update(dt, move_dir, speed_multiplier=speed_mult)
            self.check_bin_collision()
        
        if self.score > 0 and self.score % 5 == 0:
            new_level = 1 + self.score // 5
            if new_level > self.speed_level:
                self.speed_level = new_level
                FALL_SPEED = BASE_FALL_SPEED + (self.speed_level - 1) * 30
                self.speed_message_timer = 2.0

        if self.speed_message_timer > 0:
            self.speed_message_timer -= dt

    def draw(self, surf, mouse_pos):
        surf.blit(self.background_img, (0, 0))
        surf.blit(self.bin_surface, (0, HEIGHT - self.bin_surface.get_height()))
        
        if self.falling:
            self.falling.draw(surf)

        panel_x, panel_y = 10, 10
        surf.blit(self.score_panel, (panel_x, panel_y))
        
        diff_font = pygame.font.SysFont('Georgia', 14, bold=True)
        diff_text = diff_font.render(self.difficulty, True, (200, 200, 200))
        surf.blit(diff_text, (panel_x + 10, panel_y + 45))

        score_text = HUD_FONT.render(f"Score: {self.score}", True, (255, 255, 255))
        sx = panel_x + (140 - score_text.get_width()) // 2
        sy = panel_y + (40 - score_text.get_height()) // 2
        surf.blit(score_text, (sx, sy))

        start_x_lives = 170
        for i in range(self.lives):
            surf.blit(self.heart_icon, (start_x_lives + i * 35, 14))

        is_hover = self.pause_rect.collidepoint(mouse_pos)
        btn_img = self.pause_btn_hover if is_hover else self.pause_btn_normal
        surf.blit(btn_img, self.pause_rect.topleft)

        if self.speed_message_timer > 0:
            msg_font = pygame.font.SysFont('Georgia', 32, bold=True)
            msg_s = msg_font.render("SPEED UP!", True, (0,0,0))
            msg = msg_font.render("SPEED UP!", True, (255, 220, 80))
            cx, cy = WIDTH//2, 100
            surf.blit(msg_s, msg_s.get_rect(center=(cx+2, cy+2)))
            surf.blit(msg, msg.get_rect(center=(cx, cy)))

    def is_game_over(self):
        return self.lives <= 0

def draw_text_centered(surface, text, font, color, center_pos, shadow_offset=(2,2)):
    shad = font.render(text, True, TEXT_SHADOW)
    sr = shad.get_rect(center=(center_pos[0]+shadow_offset[0], center_pos[1]+shadow_offset[1]))
    surface.blit(shad, sr)
    txt = font.render(text, True, color)
    tr = txt.get_rect(center=center_pos)
    surface.blit(txt, tr)

def blur_surface(surface, scale_factor=0.1):
    w, h = surface.get_size()
    small_w = max(1, int(w * scale_factor))
    small_h = max(1, int(h * scale_factor))
    small_surf = pygame.transform.smoothscale(surface, (small_w, small_h))    
    blurred_surf = pygame.transform.smoothscale(small_surf, (w, h))    
    dark_tint = pygame.Surface((w, h), pygame.SRCALPHA)
    dark_tint.fill((0, 0, 0, 100)) 
    blurred_surf.blit(dark_tint, (0, 0))
    
    return blurred_surf

def difficulty_menu():
    levels = [
        ("MUDAH",  "EASY",   "#81c784"),
        ("SEDANG",  "MEDIUM", "#ffb74d"), 
        ("SULIT",  "HARD",   "#e57373")
    ]
    
    slab_w, slab_h = 350, 400
    bg_slab = draw_popup_menu(slab_w, slab_h, "PILIH LEVEL")
    bg_slab_rect = bg_slab.get_rect(center=(WIDTH//2, HEIGHT//2))
    bg_world = draw_background_game(WIDTH, HEIGHT)
    buttons = []
    btn_w, btn_h = 240, 60
    gap = 20
    start_y = bg_slab_rect.top + 120
    
    for i, (label, diff_id, color) in enumerate(levels):
        rect = pygame.Rect(0, 0, btn_w, btn_h)
        rect.centerx = WIDTH // 2
        rect.y = start_y + i * (btn_h + gap)
        
        img_normal = draw_colored_button(btn_w, btn_h, label, color, hover=False)
        img_hover = draw_colored_button(btn_w, btn_h, label, color, hover=True)
        
        buttons.append({
            "rect": rect,
            "id": diff_id,
            "img_normal": img_normal,
            "img_hover": img_hover
        })
        
    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(bg_world, (0,0))
        screen.blit(bg_slab, bg_slab_rect)
        
        for btn in buttons:
            is_hover = btn["rect"].collidepoint(mouse_pos)
            img = btn["img_hover"] if is_hover else btn["img_normal"]
            screen.blit(img, btn["rect"])
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            return btn["id"]
                            
        pygame.display.flip()
        clock.tick(60)

def main_menu():
    ops_list = [
        ("PENJUMLAHAN (+)", ['+'],             "#29b6f6"),
        ("PENGURANGAN (-)", ['-'],             "#ef5350"),
        ("PERKALIAN (x)",   ['*'],             "#ffa726"),
        ("PEMBAGIAN (/)",   ['/'],             "#66bb6a"), 
        ("SEMUA OPERASI",   ['+','-','*','/'], "#ab47bc")  
    ]
    
    slab_w, slab_h = 400, 550 
    menu_bg_img = draw_popup_menu(slab_w, slab_h, "PILIH MODE") 
    menu_bg_rect = menu_bg_img.get_rect(center=(WIDTH//2, HEIGHT//2))    
    bg_world_img = draw_background_game(WIDTH, HEIGHT)
    buttons = []    
    btn_width = 280
    btn_height = 60
    gap = 15
    start_y_offset = 110 
    
    for i, (label, ops, color_hex) in enumerate(ops_list):
        rect = pygame.Rect(0, 0, btn_width, btn_height)        
        rect.centerx = WIDTH // 2
        rect.y = menu_bg_rect.top + start_y_offset + i * (btn_height + gap)        
        img_normal = draw_colored_button(btn_width, btn_height, label, color_hex, hover=False)
        img_hover = draw_colored_button(btn_width, btn_height, label, color_hex, hover=True)
        
        buttons.append({
            "rect": rect,
            "ops": ops,
            "img_normal": img_normal,
            "img_hover": img_hover
        })

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(bg_world_img, (0,0))
        screen.blit(menu_bg_img, menu_bg_rect)        

        for btn in buttons:
            rect = btn["rect"]
            is_hover = rect.collidepoint(mouse_pos)            
            image_to_draw = btn["img_hover"] if is_hover else btn["img_normal"]
            screen.blit(image_to_draw, rect.topleft)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            return btn["ops"]

        pygame.display.flip()
        clock.tick(60)

def main():
    state = "MENU_OPS"
    game = None
    paused = False
    cached_blur_bg = None 
    selected_ops = [] 
    selected_diff = "EASY" 
    slab_w, slab_h = 350, 400
    pause_slab_img = draw_popup_menu(slab_w, slab_h, "PAUSE") 
    pause_slab_rect = pause_slab_img.get_rect(center=(WIDTH//2, HEIGHT//2))
    pause_btn_w, pause_btn_h = 220, 60
    pause_gap = 20
    slab_start_y = pause_slab_rect.top + 100 
    pause_btn_data = [
        {"text": "LANJUT",   "action": "resume",  "color": "#8bc34a"},
        {"text": "ULANGI",   "action": "restart", "color": "#ffcc00"},
        {"text": "KELUAR",   "action": "menu",    "color": "#e53935"}
    ]

    pause_buttons = []
    for i, data in enumerate(pause_btn_data):
        rect = pygame.Rect(0, 0, pause_btn_w, pause_btn_h)
        rect.centerx = WIDTH // 2
        rect.y = slab_start_y + i * (pause_btn_h + pause_gap)
        img_normal = draw_colored_button(pause_btn_w, pause_btn_h, data["text"], data["color"], hover=False)
        img_hover = draw_colored_button(pause_btn_w, pause_btn_h, data["text"], data["color"], hover=True)
        pause_buttons.append({"rect": rect, "action": data["action"], "img_normal": img_normal, "img_hover": img_hover})
        
    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        if state == "MENU_OPS":
            ops = main_menu() 
            if ops is None: return
            selected_ops = ops
            state = "MENU_DIFF"
            continue
            
        elif state == "MENU_DIFF":
            diff = difficulty_menu()
            if diff is None: return
            selected_diff = diff
            
            game = Game(selected_ops, selected_diff) 
            paused = False
            state = "GAME"
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not paused and not game.is_game_over():
                    if game.pause_rect.collidepoint(mouse_pos):
                        paused = True
                        cached_blur_bg = None
                
                elif paused:
                    for btn in pause_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            act = btn["action"]
                            if act == "resume":
                                paused = False
                                cached_blur_bg = None
                            elif act == "restart":
                                game = Game(game.allowed_ops, game.difficulty) 
                                paused = False
                                cached_blur_bg = None
                            elif act == "menu":
                                state = "MENU_OPS"
                                paused = False
                                cached_blur_bg = None

                elif game.is_game_over():
                     state = "MENU_OPS"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: game.move_dir = -1
                elif event.key == pygame.K_RIGHT: game.move_dir = 1
                elif event.key == pygame.K_r: state = "MENU_OPS"
                elif event.key == pygame.K_ESCAPE:
                    if not game.is_game_over(): 
                        paused = not paused
                        if not paused: cached_blur_bg = None

            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    game.move_dir = 0

        move_dir = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: move_dir = -1
        if keys[pygame.K_RIGHT]: move_dir = 1        
        is_fast_drop = keys[pygame.K_DOWN]
        
        if not paused and not game.is_game_over():
            game.update(dt, move_dir, is_fast_drop)

        game.draw(screen, mouse_pos)

        if paused:
            if cached_blur_bg is None:
                screen_copy = screen.copy()
                cached_blur_bg = blur_surface(screen_copy, scale_factor=0.1)
            screen.blit(cached_blur_bg, (0, 0))
            screen.blit(pause_slab_img, pause_slab_rect)
            for btn in pause_buttons:
                is_hover = btn["rect"].collidepoint(mouse_pos)
                image_to_draw = btn["img_hover"] if is_hover else btn["img_normal"]
                screen.blit(image_to_draw, btn["rect"])

        elif game.is_game_over():
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 180))
            screen.blit(ov, (0, 0))
            draw_text_centered(screen, "PERMAINAN SELESAI", TITLE_FONT, (255, 80, 80), (WIDTH//2, HEIGHT//2 - 20))
            draw_text_centered(screen, f"Skor Akhir: {game.score}", SUBTITLE_FONT, (255, 255, 255), (WIDTH//2, HEIGHT//2 + 30))
            draw_text_centered(screen, "Klik untuk kembali ke Menu", pygame.font.SysFont('Georgia', 18), (200, 200, 200), (WIDTH//2, HEIGHT//2 + 70))

        pygame.display.flip()

if __name__ == "__main__":
    main()