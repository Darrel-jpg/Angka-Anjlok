# ----------------------------
# game_assets.py
# ----------------------------
import math
import cairo
import pygame
import random

# konversi cairo -> pygame
def cairo_surface_to_pygame(surf: cairo.ImageSurface) -> pygame.Surface:
    buf = surf.get_data()
    py_surf = pygame.image.frombuffer(buf, (surf.get_width(), surf.get_height()), 'ARGB')
    return py_surf.convert_alpha()

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

    # --- LAYER 2: MATAHARI (Sun) ---
    sun_x = width * 0.85  # Posisi X (85% ke kanan)
    sun_y = height * 0.2  # Posisi Y (20% dari atas)
    sun_radius = height * 0.1 # Radius matahari

    ctx.set_source_rgb(1.0, 0.9, 0.2) # Kuning cerah
    ctx.new_path()
    ctx.arc(sun_x, sun_y, sun_radius, 0, 2 * math.pi)
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
# render tempat jawaban (bin)
def render_bins_cairo(width, height, bin_rects, bin_labels):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)

    ctx.set_source_rgba(0,0,0,0)
    ctx.paint()

    pastel_bins = [
        (0.75, 0.90, 1.0),
        (1.0, 0.85, 0.95),
        (0.85, 1.0, 0.85),
        (1.0, 0.97, 0.80),
    ]

    for rect, label in zip(bin_rects, bin_labels):
        x, y, w, h = rect
        r, g, b = random.choice(pastel_bins)

        # shadow
        ctx.set_source_rgba(0,0,0,0.22)
        ctx.rectangle(x + 3, y + 6, w, h)
        ctx.fill()

        # cloud gradient
        radius = h * 0.35
        grad = cairo.RadialGradient(
            x + w/2 - 10, y + h/2 - 10, 5,
            x + w/2,     y + h/2,     h*0.7
        )
        grad.add_color_stop_rgb(0, min(r+0.12,1), min(g+0.12,1), min(b+0.12,1))
        grad.add_color_stop_rgb(1, r, g, b)

        ctx.set_source(grad)

        ctx.new_path()
        ctx.arc(x + radius,     y + radius,     radius, math.pi, 3*math.pi/2)
        ctx.arc(x + w-radius,   y + radius,     radius, 3*math.pi/2, 0)
        ctx.arc(x + w-radius,   y + h-radius,   radius, 0, math.pi/2)
        ctx.arc(x + radius,     y + h-radius,   radius, math.pi/2, math.pi)
        ctx.close_path()
        ctx.fill()

        # highlight
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.arc(x + w*0.32, y + h*0.35, h*0.18, 0, 2*math.pi)
        ctx.fill()

        # label
        ctx.set_source_rgb(0.15, 0.15, 0.15)
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(h * 0.38)

        te = ctx.text_extents(label)
        text_x = x + (w - te.x_advance) / 2
        text_y = y + (h + te.height) / 2 - h*0.05

        ctx.move_to(text_x, text_y)
        ctx.show_text(label)

    return cairo_surface_to_pygame(surf)

LAST_SHAPE = None
LAST_COLOR = None


