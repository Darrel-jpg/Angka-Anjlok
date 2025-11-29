import math
import cairo
import pygame
import random

# ==============================================================================
# UTILITY
# ==============================================================================
def cairo_surface_to_pygame(surf: cairo.ImageSurface) -> pygame.Surface:
    buf = surf.get_data()
    return pygame.image.frombuffer(
        buf, 
        (surf.get_width(), surf.get_height()), 
        'BGRA'
    ).convert_alpha()

def hex_to_rgb(hex_color):
    """Mengubah warna hex string (#RRGGBB) menjadi tuple (r, g, b) cairo 0.0-1.0."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

def draw_chamfered_rect(ctx, x, y, width, height, chamfer_size):
    """Membuat path persegi panjang dengan sudut terpotong."""
    ctx.new_path()
    ctx.move_to(x + chamfer_size, y)
    ctx.line_to(x + width - chamfer_size, y)
    ctx.line_to(x + width, y + chamfer_size)
    ctx.line_to(x + width, y + height - chamfer_size)
    ctx.line_to(x + width - chamfer_size, y + height)
    ctx.line_to(x + chamfer_size, y + height)
    ctx.line_to(x, y + height - chamfer_size)
    ctx.line_to(x, y + chamfer_size)
    ctx.close_path()

def draw_stone_texture(ctx, w, h, dark_mode=False):
    """
    Menggambar tekstur batu (Granit/Slate).
    """
    # 1. Warna Dasar Batu
    if dark_mode:
        ctx.set_source_rgb(0.15, 0.15, 0.18) # Batu gelap
    else:
        ctx.set_source_rgb(0.28, 0.28, 0.32) # Batu standar
    ctx.rectangle(0, 0, w, h)
    ctx.fill()
    
    # 2. Noise (Butiran batu)
    for _ in range(int(w * h * 0.005)):
        nx = random.randint(0, int(w))
        ny = random.randint(0, int(h))
        size = random.uniform(1, 2)
        if random.random() > 0.5:
            ctx.set_source_rgba(0, 0, 0, 0.3)
        else:
            ctx.set_source_rgba(1, 1, 1, 0.15)
        ctx.rectangle(nx, ny, size, size)
        ctx.fill()

    # 3. Retakan (Cracks)
    ctx.set_line_width(1)
    ctx.set_source_rgba(0.05, 0.05, 0.08, 0.4)
    for _ in range(int((w+h)/100) + 1):
        cx = random.randint(0, int(w))
        cy = random.randint(0, int(h))
        ctx.move_to(cx, cy)
        for _ in range(random.randint(3, 6)):
            cx += random.randint(-15, 15)
            cy += random.randint(-15, 15)
            ctx.line_to(cx, cy)
        ctx.stroke()
        
    # 4. Sedikit Lumut (Moss)
    for _ in range(3):
        mx = random.randint(0, int(w))
        my = random.randint(0, int(h))
        ctx.set_source_rgba(0.2, 0.3, 0.15, 0.15)
        ctx.arc(mx, my, random.randint(10, 30), 0, 2*math.pi)
        ctx.fill()

# ==============================================================================
# UI: HUD PANEL & ICONS
# ==============================================================================
def render_hud_panel(width, height):
    """Panel batu pecah/kasar untuk background skor"""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)
    
    ctx.new_path()
    roughness = 2
    ctx.move_to(0, roughness)
    ctx.line_to(width, 0)
    ctx.line_to(width - roughness, height)
    ctx.line_to(roughness, height - roughness)
    ctx.close_path()
    
    ctx.save()
    ctx.clip_preserve()
    draw_stone_texture(ctx, width, height, dark_mode=True)
    ctx.restore()
    
    ctx.set_source_rgba(0.6, 0.6, 0.65, 0.8)
    ctx.set_line_width(2)
    ctx.stroke()
    
    return cairo_surface_to_pygame(surf)

def render_heart_icon(size):
    """Icon hati (Kristal Merah/Ruby)"""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surf)
    
    cx, cy = size/2, size/2 + size*0.1
    r = size * 0.45
    
    ctx.move_to(cx, cy + r * 0.8)
    ctx.curve_to(cx - r, cy, cx - r, cy - r, cx, cy - r * 0.5)
    ctx.curve_to(cx + r, cy - r, cx + r, cy, cx, cy + r * 0.8)
    ctx.close_path()
    
    pat = cairo.LinearGradient(cx - r, cy - r, cx + r, cy + r)
    pat.add_color_stop_rgb(0, 1.0, 0.6, 0.6)
    pat.add_color_stop_rgb(0.5, 0.8, 0.0, 0.1) 
    pat.add_color_stop_rgb(1, 0.3, 0.0, 0.0)
    ctx.set_source(pat)
    ctx.fill_preserve()
    
    ctx.set_source_rgba(0.9, 0.8, 0.8, 0.5)
    ctx.set_line_width(1)
    ctx.stroke()
    
    return cairo_surface_to_pygame(surf)

def render_pause_button_asset(size, hover=False):
    """Tombol Pause kecil berbentuk batu bulat kuno"""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surf)
    
    cx, cy = size/2, size/2
    r = size/2 - 2
    
    # Lingkaran Batu
    ctx.arc(cx, cy, r, 0, 2*math.pi)
    ctx.save()
    ctx.clip()
    draw_stone_texture(ctx, size, size, dark_mode=not hover)
    
    # Efek bulat
    grad = cairo.RadialGradient(cx - r*0.3, cy - r*0.3, r*0.1, cx, cy, r)
    grad.add_color_stop_rgba(0, 1, 1, 1, 0.1)
    grad.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    ctx.set_source(grad)
    ctx.paint()
    ctx.restore()
    
    # Cincin Besi
    ctx.new_path()
    ctx.arc(cx, cy, r, 0, 2*math.pi)
    ctx.set_line_width(3)
    if hover:
        ctx.set_source_rgb(0.7, 0.7, 0.8)
    else:
        ctx.set_source_rgb(0.4, 0.35, 0.3)
    ctx.stroke()
    
    # Simbol Pause
    bar_w = size * 0.12
    bar_h = size * 0.35
    
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.rectangle(cx - bar_w*1.8, cy - bar_h/2, bar_w, bar_h)
    ctx.rectangle(cx + bar_w*0.8, cy - bar_h/2, bar_w, bar_h)
    ctx.fill()
    
    ctx.set_source_rgba(1, 1, 1, 0.3)
    ctx.set_line_width(1)
    ctx.rectangle(cx - bar_w*1.8, cy - bar_h/2, bar_w, bar_h)
    ctx.stroke()
    ctx.rectangle(cx + bar_w*0.8, cy - bar_h/2, bar_w, bar_h)
    ctx.stroke()
    
    return cairo_surface_to_pygame(surf)

# ==============================================================================
# UI: MENU ASSETS (STONE SLAB & BUTTONS)
# ==============================================================================
def render_pause_slab(width, height, title_text="PAUSED"):
    """
    Menggambar papan batu background untuk menu (Container).
    """
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    ctx = cairo.Context(surf)
    
    m = 0 
    
    # Warna Batu (Beige Stone)
    color_light = hex_to_rgb("#beaa9d") 
    color_shadow = hex_to_rgb("#847666") 

    # 1. Gambar Bagian Bayangan (Depth)
    offset_depth = 15
    draw_chamfered_rect(ctx, m, m + offset_depth, width, height - offset_depth, 30)
    ctx.set_source_rgb(*color_shadow)
    ctx.fill()

    # 2. Gambar Permukaan Utama
    draw_chamfered_rect(ctx, m, m, width, height - offset_depth, 30)
    ctx.set_source_rgb(*color_light)
    ctx.fill()
    
    # 3. Detail Retakan
    ctx.set_source_rgb(*color_shadow)
    ctx.set_line_width(3)
    
    ctx.move_to(m + 20, m + 40)
    ctx.line_to(m + 50, m + 60)
    ctx.line_to(m + 40, m + 90)
    ctx.stroke()
    
    ctx.move_to(width - 20, height - offset_depth - 40)
    ctx.line_to(width - 50, height - offset_depth - 60)
    ctx.stroke()

    # 4. Judul Menu
    if title_text:
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(40)
        
        (xb, yb, tw, th, xa, ya) = ctx.text_extents(title_text)
        text_x = (width - tw) / 2
        text_y = 70 
        
        ctx.move_to(text_x + 2, text_y + 2)
        ctx.set_source_rgba(0.4, 0.35, 0.3, 0.8)
        ctx.show_text(title_text)
        
        ctx.move_to(text_x, text_y)
        ctx.set_source_rgb(1, 1, 1)
        ctx.show_text(title_text)

    return cairo_surface_to_pygame(surf)

def render_colored_button(width, height, text, color_hex, hover=False):
    """
    Menggambar tombol 3D berwarna.
    """
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height + 10))
    ctx = cairo.Context(surf)
    
    r, g, b = hex_to_rgb(color_hex)
    
    if hover:
        r = min(1.0, r * 1.2)
        g = min(1.0, g * 1.2)
        b = min(1.0, b * 1.2)

    shadow_factor = 0.7 
    shadow_r, shadow_g, shadow_b = r * shadow_factor, g * shadow_factor, b * shadow_factor
    
    chamfer = 15
    depth = 8
    
    x, y = 0, 0
    
    # 1. Gambar Ketebalan
    draw_chamfered_rect(ctx, x, y + depth, width, height, chamfer)
    ctx.set_source_rgb(shadow_r, shadow_g, shadow_b)
    ctx.fill()

    # 2. Gambar Wajah
    if hover:
        y += 2
        depth -= 2
        
    draw_chamfered_rect(ctx, x, y, width, height, chamfer)
    ctx.set_source_rgb(r, g, b)
    ctx.fill()

    # 3. Highlight Glossy
    ctx.save()
    draw_chamfered_rect(ctx, x + 5, y + 5, width - 10, height/2 - 5, chamfer)
    ctx.clip()
    pat = cairo.LinearGradient(x, y, x, y + height/2)
    pat.add_color_stop_rgba(0, 1, 1, 1, 0.3)
    pat.add_color_stop_rgba(1, 1, 1, 1, 0.0)
    ctx.set_source(pat)
    ctx.rectangle(x, y, width, height)
    ctx.fill()
    ctx.restore()

    # 4. Dekorasi Lubang Baut
    def draw_crater(cx, cy):
        ctx.arc(cx, cy, 3, 0, 2 * math.pi)
        ctx.set_source_rgb(shadow_r, shadow_g, shadow_b)
        ctx.fill()
    
    draw_crater(x + 15, y + height - 15)
    draw_crater(x + width - 15, y + 15)

    # 5. Teks
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(24) 
    (xb, yb, tw, th, xa, ya) = ctx.text_extents(text)
    
    text_x = x + (width - tw) / 2 - xb
    text_y = y + (height / 2) + (th / 2) 
    
    ctx.move_to(text_x + 1, text_y + 2)
    ctx.set_source_rgb(shadow_r, shadow_g, shadow_b)
    ctx.show_text(text)
    
    ctx.move_to(text_x, text_y)
    ctx.set_source_rgb(1, 1, 1)
    ctx.show_text(text)

    return cairo_surface_to_pygame(surf)

# ==============================================================================
# ENVIRONMENT & GAME OBJECTS
# ==============================================================================
def create_cairo_background(width, height):
    """Background Tanah dengan efek cahaya (God Rays)"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    ctx = cairo.Context(surface)

    GROUND_DARK = (0.15, 0.12, 0.10)
    GROUND_MID = (0.25, 0.20, 0.15)
    MOSS_DARK = (0.20, 0.35, 0.15)
    MOSS_LIGHT = (0.35, 0.50, 0.25)
    LIGHT_RAY = (1.0, 0.95, 0.8, 0.08)

    # Base
    ctx.set_source_rgb(*GROUND_DARK)
    ctx.paint()

    # Texture
    for _ in range(150):
        x = random.randint(0, int(width))
        y = random.randint(0, int(height))
        rad = random.randint(20, 100)
        ctx.set_source_rgba(*GROUND_MID, 0.3)
        ctx.arc(x, y, rad, 0, 2*math.pi)
        ctx.fill()

    # Moss
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
            if random.random() > 0.7:
                ctx.set_source_rgba(*MOSS_LIGHT, 0.5)
                ctx.arc(ox+1, oy-1, size*0.6, 0, 2*math.pi)
                ctx.fill()
        ctx.restore()

    for _ in range(30):
        draw_moss_clump(random.randint(0, int(width)), random.randint(0, int(height)), 40)

    # God Rays
    ctx.save()
    ctx.rotate(math.radians(-15))
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

    # Vignette
    pat_vig = cairo.RadialGradient(width/2, height/2, width*0.3, width/2, height/2, width*0.8)
    pat_vig.add_color_stop_rgba(0, 0, 0, 0, 0.0)
    pat_vig.add_color_stop_rgba(1, 0.05, 0.02, 0.02, 0.85)
    ctx.set_source(pat_vig)
    ctx.paint()

    # Particles
    for _ in range(40):
        px = random.randint(0, int(width))
        py = random.randint(0, int(height))
        ctx.set_source_rgba(1.0, 0.9, 0.6, random.uniform(0.3, 0.7))
        ctx.arc(px, py, random.uniform(0.5, 2), 0, 2*math.pi)
        ctx.fill()

    surface.flush()
    return cairo_surface_to_pygame(surface)

