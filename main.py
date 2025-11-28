import pygame
import random
import math

from assets import render_bins_cairo, render_falling_block
from assets import render_menu_button, create_cairo_background
from assets import render_hud_panel, render_heart_icon, render_pause_button_asset, render_parchment_scroll

# ==============================================================================
# KONFIGURASI
# ==============================================================================
WIDTH, HEIGHT = int(480*1.2), int(640*1.2)
FPS = 60
BIN_COUNT = 4
BASE_FALL_SPEED = 90
FALL_SPEED = BASE_FALL_SPEED
MOVE_SPEED = 300
NEW_FALL_INTERVAL = 1.2

# Warna text (Lebih ke Cream/Emas pudar agar cocok dengan background gelap)
TEXT_COLOR = (240, 230, 210) 
TEXT_SHADOW = (20, 10, 5)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Tetris Angka: Fantasy Math")

# Font diganti ke Serif agar lebih klasik/fantasy
HUD_FONT = pygame.font.SysFont('Georgia', 20, bold=True)
TITLE_FONT = pygame.font.SysFont('Georgia', 42, bold=True)
SUBTITLE_FONT = pygame.font.SysFont('Georgia', 24, italic=True)

# ==============================================================================
# LOGIC CLASS
# ==============================================================================
class Problem:
    def __init__(self, expr, answer):
        self.expr = expr
        self.answer = answer

class FallingNumber:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.image = render_falling_block(value)
        self.w = self.image.get_width()
        self.h = self.image.get_height()

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
        self.score = 0
        self.lives = 3
        
        # Load Assets
        self.background_img = create_cairo_background(WIDTH, HEIGHT)
        
        # HUD Assets
        self.score_panel = render_hud_panel(140, 40)
        self.heart_icon = render_heart_icon(32)
        
        # Pause Button Assets
        self.pause_btn_normal = render_pause_button_asset(48, hover=False)
        self.pause_btn_hover = render_pause_button_asset(48, hover=True)
        self.pause_rect = pygame.Rect(WIDTH - 60, 10, 48, 48) # Pindah ke kanan atas
        
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
            if isinstance(ans, float): ans = int(round(ans))
            if ans in answers: continue
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
                    self.score += 10
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
        
        # Level up speed
        if self.score > 0 and self.score % 50 == 0:
            new_level = 1 + self.score // 50
            if new_level > self.speed_level:
                self.speed_level = new_level
                FALL_SPEED = BASE_FALL_SPEED + (self.speed_level - 1) * 30
                self.speed_message_timer = 2.0
        if self.speed_message_timer > 0:
            self.speed_message_timer -= dt

    def draw(self, surf, mouse_pos):
        # 1. Background
        surf.blit(self.background_img, (0, 0))

        # 2. Bins (Layer bawah)
        surf.blit(self.bin_surface, (0, HEIGHT - self.bin_surface.get_height()))
        
        # 3. Falling Number
        if self.falling:
            self.falling.draw(surf)

        # 4. HUD (Heads Up Display) - Dibuat Rapi
        
        # --- Score Panel (Kiri Atas) ---
        panel_x, panel_y = 10, 10
        surf.blit(self.score_panel, (panel_x, panel_y))
        
        score_text = HUD_FONT.render(f"Score: {self.score}", True, (255, 255, 255))
        # Center text in panel
        sx = panel_x + (140 - score_text.get_width()) // 2
        sy = panel_y + (40 - score_text.get_height()) // 2
        surf.blit(score_text, (sx, sy))

        # --- Lives (Tengah Atas) ---
        # Gambar hati sejumlah nyawa
        start_x_lives = 170
        for i in range(self.lives):
            surf.blit(self.heart_icon, (start_x_lives + i * 35, 14))

        # --- Pause Button (Kanan Atas) ---
        is_hover = self.pause_rect.collidepoint(mouse_pos)
        btn_img = self.pause_btn_hover if is_hover else self.pause_btn_normal
        surf.blit(btn_img, self.pause_rect.topleft)

        # --- Level Up Message ---
        if self.speed_message_timer > 0:
            msg_font = pygame.font.SysFont('Georgia', 32, bold=True)
            msg_s = msg_font.render("SPEED UP!", True, (0,0,0)) # Shadow
            msg = msg_font.render("SPEED UP!", True, (255, 220, 80))
            
            cx, cy = WIDTH//2, 100
            surf.blit(msg_s, msg_s.get_rect(center=(cx+2, cy+2)))
            surf.blit(msg, msg.get_rect(center=(cx, cy)))

    def is_game_over(self):
        return self.lives <= 0

# ==============================================================================
# MENU UI HELPERS
# ==============================================================================
def draw_button(surface, rect, text, mouse_pos):
    hover = rect.collidepoint(mouse_pos)
    btn_img = render_menu_button(rect.width, rect.height, text, hover=hover)
    surface.blit(btn_img, rect.topleft)
    return hover # Return status hover jika butuh suara dsb

