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

# render tempat jawaban (bin)
def render_bins_cairo(width, height, bin_rects, bin_labels):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)
    ctx.set_source_rgba(0,0,0,0)
    ctx.paint()

    pastel_bins = [
        (0.75, 0.90, 1.0), # biru pastel
        (1.0, 0.85, 0.95), # pink pastel
        (0.85, 1.0, 0.85), # hijau pastel
        (1.0, 0.97, 0.80), # kuning pastel
    ]

    for rect, label in zip(bin_rects, bin_labels):
        x, y, w, h = rect
        r,g,b = random.choice(pastel_bins)

        # shadow awan
        ctx.set_source_rgba(0,0,0,0.25)
        ctx.arc(x + w/2 + 4, y + h/2 + 6, h/2, 0, 2*math.pi)
        ctx.fill()

        # tubuh awan (blob)
        grad = cairo.RadialGradient(x + w/2 - 8, y + h/2 - 8, 5, x + w/2, y + h/2, h/1.2)
        grad.add_color_stop_rgb(0, r+0.08, g+0.08, b+0.08)
        grad.add_color_stop_rgb(1, r, g, b)

        ctx.set_source(grad)
        ctx.arc(x + w/2, y + h/2, h/2, 0, 2*math.pi)
        ctx.fill()

        # highlight
        ctx.set_source_rgba(1,1,1,0.4)
        ctx.arc(x + w/2 - h/4, y + h/2 - h/4, h/5, 0, 2*math.pi)
        ctx.fill()

        # label
        ctx.set_source_rgb(0.2,0.2,0.2)
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(22)

        te = ctx.text_extents(label)
        ctx.move_to(x + (w - te.x_advance)/2, y + (h + te.height)/2 - 4)
        ctx.show_text(label)

    return cairo_surface_to_pygame(surf)



# render blok jatuh (angka)
# state global agar warna & bentuk tidak berulang 2x
LAST_SHAPE = None
LAST_COLOR = None


