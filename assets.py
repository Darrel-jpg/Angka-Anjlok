import math
import cairo
import pygame
import random

# ==============================================================================
# UTILITY: KONVERSI CAIRO KE PYGAME
# ==============================================================================
def cairo_surface_to_pygame(surf: cairo.ImageSurface) -> pygame.Surface:
    buf = surf.get_data()
    return pygame.image.frombuffer(
        buf, 
        (surf.get_width(), surf.get_height()), 
        'BGRA'
    ).convert_alpha()

# ==============================================================================
# 1. MENU BUTTON (Sama seperti sebelumnya)
# ==============================================================================
def render_menu_button(width, height, text, hover=False):
    radius = 12
    line_width = 2
    
    if hover:
        color_top = (0.45, 0.45, 0.55, 1)
        color_bottom = (0.32, 0.32, 0.40, 1)
        border_color = (0.60, 0.60, 0.70, 1)
    else:
        color_top = (0.28, 0.28, 0.35, 1)
        color_bottom = (0.18, 0.18, 0.25, 1)
        border_color = (0.15, 0.15, 0.20, 1)

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    ctx = cairo.Context(surf)

    rect_x, rect_y = line_width / 2.0, line_width / 2.0
    rect_w, rect_h = width - line_width, height - line_width

    # Rounded Path
    ctx.new_path()
    ctx.arc(rect_x + rect_w - radius, rect_y + rect_h - radius, radius, 0, math.pi/2)
    ctx.arc(rect_x + radius, rect_y + rect_h - radius, radius, math.pi/2, math.pi)
    ctx.arc(rect_x + radius, rect_y + radius, radius, math.pi, 3*math.pi/2)
    ctx.arc(rect_x + rect_w - radius, rect_y + radius, radius, 3*math.pi/2, 2*math.pi)
    ctx.close_path()

    pat = cairo.LinearGradient(0, 0, 0, height)
    pat.add_color_stop_rgba(0, *color_top)
    pat.add_color_stop_rgba(1, *color_bottom)
    ctx.set_source(pat)
    ctx.fill_preserve()

    ctx.set_source_rgba(*border_color)
    ctx.set_line_width(line_width)
    ctx.stroke()

    ps = cairo_surface_to_pygame(surf) 
    pygame_font = pygame.font.SysFont("Arial", 22, bold=True)
    
    text_shadow = pygame_font.render(text, True, (0, 0, 0))
    text_shadow.set_alpha(100)
    shadow_rect = text_shadow.get_rect(center=(width//2 + 1, height//2 + 2))
    ps.blit(text_shadow, shadow_rect)

    text_surf = pygame_font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(width//2, height//2))
    ps.blit(text_surf, text_rect)

    return ps

# ==============================================================================
# 2. BACKGROUND (DITINGKATKAN: FANTASY FOREST FLOOR)
# ==============================================================================
def create_cairo_background(width, height):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    ctx = cairo.Context(surface)

    # Palette Warna (Lebih kaya dan sinematik)
    GROUND_DARK = (0.15, 0.12, 0.10)
    GROUND_MID = (0.25, 0.20, 0.15)
    MOSS_DARK = (0.20, 0.35, 0.15)
    MOSS_LIGHT = (0.35, 0.50, 0.25)
    LIGHT_RAY = (1.0, 0.95, 0.8, 0.08)

    # 1. Base Ground (Tanah Gelap)
    ctx.set_source_rgb(*GROUND_DARK)
    ctx.paint()

    # 2. Texture Tanah (Noise & Blotches)
    for _ in range(150):
        x = random.randint(0, int(width))
        y = random.randint(0, int(height))
        rad = random.randint(20, 100)
        ctx.set_source_rgba(*GROUND_MID, 0.3)
        ctx.arc(x, y, rad, 0, 2*math.pi)
        ctx.fill()

    # 3. Lumut/Rumput Halus (Mossy Patches)
    def draw_moss_clump(mx, my, size_base):
        ctx.save()
        ctx.translate(mx, my)
        particles = int(size_base * 2)
        for _ in range(particles):
            ox = random.uniform(-size_base, size_base)
            oy = random.uniform(-size_base, size_base)
            size = random.uniform(2, 6)
            ctx.set_source_rgba(*MOSS_DARK, 0.6)
            ctx.arc(ox, oy, size, 0, 2*math.pi)
            ctx.fill()
            
            # Highlight
            if random.random() > 0.7:
                ctx.set_source_rgba(*MOSS_LIGHT, 0.5)
                ctx.arc(ox+1, oy-1, size*0.6, 0, 2*math.pi)
                ctx.fill()
        ctx.restore()

    for _ in range(30):
        draw_moss_clump(random.randint(0, int(width)), random.randint(0, int(height)), 40)

    # 4. God Rays (Cahaya Masuk)
    ctx.save()
    ctx.rotate(math.radians(-15)) # Miringkan cahaya
    for _ in range(5):
        lx = random.randint(-200, int(width))
        ly = random.randint(-100, int(height))
        w_ray = random.randint(50, 150)
        h_ray = height * 2
        
        grad = cairo.LinearGradient(lx, 0, lx, h_ray)
        grad.add_color_stop_rgba(0, *LIGHT_RAY)
        grad.add_color_stop_rgba(1, 0, 0, 0, 0)
        
        ctx.set_source(grad)
        ctx.rectangle(lx, -100, w_ray, h_ray)
        ctx.fill()
    ctx.restore()

    # 5. Vignette (Dramatic Edges)
    pat_vig = cairo.RadialGradient(width/2, height/2, width*0.3, width/2, height/2, width*0.8)
    pat_vig.add_color_stop_rgba(0, 0, 0, 0, 0.0)
    pat_vig.add_color_stop_rgba(1, 0.05, 0.02, 0.02, 0.85) # Very dark brown/black edges
    ctx.set_source(pat_vig)
    ctx.paint()

    # 6. Floating Particles (Magic Dust)
    for _ in range(40):
        px = random.randint(0, int(width))
        py = random.randint(0, int(height))
        ctx.set_source_rgba(1.0, 0.9, 0.6, random.uniform(0.3, 0.7))
        ctx.arc(px, py, random.uniform(0.5, 2), 0, 2*math.pi)
        ctx.fill()

    surface.flush()
    return cairo_surface_to_pygame(surface)

# ==============================================================================
# 3. BIN / WADAH (DIUBAH MENJADI LEATHER POUCH/KANTONG KULIT)
# ==============================================================================
def render_bins_cairo(width, height, bin_rects, bin_labels):
    """
    Menggambar Bin sebagai Kantong Kulit (Leather Pouch) Coklat
    dengan tekstur, tali pengikat, dan jahitan kasar.
    """
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # Warna Kulit
    LEATHER_DARK = (0.28, 0.15, 0.08)    # Coklat gelap (Shadow)
    LEATHER_BASE = (0.45, 0.25, 0.12)    # Coklat dasar
    LEATHER_HIGH = (0.60, 0.35, 0.20)    # Highlight
    ROPE_COLOR_1 = (0.75, 0.65, 0.50)    # Tali terang
    ROPE_COLOR_2 = (0.55, 0.45, 0.35)    # Tali gelap
    STITCH_COLOR = (0.85, 0.80, 0.70)    # Benang jahitan

    for rect, label in zip(bin_rects, bin_labels):
        x, y, w, h = rect
        
        # Pusat kantong
        cx = x + w / 2
        base_y = y + h - 10
        
        # --- 1. SHADOW BAWAH (Bayangan di tanah) ---
        ctx.save()
        ctx.scale(1, 0.3) # Pipihkan lingkaran jadi oval
        ctx.arc(cx, (base_y + 5) / 0.3, w * 0.45, 0, 2*math.pi)
        ctx.set_source_rgba(0, 0, 0, 0.5)
        ctx.fill()
        ctx.restore()

        # --- 2. BADAN KANTONG (Main Body) ---
        # Bentuk seperti labu: lebar di bawah, menyempit di leher, melebar di mulut
        neck_y = y + h * 0.25
        neck_w = w * 0.55
        body_w = w * 0.9
        
        ctx.new_path()
        # Mulai dari leher kiri
        ctx.move_to(cx - neck_w/2, neck_y)
        # Kurva ke bawah kiri (Badan gembung)
        ctx.curve_to(x - 10, y + h * 0.6,    # Control point 1
                     x + 10, base_y,         # Control point 2
                     cx, base_y)             # Tujuan (Tengah bawah)
        # Kurva ke atas kanan
        ctx.curve_to(x + w - 10, base_y, 
                     x + w + 10, y + h * 0.6, 
                     cx + neck_w/2, neck_y)
        
        # Tutup path sementara untuk fill badan
        ctx.close_path()

        # Gradient Radial untuk efek 3D (Cembung)
        grad = cairo.RadialGradient(cx - w*0.2, y + h*0.5, 10, cx, y + h*0.5, w*0.7)
        grad.add_color_stop_rgb(0, *LEATHER_HIGH) # Highlight agak ke kiri atas
        grad.add_color_stop_rgb(0.5, *LEATHER_BASE)
        grad.add_color_stop_rgb(1, *LEATHER_DARK)
        ctx.set_source(grad)
        ctx.fill_preserve()
        
        # Outline tipis
        ctx.set_source_rgba(0.2, 0.1, 0.05, 1)
        ctx.set_line_width(2)
        ctx.stroke()

        # --- 3. TEXTURE KULIT & GORESAN ---
        ctx.save()
        ctx.set_line_width(1)
        # Goresan acak untuk tekstur kulit tua
        for _ in range(15):
            sx = cx + random.uniform(-w*0.3, w*0.3)
            sy = y + h*0.4 + random.uniform(0, h*0.4)
            ctx.move_to(sx, sy)
            ctx.curve_to(sx + random.randint(-10, 10), sy + random.randint(-5, 5),
                         sx + random.randint(-10, 10), sy + random.randint(-5, 5),
                         sx + random.randint(-15, 15), sy + random.randint(-5, 5))
            ctx.set_source_rgba(0.2, 0.1, 0.05, 0.15) # Sangat transparan
            ctx.stroke()
        ctx.restore()

        # --- 4. JAHITAN (STITCHING) ---
        # Garis vertikal melengkung di sisi kanan
        stitch_path_x = cx + w * 0.25
        ctx.new_path()
        ctx.move_to(stitch_path_x, neck_y + 10)
        ctx.curve_to(stitch_path_x + 15, y + h*0.5, 
                     stitch_path_x + 5, y + h*0.8, 
                     stitch_path_x, y + h*0.85)
        
        # Gambar garis belahan kulit
        ctx.set_source_rgba(0.15, 0.08, 0.05, 0.6)
        ctx.set_line_width(2)
        ctx.stroke_preserve() # Simpan path untuk referensi posisi silang

        # Gambar benang silang (X) atau lurus
        # Kita pakai pendekatan manual sepanjang kurva imajiner
        num_stitches = 8
        for i in range(num_stitches):
            prog = i / num_stitches
            # Interpolasi kasar posisi y
            sy = (neck_y + 15) + prog * (h * 0.5)
            # Interpolasi kasar posisi x (mengikuti lengkung perut)
            sx = stitch_path_x + math.sin(prog * math.pi) * 10 
            
            ctx.move_to(sx - 4, sy - 3)
            ctx.line_to(sx + 4, sy + 3)
            ctx.move_to(sx - 4, sy + 3)
            ctx.line_to(sx + 4, sy - 3)
            
            ctx.set_source_rgba(*STITCH_COLOR, 0.9)
            ctx.set_line_width(1.5)
            ctx.stroke()

        # --- 5. BAGIAN ATAS (RUFFLES/MULUT TAS) ---
        # Bagian di atas tali pengikat
        ctx.new_path()
        ruffle_h = h * 0.15
        top_y = y + 5
        
        ctx.move_to(cx - neck_w/2 + 5, neck_y)
        
        # [FIX] Mengganti quadratic_curve_to dengan curve_to manual
        # Sisi kiri mekar ke atas
        # Quad control: (cx - neck_w/2 - 10, top_y + ruffle_h/2)
        # End point:    (cx - neck_w/2, top_y)
        x0, y0 = ctx.get_current_point()
        qx1, qy1 = cx - neck_w/2 - 10, top_y + ruffle_h/2
        qx2, qy2 = cx - neck_w/2, top_y
        ctx.curve_to(
            x0 + (2/3)*(qx1 - x0), y0 + (2/3)*(qy1 - y0),
            qx2 + (2/3)*(qx1 - qx2), qy2 + (2/3)*(qy1 - qy2),
            qx2, qy2
        )
        
        # Bagian atas bergelombang (Ruffles)
        ctx.curve_to(cx - neck_w/4, top_y + 10, cx + neck_w/4, top_y - 10, cx + neck_w/2, top_y)
        
        # [FIX] Mengganti quadratic_curve_to dengan curve_to manual
        # Sisi kanan kembali ke leher
        # Quad control: (cx + neck_w/2 + 10, top_y + ruffle_h/2)
        # End point:    (cx + neck_w/2 - 5, neck_y)
        x0, y0 = ctx.get_current_point()
        qx3, qy3 = cx + neck_w/2 + 10, top_y + ruffle_h/2
        qx4, qy4 = cx + neck_w/2 - 5, neck_y
        ctx.curve_to(
            x0 + (2/3)*(qx3 - x0), y0 + (2/3)*(qy3 - y0),
            qx4 + (2/3)*(qx3 - qx4), qy4 + (2/3)*(qy3 - qy4),
            qx4, qy4
        )
        
        # Bagian dalam mulut tas (Gelap)
        ctx.close_path()
        
        # Isi dengan warna kulit tapi lebih gelap (bagian dalam)
        grad_top = cairo.LinearGradient(cx, top_y, cx, neck_y)
        grad_top.add_color_stop_rgb(0, *LEATHER_DARK)
        grad_top.add_color_stop_rgb(1, *LEATHER_BASE)
        ctx.set_source(grad_top)
        ctx.fill()
        
        # Highlight pinggiran atas
        ctx.move_to(cx - neck_w/2, top_y)
        ctx.curve_to(cx - neck_w/4, top_y + 10, cx + neck_w/4, top_y - 10, cx + neck_w/2, top_y)
        ctx.set_source_rgba(0.7, 0.5, 0.4, 0.8)
        ctx.set_line_width(2)
        ctx.stroke()

        # --- 6. TALI PENGIKAT (ROPE) ---
        rope_thick = 8
        rope_segments = 12
        rope_w = neck_w - 5
        rope_start_x = cx - rope_w/2
        
        for i in range(rope_segments):
            # Menggambar segmen tali miring (twisted effect)
            seg_w = rope_w / rope_segments
            sx = rope_start_x + i * seg_w
            sy = neck_y - rope_thick/2
            
            ctx.save()
            # Clip ke area leher saja agar rapi
            ctx.rectangle(sx, sy - 5, seg_w + 2, rope_thick + 10)
            ctx.clip()
            
            # Gambar oval miring
            ctx.translate(sx + seg_w/2, sy + rope_thick/2)
            ctx.rotate(math.radians(-20))
            ctx.scale(0.8, 1.0)
            ctx.arc(0, 0, rope_thick, 0, 2*math.pi)
            
            # Warna selang seling untuk tekstur tali
            if i % 2 == 0:
                ctx.set_source_rgb(*ROPE_COLOR_1)
            else:
                ctx.set_source_rgb(*ROPE_COLOR_2)
            ctx.fill()
            
            # Outline tali
            ctx.set_source_rgba(0.3, 0.2, 0.1, 0.8)
            ctx.set_line_width(1)
            ctx.stroke()
            ctx.restore()

        # --- 7. LABEL ---
        # Label sekarang seolah diukir atau dicat di atas kulit
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        font_size = min(w, h) * 0.25
        ctx.set_font_size(font_size)
        
        (xb, yb, wb, hb, xb_adv, yb_adv) = ctx.text_extents(label)
        text_x = cx - wb / 2 - xb
        text_y = base_y - h*0.35 # Posisi di perut tas
        
        # Efek "Burned" / Terbakar (Hitam transparan di bawah)
        ctx.set_source_rgba(0.2, 0.1, 0.05, 0.6)
        ctx.move_to(text_x + 1, text_y + 2)
        ctx.show_text(label)
        
        # Teks Utama (Warna krem pudar seperti cat lama)
        ctx.set_source_rgba(0.9, 0.85, 0.7, 0.9)
        ctx.move_to(text_x, text_y)
        ctx.show_text(label)

    return cairo_surface_to_pygame(surface)

# ==============================================================================
# 4. FALLING BLOCK / COIN (Sama seperti sebelumnya)
# ==============================================================================
def render_falling_block(value):
    w, h = 70, 70
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    # Bersihkan background
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    cx, cy = w / 2, h / 2
    radius = (w / 2) - 5 

    # Layer 1: Dasar Emas
    pattern = cairo.RadialGradient(cx, cy, radius * 0.1, cx, cy, radius)
    pattern.add_color_stop_rgb(0, 1.0, 0.95, 0.6)
    pattern.add_color_stop_rgb(0.7, 1.0, 0.8, 0.2)
    pattern.add_color_stop_rgb(1, 0.8, 0.6, 0.1)
    
    ctx.set_source(pattern)
    ctx.arc(cx, cy, radius, 0, 2 * math.pi)
    ctx.fill()

    # Layer 2: Rims
    ctx.set_line_width(4)
    ctx.set_source_rgb(0.9, 0.7, 0.1)
    ctx.arc(cx, cy, radius - 2, 0, 2 * math.pi)
    ctx.stroke()

    ctx.set_line_width(2)
    ctx.set_source_rgb(0.7, 0.5, 0.0)
    inner_radius = radius * 0.75
    ctx.arc(cx, cy, inner_radius, 0, 2 * math.pi)
    ctx.stroke()
    
    # Layer 3: Sheen
    sheen = cairo.LinearGradient(0, 0, w, h)
    sheen.add_color_stop_rgba(0.3, 1, 1, 1, 0.0) 
    sheen.add_color_stop_rgba(0.5, 1, 1, 1, 0.4)
    sheen.add_color_stop_rgba(0.7, 1, 1, 1, 0.0)

    ctx.set_source(sheen)
    ctx.arc(cx, cy, radius, 0, 2 * math.pi)
    ctx.fill()

    # Layer 4: Text
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    font_size = 32
    ctx.set_font_size(font_size)
    
    te = ctx.text_extents(str(value))
    text_x = cx - (te.width / 2 + te.x_bearing)
    text_y = cy - (te.height / 2 + te.y_bearing)

    ctx.set_source_rgba(0.4, 0.3, 0.0, 0.6)
    ctx.move_to(text_x + 2, text_y + 2)
    ctx.show_text(str(value))

    ctx.set_source_rgb(1.0, 1.0, 0.9) 
    ctx.move_to(text_x, text_y)
    ctx.text_path(str(value))
    ctx.fill_preserve()
    
    ctx.set_source_rgba(0.6, 0.4, 0.0, 0.8)
    ctx.set_line_width(1.0)
    ctx.stroke()

    return cairo_surface_to_pygame(surf)