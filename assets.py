import math
import cairo
import pygame
import random

# Konversi cairo -> pygame
def cairo_surface_to_pygame(surf: cairo.ImageSurface) -> pygame.Surface:
    buf = surf.get_data()
    py_surf = pygame.image.frombuffer(buf, (surf.get_width(), surf.get_height()), 'ARGB')
    return py_surf.convert_alpha()

def render_menu_button(width, height, text, hover=False):
    # 1. Konfigurasi Warna & Style
    radius = 12
    line_width = 2
    
    if hover:
        # Gradasi Hover (Lebih Terang)
        color_top = (0.45, 0.45, 0.55, 1)
        color_bottom = (0.32, 0.32, 0.40, 1)
        border_color = (0.60, 0.60, 0.70, 1)
    else:
        # Gradasi Normal (Lebih Gelap)
        color_top = (0.28, 0.28, 0.35, 1)
        color_bottom = (0.18, 0.18, 0.25, 1)
        border_color = (0.15, 0.15, 0.20, 1)

    # 2. Setup Cairo Surface
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    ctx = cairo.Context(surf)

    # Menghitung area gambar (dikurangi line_width agar border tidak terpotong)
    # Offset 1 pixel untuk ketajaman garis (anti-aliasing)
    rect_x = line_width / 2.0
    rect_y = line_width / 2.0
    rect_w = width - line_width
    rect_h = height - line_width

    # 3. Membuat Path Rounded Rectangle
    ctx.new_path()
    # Kanan Bawah
    ctx.arc(rect_x + rect_w - radius, rect_y + rect_h - radius, radius, 0, math.pi/2)
    # Kiri Bawah
    ctx.arc(rect_x + radius, rect_y + rect_h - radius, radius, math.pi/2, math.pi)
    # Kiri Atas
    ctx.arc(rect_x + radius, rect_y + radius, radius, math.pi, 3*math.pi/2)
    # Kanan Atas
    ctx.arc(rect_x + rect_w - radius, rect_y + radius, radius, 3*math.pi/2, 2*math.pi)
    ctx.close_path()

    # 4. Mengisi dengan Gradasi (Linear Gradient)
    # Gradasi dari atas ke bawah untuk efek cahaya
    pat = cairo.LinearGradient(0, 0, 0, height)
    pat.add_color_stop_rgba(0, *color_top)      # Atas
    pat.add_color_stop_rgba(1, *color_bottom)   # Bawah
    
    ctx.set_source(pat)
    ctx.fill_preserve() # Simpan path untuk digunakan border

    # 5. Menggambar Border (Stroke)
    ctx.set_source_rgba(*border_color)
    ctx.set_line_width(line_width)
    ctx.stroke()

    # 6. Render Text via Pygame
    # Konversi ke surface pygame
    # Pastikan fungsi 'cairo_surface_to_pygame' sudah didefinisikan sebelumnya atau diimpor
    ps = cairo_surface_to_pygame(surf) 
    
    pygame_font = pygame.font.SysFont("Arial", 22, bold=True)
    
    # Text Shadow (Hitam transparan) untuk kedalaman
    text_shadow = pygame_font.render(text, True, (0, 0, 0))
    text_shadow.set_alpha(100) # Transparansi bayangan
    shadow_rect = text_shadow.get_rect(center=(width//2 + 1, height//2 + 2))
    ps.blit(text_shadow, shadow_rect)

    # Text Utama (Putih)
    text_surf = pygame_font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(width//2, height//2))
    ps.blit(text_surf, text_rect)

    return ps

def create_cairo_background(width, height):
    # Setup Surface Cairo
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    ctx = cairo.Context(surface)

    # --- LAYER 1: LANGIT (Sky) ---
    # Gradasi dari biru langit cerah di atas ke biru yang lebih muda di cakrawala
    sky_pat = cairo.LinearGradient(0, 0, 0, height)
    sky_pat.add_color_stop_rgb(0, 0.4, 0.7, 1.0)  # Biru Langit Cerah (Atas)
    sky_pat.add_color_stop_rgb(1, 0.7, 0.9, 1.0)  # Biru Muda Pucat (Bawah)
    
    ctx.rectangle(0, 0, width, height)
    ctx.set_source(sky_pat)
    ctx.fill()
    
    # (Opsional) Tambahkan sedikit "glow" oranye di sekitar matahari
    # ctx.set_source_rgba(1.0, 0.7, 0.1, 0.3) # Oranye transparan
    # ctx.set_line_width(8)
    # ctx.stroke() # Gunakan stroke pada path lingkaran yang sama

    # --- LAYER 3: BUKIT BELAKANG (Back Hills) ---
    # Warna hijau sedikit lebih gelap/kebiruan untuk kesan jauh
    ctx.set_source_rgb(0.3, 0.7, 0.4) 
    
    ctx.new_path()
    # Mulai dari kiri tengah
    ctx.move_to(0, height * 0.6)
    
    # Gambar kurva bergelombang (Bezier Curve)
    # curve_to(control_point_1_x, cp1_y, control_point_2_x, cp2_y, end_x, end_y)
    ctx.curve_to(width * 0.3, height * 0.4,  # Titik kontrol 1 (puncak bukit 1)
                 width * 0.7, height * 0.7,  # Titik kontrol 2 (lembah)
                 width, height * 0.55)       # Titik akhir (kanan)
                 
    # Tutup path ke sudut bawah agar bisa di-fill
    ctx.line_to(width, height)
    ctx.line_to(0, height)
    ctx.close_path()
    ctx.fill()

    # --- LAYER 4: BUKIT DEPAN (Front Hills) ---
    # Warna hijau cerah, segar
    ctx.set_source_rgb(0.4, 0.8, 0.3) 

    ctx.new_path()
    # Mulai dari kiri, sedikit lebih rendah dari bukit belakang
    ctx.move_to(0, height * 0.75)
    
    # Kurva bukit depan, lebih landai
    ctx.curve_to(width * 0.4, height * 0.85, # Lembah kecil
                 width * 0.6, height * 0.65, # Puncak bukit depan
                 width, height * 0.8)        # Titik akhir
                 
    # Tutup path ke bawah
    ctx.line_to(width, height)
    ctx.line_to(0, height)
    ctx.close_path()
    ctx.fill()

    # --- Convert Cairo → Pygame Surface ---
    # Memastikan data di-flush sebelum diambil
    surface.flush() 
    buf = surface.get_data()
    # Menggunakan "ARGB" karena format surface cairo di atas adalah ARGB32
    return pygame.image.frombuffer(buf, (int(width), int(height)), "ARGB")

# Render tempat jawaban (bins) dengan desain lebih modern
def render_bins_cairo(width, height, bin_rects, bin_labels):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)

    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    # Palet warna yang lebih vibrant dan konsisten
    modern_colors = [
        (0.40, 0.76, 0.95),  # Biru cerah
        (0.95, 0.55, 0.76),  # Pink
        (0.55, 0.90, 0.65),  # Hijau mint
        (1.00, 0.80, 0.40),  # Kuning emas
    ]

    for idx, (rect, label) in enumerate(zip(bin_rects, bin_labels)):
        x, y, w, h = rect
        r, g, b = modern_colors[idx % len(modern_colors)]

        # Shadow dengan blur effect (multiple layers)
        for i in range(4):
            alpha = 0.08 * (4 - i)
            offset = i * 1.5
            ctx.set_source_rgba(0, 0, 0, alpha)
            rounded_rectangle(ctx, x + offset + 2, y + offset + 4, w, h, h * 0.2)
            ctx.fill()

        # Gradient background yang lebih smooth
        grad = cairo.LinearGradient(x, y, x, y + h)
        grad.add_color_stop_rgb(0, min(r + 0.15, 1), min(g + 0.15, 1), min(b + 0.15, 1))
        grad.add_color_stop_rgb(0.5, r, g, b)
        grad.add_color_stop_rgb(1, max(r - 0.1, 0), max(g - 0.1, 0), max(b - 0.1, 0))
        
        ctx.set_source(grad)
        rounded_rectangle(ctx, x, y, w, h, h * 0.2)
        ctx.fill()

        # Border dengan gradient
        border_grad = cairo.LinearGradient(x, y, x, y + h)
        border_grad.add_color_stop_rgba(0, 1, 1, 1, 0.4)
        border_grad.add_color_stop_rgba(0.5, 1, 1, 1, 0.2)
        border_grad.add_color_stop_rgba(1, 0, 0, 0, 0.2)
        
        ctx.set_source(border_grad)
        rounded_rectangle(ctx, x, y, w, h, h * 0.2)
        ctx.set_line_width(3)
        ctx.stroke()

        # Label dengan shadow
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(h * 0.35)

        te = ctx.text_extents(label)
        text_x = x + (w - te.x_advance) / 2
        text_y = y + (h + te.height) / 2

        # Text shadow
        ctx.set_source_rgba(0, 0, 0, 0.3)
        ctx.move_to(text_x + 2, text_y + 2)
        ctx.show_text(label)

        # Text utama
        ctx.set_source_rgb(1, 1, 1)
        ctx.move_to(text_x, text_y)
        ctx.show_text(label)

    return cairo_surface_to_pygame(surf)

def rounded_rectangle(ctx, x, y, width, height, radius):
    """Helper untuk membuat rounded rectangle"""
    ctx.new_path()
    ctx.arc(x + radius, y + radius, radius, math.pi, 3 * math.pi / 2)
    ctx.arc(x + width - radius, y + radius, radius, 3 * math.pi / 2, 0)
    ctx.arc(x + width - radius, y + height - radius, radius, 0, math.pi / 2)
    ctx.arc(x + radius, y + height - radius, radius, math.pi / 2, math.pi)
    ctx.close_path()


LAST_SHAPE = None
LAST_COLOR = None

def render_falling_block(value):
    """Render falling block dengan desain lebih polished"""
    global LAST_SHAPE, LAST_COLOR

    w, h = 90, 90
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    # Palet warna yang lebih vibrant
    vibrant_colors = [
        (0.98, 0.40, 0.52),  # Coral pink
        (1.00, 0.60, 0.20),  # Orange
        (0.30, 0.85, 0.95),  # Cyan
        (0.60, 0.45, 0.95),  # Purple
        (0.95, 0.75, 0.30),  # Gold
        (0.40, 0.95, 0.60),  # Green
        (0.95, 0.35, 0.75),  # Magenta
        (0.35, 0.70, 0.95),  # Blue
    ]

    color_choices = [c for c in vibrant_colors if c != LAST_COLOR]
    r, g, b = random.choice(color_choices)
    LAST_COLOR = (r, g, b)

    # Simplified shape list (lebih fokus dan mudah dikenali)
    shapes = ["star", "circle", "hexagon", "heart", "diamond", "pentagon", "triangle", "square"]
    # shapes = ["heart"]

    shape_choices = [s for s in shapes if s != LAST_SHAPE]
    shape = random.choice(shape_choices)
    LAST_SHAPE = shape

    cx, cy = w / 2, h / 2

    # Multi-layer shadow untuk depth
    for i in range(4):
        alpha = 0.1 * (4 - i)
        offset = 1.5 + i * 1.2
        ctx.set_source_rgba(0, 0, 0, alpha)
        draw_shape(ctx, shape, cx + offset, cy + offset, 32 + i * 0.5)
        ctx.fill()

    # Gradient yang lebih kompleks
    grad = cairo.RadialGradient(cx - 8, cy - 8, 5, cx, cy, 35)
    grad.add_color_stop_rgba(0, min(r + 0.25, 1), min(g + 0.25, 1), min(b + 0.25, 1), 1)
    grad.add_color_stop_rgba(0.4, r, g, b, 1)
    grad.add_color_stop_rgba(1, max(r - 0.25, 0), max(g - 0.25, 0), max(b - 0.25, 0), 1)

    ctx.set_source(grad)
    draw_shape(ctx, shape, cx, cy, 32)
    ctx.fill()

    # Border outline
    ctx.set_source_rgba(1, 1, 1, 0.4)
    draw_shape(ctx, shape, cx, cy, 32)
    ctx.set_line_width(2.5)
    ctx.stroke()

    # Angka dengan efek 3D
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    
    # Multiple shadow layers untuk 3D effect
    for offset in [(3, 3), (2, 2), (1, 1)]:
        ctx.set_source_rgba(0, 0, 0, 0.15)
        ctx.set_font_size(36)
        te = ctx.text_extents(str(value))
        ctx.move_to((w - te.x_advance) / 2 + offset[0], (h + te.height) / 2 + offset[1])
        ctx.show_text(str(value))

    # Angka utama dengan outline
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_font_size(36)
    te = ctx.text_extents(str(value))
    text_x = (w - te.x_advance) / 2
    text_y = (h + te.height) / 2
    
    ctx.move_to(text_x, text_y)
    ctx.text_path(str(value))
    ctx.fill_preserve()
    
    # Text outline
    ctx.set_source_rgba(0, 0, 0, 0.4)
    ctx.set_line_width(1.5)
    ctx.stroke()

    return cairo_surface_to_pygame(surf)

def draw_shape(ctx, shape, cx, cy, size):
    """Helper function untuk menggambar berbagai bentuk"""
    ctx.new_path()
    
    if shape == "circle":
        size = size * 0.9
        ctx.arc(cx, cy, size, 0, 2 * math.pi)
    
    if shape == "star":
        # Bintang 5 ujung
        size = size * 1.2
        spikes, outer_r, inner_r = 5, size, size * 0.45
        angle = -math.pi / 2
        step = math.pi / spikes
        for i in range(spikes * 2):
            r_val = outer_r if i % 2 == 0 else inner_r
            px = cx + math.cos(angle) * r_val
            py = cy + math.sin(angle) * r_val
            if i == 0:
                ctx.move_to(px, py)
            else:
                ctx.line_to(px, py)
            angle += step
        ctx.close_path()
    
    elif shape == "heart":
        # Hati
        scale = (size * 2.2) / 30
        offset_y = size * 0.15
        ctx.move_to(cx, cy + 12 * scale + offset_y)
        ctx.curve_to(cx + 30 * scale, cy - 2 * scale + offset_y, cx + 12 * scale, cy - 24 * scale + offset_y, cx, cy - 10 * scale + offset_y)
        ctx.curve_to(cx - 12 * scale, cy - 24 * scale + offset_y, cx - 30 * scale, cy - 2 * scale + offset_y, cx, cy + 12 * scale + offset_y)
        ctx.close_path()
    
    elif shape == "hexagon":
        # Hexagon
        for i in range(6):
            angle = i * math.pi / 3
            px = cx + math.cos(angle) * size
            py = cy + math.sin(angle) * size
            if i == 0:
                ctx.move_to(px, py)
            else:
                ctx.line_to(px, py)
        ctx.close_path()
    
    elif shape == "diamond":
        # Diamond
        size = size * 1.3
        ctx.move_to(cx, cy - size)
        ctx.line_to(cx + size * 0.7, cy)
        ctx.line_to(cx, cy + size)
        ctx.line_to(cx - size * 0.7, cy)
        ctx.close_path()
    
    elif shape == "pentagon":
        # Pentagon
        for i in range(5):
            angle = -math.pi / 2 + i * 2 * math.pi / 5
            px = cx + math.cos(angle) * size
            py = cy + math.sin(angle) * size
            if i == 0:
                ctx.move_to(px, py)
            else:
                ctx.line_to(px, py)
        ctx.close_path()
    
    elif shape == "triangle":
        # Triangle
        size = size * 1.2
        offset_y = size * 0.12  # Offset untuk menurunkan posisi
        ctx.move_to(cx, cy - size + offset_y)
        ctx.line_to(cx + size * 0.87, cy + size * 0.5 + offset_y)
        ctx.line_to(cx - size * 0.87, cy + size * 0.5 + offset_y)
        ctx.close_path()
    
    elif shape == "square":
        # Square dengan sedikit rotasi
        size = size * 0.9
        angle = math.pi / 4
        for i in range(4):
            a = angle + i * math.pi / 2
            px = cx + math.cos(a) * size * 1.4
            py = cy + math.sin(a) * size * 1.4
            if i == 0:
                ctx.move_to(px, py)
            else:
                ctx.line_to(px, py)
        ctx.close_path()