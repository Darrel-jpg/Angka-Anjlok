import math
import cairo
import pygame
import random

# Konversi cairo -> pygame
def cairo_surface_to_pygame(surf: cairo.ImageSurface) -> pygame.Surface:
    buf = surf.get_data()
    py_surf = pygame.image.frombuffer(buf, (surf.get_width(), surf.get_height()), 'ARGB')
    return py_surf.convert_alpha()

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

        # Highlight gloss effect
        gloss_grad = cairo.LinearGradient(x, y, x, y + h * 0.5)
        gloss_grad.add_color_stop_rgba(0, 1, 1, 1, 0.5)
        gloss_grad.add_color_stop_rgba(1, 1, 1, 1, 0)
        
        ctx.set_source(gloss_grad)
        rounded_rectangle(ctx, x + 5, y + 5, w - 10, h * 0.4, h * 0.15)
        ctx.fill()

        # Icon dekoratif di pojok
        icon_size = h * 0.15
        ctx.set_source_rgba(1, 1, 1, 0.3)
        ctx.arc(x + w - icon_size * 2, y + icon_size * 1.5, icon_size, 0, 2 * math.pi)
        ctx.fill()

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

    # Highlight effect
    highlight_grad = cairo.RadialGradient(cx - 10, cy - 10, 2, cx - 10, cy - 10, 15)
    highlight_grad.add_color_stop_rgba(0, 1, 1, 1, 0.6)
    highlight_grad.add_color_stop_rgba(1, 1, 1, 1, 0)
    
    ctx.set_source(highlight_grad)
    ctx.arc(cx - 8, cy - 8, 12, 0, 2 * math.pi)
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