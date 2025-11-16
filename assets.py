# ----------------------------
# game_assets.py
# ----------------------------
import math
import cairo
import pygame

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

    import random
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
def render_falling_block(value):
    w, h = 64, 52
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    # clean background
    ctx.set_source_rgba(0,0,0,0)
    ctx.paint()

    # -------------------------------------------------
    # WARNA SUPER CERAH (anak-anak style)
    # -------------------------------------------------
    import random
    bright_colors = [
        (1.00, 0.40, 0.55), # merah bubblegum
        (1.00, 0.62, 0.20), # oranye cerah
        (1.00, 0.85, 0.20), # kuning lembut cerah
        (0.38, 0.85, 0.28), # hijau slimer
        (0.20, 0.75, 1.00), # biru aqua cerah
        (0.55, 0.45, 1.00), # ungu neon lembut
        (1.00, 0.50, 0.90), # pink candy
        (0.25, 1.00, 0.80), # toska mint terang
    ]
    r, g, b = random.choice(bright_colors)

    # -------------------------------------------------
    # SOFT SHADOW (lebih smooth)
    # -------------------------------------------------
    ctx.set_source_rgba(0,0,0,0.22)
    ctx.arc(w/2 + 4, h/2 + 4, 24, 0, 2*math.pi)
    ctx.fill()

    # -------------------------------------------------
    # BUBBLE BODY (gradient neon pastel)
    # -------------------------------------------------
    grad = cairo.RadialGradient(
        w/2 - 8, h/2 - 8, 5,
        w/2, h/2, 30
    )

    # warna dalam lebih terang → efek glowing
    grad.add_color_stop_rgba(0, min(r+0.25,1), min(g+0.25,1), min(b+0.25,1), 1)
    grad.add_color_stop_rgba(0.6, r, g, b, 1)
    grad.add_color_stop_rgba(1, max(r-0.1,0), max(g-0.1,0), max(b-0.1,0), 1)

    ctx.set_source(grad)
    ctx.arc(w/2, h/2, 26, 0, 2*math.pi)
    ctx.fill()

    # -------------------------------------------------
    # BIG HIGHLIGHT (lebih imut & bubbly)
    # -------------------------------------------------
    ctx.set_source_rgba(1,1,1,0.45)
    ctx.arc(w/2 - 12, h/2 - 14, 10, 0, 2*math.pi)
    ctx.fill()

    ctx.set_source_rgba(1,1,1,0.18)
    ctx.arc(w/2 + 8, h/2 + 4, 6, 0, 2*math.pi)
    ctx.fill()

    # -------------------------------------------------
    # TEXT (lebih tebal dan kontras)
    # -------------------------------------------------
    ctx.set_source_rgb(0.1,0.1,0.1)
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(28)

    te = ctx.text_extents(str(value))
    ctx.move_to((w - te.x_advance)/2, (h + te.height)/2 - 3)
    ctx.show_text(str(value))

    return cairo_surface_to_pygame(surf)