def draw_text_centered(surface, text, font, color, center_pos, shadow_offset=(2,2)):
    # Shadow
    shad = font.render(text, True, TEXT_SHADOW)
    sr = shad.get_rect(center=(center_pos[0]+shadow_offset[0], center_pos[1]+shadow_offset[1]))
    surface.blit(shad, sr)
    # Main
    txt = font.render(text, True, color)
    tr = txt.get_rect(center=center_pos)
    surface.blit(txt, tr)

# ==============================================================================
# MAIN MENU
# ==============================================================================
def main_menu():
    ops_list = [
        ("Penjumlahan (+)", ['+']),
        ("Pengurangan (-)", ['-']),
        ("Perkalian (x)", ['*']),
        ("Pembagian (/)", ['/']),
        ("Semua Operasi", ['+','-','*','/'])
    ]
    
    # 1. Siapkan Background
    scroll_bg = render_parchment_scroll(400, 500)
    scroll_rect = scroll_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
    bg_img = create_cairo_background(WIDTH, HEIGHT)

    # 2. PRE-RENDER TOMBOL (PENTING! Lakukan ini di luar loop)
    # Kita buat 2 versi gambar untuk setiap tombol: Normal dan Hover
    buttons = []
    base_y = scroll_rect.top + 140
    
    for i, (label, ops) in enumerate(ops_list):
        rect = pygame.Rect(0, 0, 260, 50)
        rect.centerx = WIDTH // 2
        rect.y = base_y + i * 65
        
        # Buat gambar SEKALI saja di sini
        img_normal = render_menu_button(rect.width, rect.height, label, hover=False)
        img_hover = render_menu_button(rect.width, rect.height, label, hover=True)
        
        # Simpan data tombol
        buttons.append({
            "rect": rect,
            "ops": ops,
            "img_normal": img_normal,
            "img_hover": img_hover
        })

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        # Gambar Background
        screen.blit(bg_img, (0,0))
        screen.blit(scroll_bg, scroll_rect)
        
        # Judul
        draw_text_centered(screen, "PILIH MODE", TITLE_FONT, (60, 40, 20), (WIDTH//2, scroll_rect.top + 60))
        draw_text_centered(screen, "Tantangan Matematika", SUBTITLE_FONT, (100, 80, 60), (WIDTH//2, scroll_rect.top + 100))

        # 3. Loop Gambar Tombol (Tinggal tempel gambar yang sudah jadi)
        for btn in buttons:
            rect = btn["rect"]
            is_hover = rect.collidepoint(mouse_pos)
            
            # Pilih gambar berdasarkan posisi mouse
            image_to_draw = btn["img_hover"] if is_hover else btn["img_normal"]
            
            screen.blit(image_to_draw, rect.topleft)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            return btn["ops"] # Kembalikan operasi yang dipilih

        pygame.display.flip()
        clock.tick(60)

# ==============================================================================
# PAUSE POPUP
# ==============================================================================
def pause_popup(surface, mouse_pos):
    # Overlay gelap
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    # Scroll Background
    w, h = 320, 350
    scroll = render_parchment_scroll(w, h)
    cx, cy = WIDTH//2, HEIGHT//2
    rect_scroll = scroll.get_rect(center=(cx, cy))
    surface.blit(scroll, rect_scroll)

    draw_text_centered(surface, "PAUSE", TITLE_FONT, (60, 40, 20), (cx, rect_scroll.top + 60))

    btn_w, btn_h = 220, 50
    gap = 15
    start_y = rect_scroll.top + 120
    
    resume_rect = pygame.Rect(cx - btn_w//2, start_y, btn_w, btn_h)
    restart_rect = pygame.Rect(cx - btn_w//2, start_y + btn_h + gap, btn_w, btn_h)
    menu_rect = pygame.Rect(cx - btn_w//2, start_y + 2*(btn_h + gap), btn_w, btn_h)

    draw_button(surface, resume_rect, "Lanjutkan", mouse_pos)
    draw_button(surface, restart_rect, "Ulangi", mouse_pos)
    draw_button(surface, menu_rect, "Keluar ke Menu", mouse_pos)

    return resume_rect, restart_rect, menu_rect

# ==============================================================================
# MAIN LOOP
# ==============================================================================
def main():
    state = "MENU"
    game = None
    paused = False
    
    # ==========================================
    # 1. SETUP ASET PAUSE (PRE-RENDER / CACHE)
    # ==========================================
    # Kita buat gambar-gambarnya SEKALI saja di sini agar tidak glitch/berat.
    
    # A. Overlay Gelap & Kertas Background
    pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pause_overlay.fill((0, 0, 0, 150)) # Hitam transparan

    pause_paper_w, pause_paper_h = 320, 350
    pause_paper_img = render_parchment_scroll(pause_paper_w, pause_paper_h)
    pause_paper_rect = pause_paper_img.get_rect(center=(WIDTH//2, HEIGHT//2))

    # B. Judul Pause
    pause_title = TITLE_FONT.render("PAUSE", True, (60, 40, 20))
    pause_title_rect = pause_title.get_rect(center=(WIDTH//2, pause_paper_rect.top + 60))

    # C. Tombol-tombol Pause (Normal & Hover)
    pause_btn_w, pause_btn_h = 220, 50
    pause_gap = 15
    pause_start_y = pause_paper_rect.top + 120
    
    # Data konfigurasi tombol
    pause_btn_data = [
        {"text": "Lanjutkan",      "action": "resume"},
        {"text": "Ulangi",         "action": "restart"},
        {"text": "Keluar ke Menu", "action": "menu"}
    ]

    pause_buttons = []
    
    for i, data in enumerate(pause_btn_data):
        # Tentukan posisi rect
        rect = pygame.Rect(0, 0, pause_btn_w, pause_btn_h)
        rect.centerx = WIDTH // 2
        rect.y = pause_start_y + i * (pause_btn_h + pause_gap)
        
        # RENDER GAMBAR SEKARANG (Agar tidak diulang-ulang)
        img_normal = render_menu_button(pause_btn_w, pause_btn_h, data["text"], hover=False)
        img_hover = render_menu_button(pause_btn_w, pause_btn_h, data["text"], hover=True)
        
        pause_buttons.append({
            "rect": rect,
            "action": data["action"],
            "img_normal": img_normal,
            "img_hover": img_hover
        })

    # ==========================================
    # 2. GAME LOOP UTAMA
    # ==========================================
    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        # --- MODE MENU ---
        if state == "MENU":
            allowed_ops = main_menu() # Pastikan main_menu() Anda sudah yang versi diperbaiki (tidak glitch)
            if allowed_ops is None: return # Quit
            game = Game(allowed_ops)
            paused = False
            state = "GAME"
            continue

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 1. Klik Tombol Pause Kecil (Di Pojok Kanan Atas Game)
                if not paused and not game.is_game_over():
                    if game.pause_rect.collidepoint(mouse_pos):
                        paused = True
                
                # 2. Klik Menu Pause (Saat sedang Pause)
                elif paused:
                    for btn in pause_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            act = btn["action"]
                            if act == "resume":
                                paused = False
                            elif act == "restart":
                                game = Game(game.allowed_ops) # Reset game
                                paused = False
                            elif act == "menu":
                                state = "MENU" # Balik ke menu utama
                                paused = False

                # 3. Klik Game Over
                elif game.is_game_over():
                     state = "MENU"

            # Shortcut Keyboard
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: game.move_dir = -1
                elif event.key == pygame.K_RIGHT: game.move_dir = 1
                elif event.key == pygame.K_r: state = "MENU"
                elif event.key == pygame.K_SPACE and game.falling and not paused:
                    game.falling.y = HEIGHT
                elif event.key == pygame.K_ESCAPE:
                    if not game.is_game_over(): paused = not paused

            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    game.move_dir = 0

        # --- UPDATE & DRAW ---
        move_dir = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: move_dir = -1
        if keys[pygame.K_RIGHT]: move_dir = 1
        
        if not paused and not game.is_game_over():
            game.update(dt, move_dir)

        # Gambar Game
        game.draw(screen, mouse_pos)

        # --- GAMBAR OVERLAY (PAUSE / GAME OVER) ---
        
        if paused:
            # Tinggal tempel gambar yang sudah dibuat di awal (Sangat Ringan)
            screen.blit(pause_overlay, (0, 0))
            screen.blit(pause_paper_img, pause_paper_rect)
            screen.blit(pause_title, pause_title_rect)
            
            for btn in pause_buttons:
                is_hover = btn["rect"].collidepoint(mouse_pos)
                # Pilih gambar berdasarkan hover
                image_to_draw = btn["img_hover"] if is_hover else btn["img_normal"]
                screen.blit(image_to_draw, btn["rect"])

        elif game.is_game_over():
            # Overlay sederhana untuk game over
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 180))
            screen.blit(ov, (0, 0))
            draw_text_centered(screen, "PERMAINAN SELESAI", TITLE_FONT, (255, 80, 80), (WIDTH//2, HEIGHT//2 - 20))
            draw_text_centered(screen, f"Skor Akhir: {game.score}", SUBTITLE_FONT, (255, 255, 255), (WIDTH//2, HEIGHT//2 + 30))
            draw_text_centered(screen, "Klik untuk kembali ke Menu", pygame.font.SysFont('Georgia', 18), (200, 200, 200), (WIDTH//2, HEIGHT//2 + 70))

        pygame.display.flip()

if __name__ == "__main__":
    main()