def render_falling_block(value):
    global LAST_SHAPE, LAST_COLOR

    w, h = 64, 64
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    ctx.set_source_rgba(0,0,0,0)
    ctx.paint()

    # -------------------------------------------------
    # WARNA CERAH
    # -------------------------------------------------
    bright_colors = [
        (1.00, 0.40, 0.55),
        (1.00, 0.62, 0.20),
        (1.00, 0.85, 0.20),
        (0.38, 0.85, 0.28),
        (0.20, 0.75, 1.00),
        (0.55, 0.45, 1.00),
        (1.00, 0.50, 0.90),
        (0.25, 1.00, 0.80),
    ]

    # pilih warna yang tidak sama dengan sebelumnya
    color_choices = [c for c in bright_colors if c != LAST_COLOR]
    r, g, b = random.choice(color_choices)
    LAST_COLOR = (r, g, b)

    # -------------------------------------------------
    # BENTUK
    # -------------------------------------------------
    shapes = [
        "circle",
        "rounded_square",
        "star",
        "diamond",
        "heart",
        "flower",
        "cloud",
        "triangle",
        "hexagon",
        "pill",
    ]

    shape_choices = [s for s in shapes if s != LAST_SHAPE]
    shape = random.choice(shape_choices)
    LAST_SHAPE = shape

    # -------------------------------------------------
    # SHADOW
    # -------------------------------------------------
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.arc(w/2 + 4, h/2 + 4, 26, 0, 2*math.pi)
    ctx.fill()

    # -------------------------------------------------
    # GRADIENT (body)
    # -------------------------------------------------
    grad = cairo.RadialGradient(w/2 - 8, h/2 - 8, 4, w/2, h/2, 30)
    grad.add_color_stop_rgba(0, min(r+0.25,1), min(g+0.25,1), min(b+0.25,1), 1)
    grad.add_color_stop_rgba(0.6, r, g, b, 1)
    grad.add_color_stop_rgba(1, max(r-0.12,0), max(g-0.12,0), max(b-0.12,0), 1)

    ctx.set_source(grad)

    # -------------------------------------------------
    # DRAW SHAPE
    # -------------------------------------------------
    if shape == "circle":
        ctx.arc(w/2, h/2, 26, 0, 2*math.pi)
        ctx.fill()

    elif shape == "rounded_square":
        radius = 14
        x, y, size = w/2 - 22, h/2 - 22, 44
        ctx.new_path()
        ctx.arc(x+size-radius, y+radius, radius, -90*math.pi/180, 0)
        ctx.arc(x+size-radius, y+size-radius, radius, 0, 90*math.pi/180)
        ctx.arc(x+radius, y+size-radius, radius, 90*math.pi/180, math.pi)
        ctx.arc(x+radius, y+radius, radius, math.pi, 3*math.pi/2)
        ctx.close_path()
        ctx.fill()

    elif shape == "diamond":
        ctx.new_path()
        ctx.move_to(w/2, h/2 - 26)
        ctx.line_to(w/2 + 26, h/2)
        ctx.line_to(w/2, h/2 + 26)
        ctx.line_to(w/2 - 26, h/2)
        ctx.close_path()
        ctx.fill()

    elif shape == "star":
        ctx.new_path()
        cx, cy, spikes, outer_r, inner_r = w/2, h/2, 5, 26, 12
        angle = -math.pi/2
        step = math.pi / spikes
        for i in range(spikes * 2):
            r_now = outer_r if i % 2 == 0 else inner_r
            sx = cx + math.cos(angle) * r_now
            sy = cy + math.sin(angle) * r_now
            if i == 0:
                ctx.move_to(sx, sy)
            else:
                ctx.line_to(sx, sy)
            angle += step
        ctx.close_path()
        ctx.fill()

    elif shape == "heart":
        ctx.new_path()
        ctx.move_to(w/2, h/2 + 10)
        ctx.curve_to(w/2 + 26, h/2 - 8, w/2 + 10, h/2 - 30, w/2, h/2 - 10)
        ctx.curve_to(w/2 - 10, h/2 - 30, w/2 - 26, h/2 - 8, w/2, h/2 + 10)
        ctx.close_path()
        ctx.fill()

    # ---------------- NEW SHAPES -------------------

    elif shape == "flower":
        cx, cy = w/2, h/2
        for i in range(6):
            angle = i * (math.pi/3)
            px = cx + math.cos(angle)*18
            py = cy + math.sin(angle)*18
            ctx.arc(px, py, 12, 0, 2*math.pi)
            ctx.fill()
        ctx.arc(cx, cy, 14, 0, 2*math.pi)
        ctx.fill()

    elif shape == "cloud":
        cx, cy = w/2, h/2
        ctx.new_path()
        ctx.arc(cx - 16, cy, 18, 0, 2*math.pi)
        ctx.arc(cx + 16, cy, 20, 0, 2*math.pi)
        ctx.arc(cx, cy - 10, 18, 0, 2*math.pi)
        ctx.fill()

    elif shape == "triangle":
        ctx.new_path()
        ctx.move_to(w/2, h/2 - 28)
        ctx.line_to(w/2 + 26, h/2 + 22)
        ctx.line_to(w/2 - 26, h/2 + 22)
        ctx.close_path()
        ctx.fill()

    elif shape == "hexagon":
        ctx.new_path()
        cx, cy, r = w/2, h/2, 26
        for i in range(6):
            angle = math.pi/3 * i + math.pi/6
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
        ctx.close_path()
        ctx.fill()

    elif shape == "pill":
        ctx.new_path()
        cx, cy = w/2, h/2
        ctx.rectangle(cx - 20, cy - 10, 40, 20)
        ctx.arc(cx - 20, cy, 10, math.pi/2, math.pi*3/2)
        ctx.arc(cx + 20, cy, 10, -math.pi/2, math.pi/2)
        ctx.fill()

    # -------------------------------------------------
    # HIGHLIGHT → hanya untuk LINGKARAN
    # -------------------------------------------------
    if shape == "circle":
        ctx.set_source_rgba(1,1,1,0.45)
        ctx.arc(w/2 - 10, h/2 - 14, 10, 0, 2*math.pi)
        ctx.fill()

    # -------------------------------------------------
    # TEXT
    # -------------------------------------------------
    ctx.set_source_rgb(0.1,0.1,0.1)
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(28)
    te = ctx.text_extents(str(value))
    ctx.move_to((w - te.x_advance)/2, (h + te.height)/2 - 3)
    ctx.show_text(str(value))

    return cairo_surface_to_pygame(surf)





