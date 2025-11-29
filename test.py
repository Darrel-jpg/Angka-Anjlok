import cairo
import math

def hex_to_rgb(hex_color):
    """Mengubah warna hex string (#RRGGBB) menjadi tuple (r, g, b) cairo."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

def draw_chamfered_rect(ctx, x, y, width, height, chamfer_size):
    """
    Membuat path berbentuk persegi panjang dengan sudut terpotong (chamfered).
    Bentuk ini khas untuk gaya UI game 'batu' atau kartun.
    """
    ctx.new_path()
    # Kiri atas
    ctx.move_to(x + chamfer_size, y)
    # Kanan atas
    ctx.line_to(x + width - chamfer_size, y)
    ctx.line_to(x + width, y + chamfer_size)
    # Kanan bawah
    ctx.line_to(x + width, y + height - chamfer_size)
    ctx.line_to(x + width - chamfer_size, y + height)
    # Kiri bawah
    ctx.line_to(x + chamfer_size, y + height)
    ctx.line_to(x, y + height - chamfer_size)
    # Kembali ke kiri atas
    ctx.line_to(x, y + chamfer_size)
    ctx.close_path()

def draw_stone_slab(ctx, x, y, width, height):
    """
    Fungsi untuk menggambar background batu besar.
    """
    # Warna Batu
    color_light = hex_to_rgb("#cfc6b8") # Warna permukaan
    color_shadow = hex_to_rgb("#8f857d") # Warna bayangan/ketebalan

    # 1. Gambar Bagian Bayangan/Ketebalan (Lapisan bawah)
    # Kita geser sedikit ke bawah untuk efek 3D
    offset_depth = 15
    draw_chamfered_rect(ctx, x, y + offset_depth, width, height, 30)
    ctx.set_source_rgb(*color_shadow)
    ctx.fill()

    # 2. Gambar Permukaan Utama (Lapisan atas)
    draw_chamfered_rect(ctx, x, y, width, height, 30)
    ctx.set_source_rgb(*color_light)
    ctx.fill()
    
    # 3. Tambahkan sedikit detail retakan (Opsional - Dekorasi sederhana)
    ctx.set_source_rgb(*color_shadow)
    ctx.set_line_width(3)
    
    # Retakan kiri atas
    ctx.move_to(x + 20, y + 40)
    ctx.line_to(x + 50, y + 60)
    ctx.line_to(x + 40, y + 90)
    ctx.stroke()
    
    # Retakan kanan bawah
    ctx.move_to(x + width - 20, y + height - 40)
    ctx.line_to(x + width - 50, y + height - 60)
    ctx.stroke()

def draw_game_button(ctx, text, x, y, width, height, base_color_hex):
    """
    Fungsi reusable untuk membuat tombol game 3D.
    Args:
        ctx: Context pycairo
        text: Tulisan pada tombol (misal: EASY)
        x, y: Posisi tombol
        width, height: Ukuran tombol
        base_color_hex: Warna utama tombol (hex code)
    """
    r, g, b = hex_to_rgb(base_color_hex)
    
    # Membuat warna bayangan (lebih gelap dari warna dasar)
    # Kembali ke faktor 0.7 seperti semula, karena yang ingin digelapkan adalah background layar
    shadow_factor = 0.7 
    shadow_r, shadow_g, shadow_b = r * shadow_factor, g * shadow_factor, b * shadow_factor
    
    chamfer = 15 # Besaran potongan sudut
    depth = 8    # Ketebalan efek 3D tombol (kembali ke 8)

    # 1. Gambar Ketebalan Tombol (Bagian Bawah/Gelap)
    draw_chamfered_rect(ctx, x, y + depth, width, height, chamfer)
    ctx.set_source_rgb(shadow_r, shadow_g, shadow_b)
    ctx.fill()

    # 2. Gambar Wajah Tombol (Bagian Atas/Terang)
    draw_chamfered_rect(ctx, x, y, width, height, chamfer)
    ctx.set_source_rgb(r, g, b)
    ctx.fill()

    # 3. Highlight/Shine di bagian atas (Opsional, agar lebih 'pop')
    ctx.save()
    draw_chamfered_rect(ctx, x + 5, y + 5, width - 10, height/2 - 5, chamfer)
    ctx.clip()
    # Gradient putih transparan
    pat = cairo.LinearGradient(x, y, x, y + height/2)
    pat.add_color_stop_rgba(0, 1, 1, 1, 0.3)
    pat.add_color_stop_rgba(1, 1, 1, 1, 0.0)
    ctx.set_source(pat)
    ctx.rectangle(x, y, width, height) # Fill area clip
    ctx.fill()
    ctx.restore()

    # 4. Dekorasi "Lubang/Kawah" kecil di sudut (seperti di gambar contoh)
    def draw_crater(cx, cy):
        ctx.arc(cx, cy, 3, 0, 2 * math.pi)
        ctx.set_source_rgb(shadow_r, shadow_g, shadow_b)
        ctx.fill()
    
    draw_crater(x + 15, y + height - 15)
    draw_crater(x + width - 15, y + 15)

    # 5. Render Teks
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(28)
    
    # Hitung posisi teks agar di tengah (centering)
    (x_bearing, y_bearing, text_width, text_height, x_advance, y_advance) = ctx.text_extents(text)
    text_x = x + (width / 2) - (text_width / 2) - x_bearing
    text_y = y + (height / 2) - (text_height / 2) - y_bearing
    
    # Warna teks putih dengan outline/shadow tipis
    ctx.move_to(text_x + 1, text_y + 2) # Shadow teks
    ctx.set_source_rgb(shadow_r, shadow_g, shadow_b)
    ctx.show_text(text)
    
    ctx.move_to(text_x, text_y) # Teks Utama
    ctx.set_source_rgb(1, 1, 1)
    ctx.show_text(text)

def main():
    # Setup Canvas
    WIDTH, HEIGHT = 500, 700
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # 1. Background Layar (Ungu Gelap seperti contoh)
    # Ubah warna hex ini menjadi lebih gelap
    ctx.set_source_rgb(*hex_to_rgb("#301a3d")) # Lebih gelap dari #4a2c5a
    ctx.paint()
    
    # Efek Kayu Background (Garis-garis tipis)
    ctx.set_source_rgba(0, 0, 0, 0.15) # Sedikit lebih gelap agar terlihat di background yang lebih gelap
    ctx.set_line_width(40)
    for i in range(0, HEIGHT, 60):
        ctx.move_to(0, i)
        ctx.line_to(WIDTH, i)
        ctx.stroke()

    # --- PENGGUNAAN FUNGSI REUSABLE ---

    # 2. Gambar Papan Batu (Container)
    slab_width = 350
    slab_height = 400
    slab_x = (WIDTH - slab_width) / 2
    slab_y = 150
    
    draw_stone_slab(ctx, slab_x, slab_y, slab_width, slab_height)

    # Judul (Sekedar pelengkap)
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(40)
    ctx.set_source_rgb(1, 1, 1)
    title = "STONE MENU"
    (xb, yb, tw, th, xa, ya) = ctx.text_extents(title)
    ctx.move_to((WIDTH - tw)/2, slab_y + 60)
    ctx.show_text(title)

    # 3. Gambar Tombol-tombol
    button_width = 220
    button_height = 60
    button_x = (WIDTH - button_width) / 2
    start_y = slab_y + 100
    gap = 80 # Jarak antar tombol

    # Tombol EASY (Kuning/Oranye)
    draw_game_button(ctx, "EASY", button_x, start_y, button_width, button_height, "#ffcc00")

    # Tombol MEDIUM (Hijau Muda)
    draw_game_button(ctx, "MEDIUM", button_x, start_y + gap, button_width, button_height, "#8bc34a")

    # Tombol HARD (Hijau Lebih Tua)
    draw_game_button(ctx, "HARD", button_x, start_y + (gap * 2), button_width, button_height, "#689f38")

    # Output
    output_filename = "stone_menu_darker_screen_bg.png"
    surface.write_to_png(output_filename)
    print(f"Gambar berhasil dibuat: {output_filename}")

if __name__ == "__main__":
    main()