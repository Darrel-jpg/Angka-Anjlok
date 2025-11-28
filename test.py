import cairo
import math

def draw_coin_asset(number_text, size, filename):
    """
    Membuat gambar koin emas dengan angka di tengahnya.
    
    Args:
        number_text (str): Angka yang ingin ditampilkan (misal: "5", "10").
        size (int): Ukuran lebar dan tinggi gambar dalam piksel (misal: 128).
        filename (str): Nama file output (misal: "coin_5.png").
    """
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surface)

    # --- Koordinat Pusat dan Radius ---
    cx, cy = size / 2, size / 2
    radius = size / 2 - 5 # Memberi sedikit margin di tepi

    # --- LAPISAN 1: Dasar Koin (Gradien Radial Emas) ---
    # Ini membuat koin terlihat bulat dan metalik
    pattern = cairo.RadialGradient(cx, cy, radius * 0.1, cx, cy, radius)
    pattern.add_color_stop_rgb(0, 1.0, 0.95, 0.6) # Emas kuning terang di tengah
    pattern.add_color_stop_rgb(0.7, 1.0, 0.8, 0.2) # Emas oranye
    pattern.add_color_stop_rgb(1, 0.8, 0.6, 0.1)   # Emas gelap di pinggir
    
    ctx.set_source(pattern)
    ctx.arc(cx, cy, radius, 0, 2 * math.pi)
    ctx.fill()

    # --- LAPISAN 2: Cincin Pinggir (Outer Rim) ---
    # Memberi definisi pada tepi koin
    ctx.set_line_width(size * 0.05)
    ctx.set_source_rgb(0.9, 0.7, 0.1) # Warna emas solid untuk pinggiran
    ctx.arc(cx, cy, radius - (size * 0.025), 0, 2 * math.pi)
    ctx.stroke()

    # --- LAPISAN 3: Cincin Dalam (Inner Border) ---
    # Garis tipis yang memisahkan bagian luar dan dalam seperti di referensi
    ctx.set_line_width(size * 0.02)
    ctx.set_source_rgb(0.7, 0.5, 0.0) # Emas lebih gelap
    inner_radius = radius * 0.75
    ctx.arc(cx, cy, inner_radius, 0, 2 * math.pi)
    ctx.stroke()
    
    # --- LAPISAN 4: Efek Kilau Diagonal (Shiny Sheen) ---
    # Ini adalah kunci untuk membuatnya terlihat seperti gambar referensi.
    # Kita menggunakan gradien linear transparan diagonal.
    sheen = cairo.LinearGradient(0, 0, size, size)
    # Putih transparan -> Kuning sangat transparan -> Putih transparan
    sheen.add_color_stop_rgba(0.3, 1, 1, 1, 0.0) 
    sheen.add_color_stop_rgba(0.5, 1, 1, 0.8, 0.4) # Kilau utama di tengah
    sheen.add_color_stop_rgba(0.7, 1, 1, 1, 0.0)

    ctx.set_source(sheen)
    ctx.arc(cx, cy, radius, 0, 2 * math.pi)
    ctx.fill()

    # --- LAPISAN 5: Angka di Tengah ---
    # Menggambar angka agar terlihat menonjol
    
    # Pengaturan Font (Gunakan font yang tebal dan jelas)
    font_size = size * 0.5
    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(font_size)

    # Menghitung posisi agar teks benar-benar di tengah
    (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(number_text)
    text_x = cx - width / 2 - x_bearing
    text_y = cy + height / 2 - y_bearing # Perhatikan y-bearing seringkali negatif

    # 5a. Bayangan Teks (opsional, agar lebih kontras)
    ctx.set_source_rgba(0.6, 0.4, 0.0, 0.5) # Warna bayangan gelap transparan
    ctx.move_to(text_x + 2, text_y + 2)
    ctx.show_text(number_text)

    # 5b. Teks Utama
    ctx.set_source_rgb(1.0, 1.0, 0.8) # Warna teks kuning pucat/krem
    ctx.move_to(text_x, text_y)
    ctx.show_text(number_text)

    # --- Simpan Gambar ---
    surface.write_to_png(filename)
    print(f"Berhasil membuat: {filename}")

# ==========================================
# Contoh Penggunaan untuk Game Anda
# ==========================================

# Tentukan ukuran aset sprite yang Anda inginkan (misal 100x100 pixel)
SPRITE_SIZE = 100

# Hasilkan beberapa angka untuk contoh
draw_coin_asset("5", SPRITE_SIZE, "coin_5.png")
draw_coin_asset("10", SPRITE_SIZE, "coin_10.png")
draw_coin_asset("42", SPRITE_SIZE, "coin_42.png")
draw_coin_asset("?", SPRITE_SIZE, "coin_tanya.png") # Bisa juga simbol lain