def render_falling_block(value):
    global LAST_SHAPE, LAST_COLOR

    w, h = 80, 80
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    cheerful_colors = [
        (1.00, 0.30, 0.50),  # Pink Permen
        (1.00, 0.50, 0.10),  # Oranye Jeruk
        (1.00, 0.80, 0.10),  # Kuning Matahari
        (0.30, 0.90, 0.30),  # Hijau Apel
        (0.20, 0.75, 1.00),  # Biru Langit
        (0.60, 0.40, 1.00),  # Ungu Anggur
        (1.00, 0.45, 0.85),  # Merah Jambu
        (0.25, 1.00, 0.75),  # Hijau Mint
        (1.00, 0.20, 0.30),  # Merah Ceri
        (0.95, 0.70, 0.20),  # Emas
    ]

    color_choices = [c for c in cheerful_colors if c != LAST_COLOR]
    r, g, b = random.choice(color_choices)
    LAST_COLOR = (r, g, b)

    shapes = [
        "smiley",           # Wajah tersenyum
        "star",             # Bintang
        "heart",            # Hati
        "balloon",          # Balon
        "ice_cream",        # Es krim
        "lollipop",         # Permen lolipop
        "apple",            # Apel
        "flower",           # Bunga
        "sun",              # Matahari
        "cloud",            # Awan
        "rainbow",          # Pelangi
        "cupcake",          # Kue
        "butterfly",        # Kupu-kupu
        "fish",             # Ikan
        "teddy_bear",       # Beruang
        "cat",              # Kucing
        "pizza",            # Pizza
        "house",            # Rumah
        "car",              # Mobil
        "kite",             # Layang-layang
    ]

    shape_choices = [s for s in shapes if s != LAST_SHAPE]
    shape = random.choice(shape_choices)
    LAST_SHAPE = shape

    for i in range(3):
        alpha = 0.08 * (3 - i)
        offset = 2 + i * 1.5
        ctx.set_source_rgba(0, 0, 0, alpha)
        ctx.arc(w/2 + offset, h/2 + offset, 35 + i, 0, 2*math.pi)
        ctx.fill()
        
    grad = cairo.RadialGradient(w/2 - 10, h/2 - 10, 3, w/2, h/2, 38)
    grad.add_color_stop_rgba(0, min(r+0.3,1), min(g+0.3,1), min(b+0.3,1), 1)
    grad.add_color_stop_rgba(0.5, r, g, b, 1)
    grad.add_color_stop_rgba(1, max(r-0.2,0), max(g-0.2,0), max(b-0.2,0), 1)

    ctx.set_source(grad)

    cx, cy = w/2, h/2

    if shape == "smiley":
        # Wajah bulat
        ctx.arc(cx, cy, 28, 0, 2*math.pi)
        ctx.fill()
        # Mata kiri
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.arc(cx - 10, cy - 8, 3, 0, 2*math.pi)
        ctx.fill()
        # Mata kanan
        ctx.arc(cx + 10, cy - 8, 3, 0, 2*math.pi)
        ctx.fill()
        # Senyum
        ctx.arc(cx, cy + 2, 15, 0, math.pi)
        ctx.set_line_width(3)
        ctx.stroke()

    elif shape == "star":
        # Bintang 5 ujung
        ctx.new_path()
        spikes, outer_r, inner_r = 5, 30, 14
        angle = -math.pi/2
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
        ctx.fill()

    elif shape == "heart":
        # Hati
        ctx.new_path()
        ctx.move_to(cx, cy + 12)
        ctx.curve_to(cx + 30, cy - 8, cx + 12, cy - 30, cx, cy - 10)
        ctx.curve_to(cx - 12, cy - 30, cx - 30, cy - 8, cx, cy + 12)
        ctx.close_path()
        ctx.fill()

    elif shape == "balloon":
        # Balon
        ctx.new_path()
        ctx.arc(cx, cy - 5, 25, 0, 2*math.pi)
        ctx.fill()
        # Tali balon
        ctx.set_source_rgba(0.3, 0.3, 0.3, 0.7)
        ctx.move_to(cx, cy + 20)
        ctx.curve_to(cx - 5, cy + 30, cx + 5, cy + 35, cx, cy + 40)
        ctx.set_line_width(2)
        ctx.stroke()

    elif shape == "ice_cream":
        # Es krim
        # Cone
        ctx.set_source_rgb(0.85, 0.65, 0.35)
        ctx.new_path()
        ctx.move_to(cx - 15, cy + 5)
        ctx.line_to(cx + 15, cy + 5)
        ctx.line_to(cx, cy + 32)
        ctx.close_path()
        ctx.fill()
        # Ice cream
        ctx.set_source(grad)
        ctx.arc(cx, cy - 5, 22, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx - 12, cy - 15, 15, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx + 12, cy - 15, 15, 0, 2*math.pi)
        ctx.fill()

    elif shape == "lollipop":
        # Permen lolipop
        ctx.arc(cx, cy - 8, 22, 0, 2*math.pi)
        ctx.fill()
        # Batang
        ctx.set_source_rgba(0.9, 0.9, 0.9, 0.9)
        ctx.rectangle(cx - 2, cy + 14, 4, 20)
        ctx.fill()
        # Swirl
        ctx.set_source_rgba(1, 1, 1, 0.4)
        ctx.arc(cx, cy - 8, 16, 0, math.pi)
        ctx.set_line_width(3)
        ctx.stroke()

    elif shape == "apple":
        # Apel
        ctx.arc(cx, cy + 2, 26, 0, 2*math.pi)
        ctx.fill()
        # Daun
        ctx.set_source_rgb(0.2, 0.7, 0.2)
        ctx.new_path()
        ctx.arc(cx + 8, cy - 22, 8, 0, 2*math.pi)
        ctx.fill()
        # Batang
        ctx.set_source_rgb(0.4, 0.3, 0.2)
        ctx.rectangle(cx - 1, cy - 24, 2, 8)
        ctx.fill()

    elif shape == "flower":
        # Bunga 6 kelopak
        for i in range(6):
            angle = i * (math.pi/3)
            px = cx + math.cos(angle) * 18
            py = cy + math.sin(angle) * 18
            ctx.arc(px, py, 12, 0, 2*math.pi)
            ctx.fill()
        # Tengah bunga
        ctx.set_source_rgb(1, 0.9, 0.3)
        ctx.arc(cx, cy, 10, 0, 2*math.pi)
        ctx.fill()

    elif shape == "sun":
        # Matahari
        ctx.arc(cx, cy, 20, 0, 2*math.pi)
        ctx.fill()
        # Sinar
        for i in range(8):
            angle = i * (math.pi/4)
            x1 = cx + math.cos(angle) * 22
            y1 = cy + math.sin(angle) * 22
            x2 = cx + math.cos(angle) * 32
            y2 = cy + math.sin(angle) * 32
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
            ctx.set_line_width(3)
            ctx.stroke()

    elif shape == "cloud":
        # Awan
        ctx.arc(cx - 15, cy, 18, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx + 15, cy, 20, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx, cy - 10, 18, 0, 2*math.pi)
        ctx.fill()

    elif shape == "rainbow":
        # Pelangi
        colors_rainbow = [
            (1, 0.2, 0.2), (1, 0.6, 0.2), (1, 0.9, 0.2),
            (0.3, 0.9, 0.3), (0.2, 0.5, 1), (0.5, 0.3, 1)
        ]
        for i, col in enumerate(colors_rainbow):
            ctx.set_source_rgb(*col)
            ctx.arc(cx, cy + 10, 28 - i*4, math.pi, 2*math.pi)
            ctx.set_line_width(3)
            ctx.stroke()

    elif shape == "cupcake":
        # Kue cup
        # Cup
        ctx.set_source_rgb(0.9, 0.7, 0.5)
        ctx.new_path()
        ctx.move_to(cx - 18, cy + 10)
        ctx.line_to(cx - 14, cy + 28)
        ctx.line_to(cx + 14, cy + 28)
        ctx.line_to(cx + 18, cy + 10)
        ctx.close_path()
        ctx.fill()
        # Frosting
        ctx.set_source(grad)
        ctx.arc(cx - 10, cy + 2, 12, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx + 10, cy + 2, 12, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx, cy - 10, 14, 0, 2*math.pi)
        ctx.fill()

    elif shape == "butterfly":
        # Kupu-kupu
        # Sayap kiri
        ctx.arc(cx - 16, cy - 8, 16, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx - 16, cy + 10, 14, 0, 2*math.pi)
        ctx.fill()
        # Sayap kanan
        ctx.arc(cx + 16, cy - 8, 16, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx + 16, cy + 10, 14, 0, 2*math.pi)
        ctx.fill()
        # Badan
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.rectangle(cx - 3, cy - 22, 6, 44)
        ctx.fill()

    elif shape == "fish":
        # Ikan
        # Badan
        ctx.arc(cx + 3, cy, 22, 0, 2*math.pi)
        ctx.fill()
        # Ekor
        ctx.new_path()
        ctx.move_to(cx - 18, cy)
        ctx.line_to(cx - 30, cy - 15)
        ctx.line_to(cx - 30, cy + 15)
        ctx.close_path()
        ctx.fill()
        # Mata
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(cx + 12, cy - 5, 5, 0, 2*math.pi)
        ctx.fill()
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.arc(cx + 13, cy - 5, 2, 0, 2*math.pi)
        ctx.fill()

    elif shape == "teddy_bear":
        # Beruang
        # Kepala
        ctx.arc(cx, cy, 20, 0, 2*math.pi)
        ctx.fill()
        # Telinga kiri
        ctx.arc(cx - 15, cy - 18, 10, 0, 2*math.pi)
        ctx.fill()
        # Telinga kanan
        ctx.arc(cx + 15, cy - 18, 10, 0, 2*math.pi)
        ctx.fill()
        # Moncong
        ctx.set_source_rgba(1, 0.9, 0.8, 0.9)
        ctx.arc(cx, cy + 8, 12, 0, 2*math.pi)
        ctx.fill()
        # Mata
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.arc(cx - 8, cy - 5, 2, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx + 8, cy - 5, 2, 0, 2*math.pi)
        ctx.fill()

    elif shape == "cat":
        # Kucing
        # Kepala
        ctx.arc(cx, cy, 22, 0, 2*math.pi)
        ctx.fill()
        # Telinga kiri
        ctx.new_path()
        ctx.move_to(cx - 20, cy - 18)
        ctx.line_to(cx - 10, cy - 25)
        ctx.line_to(cx - 5, cy - 18)
        ctx.close_path()
        ctx.fill()
        # Telinga kanan
        ctx.move_to(cx + 20, cy - 18)
        ctx.line_to(cx + 10, cy - 25)
        ctx.line_to(cx + 5, cy - 18)
        ctx.close_path()
        ctx.fill()
        # Mata
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.arc(cx - 8, cy - 3, 2, 0, 2*math.pi)
        ctx.fill()
        ctx.arc(cx + 8, cy - 3, 2, 0, 2*math.pi)
        ctx.fill()

    elif shape == "pizza":
        # Pizza
        ctx.new_path()
        ctx.move_to(cx, cy - 25)
        ctx.line_to(cx + 28, cy + 20)
        ctx.line_to(cx - 28, cy + 20)
        ctx.close_path()
        ctx.fill()
        # Topping
        ctx.set_source_rgb(0.9, 0.3, 0.2)
        for pos in [(cx-10, cy-5), (cx+8, cy), (cx-5, cy+10)]:
            ctx.arc(pos[0], pos[1], 4, 0, 2*math.pi)
            ctx.fill()

    elif shape == "house":
        # Rumah
        # Dinding
        ctx.rectangle(cx - 20, cy - 5, 40, 30)
        ctx.fill()
        # Atap
        ctx.new_path()
        ctx.move_to(cx - 25, cy - 5)
        ctx.line_to(cx, cy - 28)
        ctx.line_to(cx + 25, cy - 5)
        ctx.close_path()
        ctx.fill()
        # Pintu
        ctx.set_source_rgba(0.4, 0.3, 0.2, 0.8)
        ctx.rectangle(cx - 8, cy + 8, 16, 17)
        ctx.fill()

    elif shape == "car":
        # Mobil
        # Badan
        ctx.rectangle(cx - 25, cy + 5, 50, 15)
        ctx.fill()
        # Atap
        ctx.rectangle(cx - 15, cy - 8, 30, 13)
        ctx.fill()
        # Roda kiri
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.arc(cx - 15, cy + 22, 6, 0, 2*math.pi)
        ctx.fill()
        # Roda kanan
        ctx.arc(cx + 15, cy + 22, 6, 0, 2*math.pi)
        ctx.fill()

    elif shape == "kite":
        # Layang-layang
        ctx.new_path()
        ctx.move_to(cx, cy - 28)
        ctx.line_to(cx + 22, cy)
        ctx.line_to(cx, cy + 28)
        ctx.line_to(cx - 22, cy)
        ctx.close_path()
        ctx.fill()
        # Tali
        ctx.set_source_rgba(0.3, 0.3, 0.3, 0.6)
        ctx.move_to(cx, cy + 28)
        ctx.line_to(cx + 5, cy + 38)
        ctx.set_line_width(2)
        ctx.stroke()

    # Bayangan
    ctx.set_source_rgba(0, 0, 0, 0.4)
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(34)
    te = ctx.text_extents(str(value))
    ctx.move_to((w - te.x_advance)/2 + 1, (h + te.height)/2)
    ctx.show_text(str(value))

    # Angka utama
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_font_size(34)
    ctx.move_to((w - te.x_advance)/2, (h + te.height)/2 - 1)
    ctx.show_text(str(value))

    return cairo_surface_to_pygame(surf)