def render_bins_cairo(width, height, bin_rects, bin_labels):
    """Menggambar Bin sebagai Kantong Kulit"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    LEATHER_DARK = (0.28, 0.15, 0.08)
    LEATHER_BASE = (0.45, 0.25, 0.12)
    LEATHER_HIGH = (0.60, 0.35, 0.20)
    ROPE_COLOR_1 = (0.75, 0.65, 0.50)
    ROPE_COLOR_2 = (0.55, 0.45, 0.35)
    STITCH_COLOR = (0.85, 0.80, 0.70)

    for rect, label in zip(bin_rects, bin_labels):
        x, y, w, h = rect
        cx = x + w / 2
        base_y = y + h - 10
        
        # Shadow
        ctx.save()
        ctx.scale(1, 0.3)
        ctx.arc(cx, (base_y + 5) / 0.3, w * 0.45, 0, 2*math.pi)
        ctx.set_source_rgba(0, 0, 0, 0.5)
        ctx.fill()
        ctx.restore()

        # Body
        neck_y = y + h * 0.25
        neck_w = w * 0.55
        
        ctx.new_path()
        ctx.move_to(cx - neck_w/2, neck_y)
        ctx.curve_to(x - 10, y + h * 0.6, x + 10, base_y, cx, base_y)
        ctx.curve_to(x + w - 10, base_y, x + w + 10, y + h * 0.6, cx + neck_w/2, neck_y)
        ctx.close_path()

        grad = cairo.RadialGradient(cx - w*0.2, y + h*0.5, 10, cx, y + h*0.5, w*0.7)
        grad.add_color_stop_rgb(0, *LEATHER_HIGH)
        grad.add_color_stop_rgb(0.5, *LEATHER_BASE)
        grad.add_color_stop_rgb(1, *LEATHER_DARK)
        ctx.set_source(grad)
        ctx.fill_preserve()
        
        ctx.set_source_rgba(0.2, 0.1, 0.05, 1)
        ctx.set_line_width(2)
        ctx.stroke()

        # Stitching
        stitch_path_x = cx + w * 0.25
        num_stitches = 8
        for i in range(num_stitches):
            prog = i / num_stitches
            sy = (neck_y + 15) + prog * (h * 0.5)
            sx = stitch_path_x + math.sin(prog * math.pi) * 10 
            ctx.move_to(sx - 4, sy - 3)
            ctx.line_to(sx + 4, sy + 3)
            ctx.move_to(sx - 4, sy + 3)
            ctx.line_to(sx + 4, sy - 3)
            ctx.set_source_rgba(*STITCH_COLOR, 0.9)
            ctx.set_line_width(1.5)
            ctx.stroke()

        # Ruffles
        ctx.new_path()
        ruffle_h = h * 0.15
        top_y = y + 5
        ctx.move_to(cx - neck_w/2 + 5, neck_y)
        
        # Manual curves to avoid quadratic method
        x0, y0 = ctx.get_current_point()
        qx1, qy1 = cx - neck_w/2 - 10, top_y + ruffle_h/2
        qx2, qy2 = cx - neck_w/2, top_y
        ctx.curve_to(x0 + (2/3)*(qx1 - x0), y0 + (2/3)*(qy1 - y0), qx2 + (2/3)*(qx1 - qx2), qy2 + (2/3)*(qy1 - qy2), qx2, qy2)
        
        ctx.curve_to(cx - neck_w/4, top_y + 10, cx + neck_w/4, top_y - 10, cx + neck_w/2, top_y)
        
        x0, y0 = ctx.get_current_point()
        qx3, qy3 = cx + neck_w/2 + 10, top_y + ruffle_h/2
        qx4, qy4 = cx + neck_w/2 - 5, neck_y
        ctx.curve_to(x0 + (2/3)*(qx3 - x0), y0 + (2/3)*(qy3 - y0), qx4 + (2/3)*(qx3 - qx4), qy4 + (2/3)*(qy3 - qy4), qx4, qy4)
        
        ctx.close_path()
        
        grad_top = cairo.LinearGradient(cx, top_y, cx, neck_y)
        grad_top.add_color_stop_rgb(0, *LEATHER_DARK)
        grad_top.add_color_stop_rgb(1, *LEATHER_BASE)
        ctx.set_source(grad_top)
        ctx.fill()

        # Rope
        rope_thick = 8
        rope_segments = 12
        rope_w = neck_w - 5
        rope_start_x = cx - rope_w/2
        for i in range(rope_segments):
            seg_w = rope_w / rope_segments
            sx = rope_start_x + i * seg_w
            sy = neck_y - rope_thick/2
            ctx.save()
            ctx.rectangle(sx, sy - 5, seg_w + 2, rope_thick + 10)
            ctx.clip()
            ctx.translate(sx + seg_w/2, sy + rope_thick/2)
            ctx.rotate(math.radians(-20))
            ctx.scale(0.8, 1.0)
            ctx.arc(0, 0, rope_thick, 0, 2*math.pi)
            if i % 2 == 0: ctx.set_source_rgb(*ROPE_COLOR_1)
            else: ctx.set_source_rgb(*ROPE_COLOR_2)
            ctx.fill()
            ctx.set_source_rgba(0.3, 0.2, 0.1, 0.8)
            ctx.set_line_width(1)
            ctx.stroke()
            ctx.restore()

        # Label
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(min(w, h) * 0.25)
        (xb, yb, wb, hb, xb_adv, yb_adv) = ctx.text_extents(label)
        text_x = cx - wb / 2 - xb
        text_y = base_y - h*0.35
        ctx.set_source_rgba(0.2, 0.1, 0.05, 0.6)
        ctx.move_to(text_x + 1, text_y + 2)
        ctx.show_text(label)
        ctx.set_source_rgba(0.9, 0.85, 0.7, 0.9)
        ctx.move_to(text_x, text_y)
        ctx.show_text(label)

    return cairo_surface_to_pygame(surface)

def render_falling_block(value):
    w, h = 70, 70
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    # Layer 1: Dasar Emas
    cx, cy = w / 2, h / 2
    radius = (w / 2) - 5 
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
    ctx.set_font_size(32)
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