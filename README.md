<div align="center">
    <h1>ANGKA ANJLOK</h1>
    <p>
        <strong>Game Edukasi Perhitungan Matematika</strong>
    </p>
</div>

<hr>

<h2 id="-tentang">Tentang Game</h2>
<p>
    <strong>Angka Anjlok</strong> adalah permainan mengasah otak di mana pemain harus mencocokkan angka yang jatuh dengan soal matematika yang benar di kantong bawah. Game ini unik karena <strong>tidak menggunakan aset gambar eksternal (JPG/PNG)</strong>. Semua elemen visual (tekstur batu, tas kulit, koin emas, efek blur) dibuat secara <em>real-time</em> menggunakan kode Python dengan library <strong>PyCairo</strong>.
</p>

<h2 id="-fitur">Fitur Utama</h2>
<ul>
    <li>
        <strong>Grafik Prosedural (Code-Generated Art):</strong>
        <ul>
            <li>Tekstur batu granit/slate dengan detail retakan dan lumut.</li>
            <li>Kantong kulit (Leather Pouch) dengan efek jahitan dan dimensi.</li>
            <li>Tombol UI 3D dengan efek pencahayaan dinamis.</li>
        </ul>
    </li>
    <li>
        <strong>Mode Permainan Lengkap:</strong>
        <ul>
            <li>Penjumlahan (+), Pengurangan (-), Perkalian (x), Pembagian (:).</li>
            <li>Mode Campuran (Semua Operasi).</li>
        </ul>
    </li>
    <li>
        <strong>uD83C\uDFAE Tingkat Kesulitan:</strong>
        <ul>
            <li><strong>MUDAH:</strong> Soal 2 digit sederhana.</li>
            <li><strong>SEDANG:</strong> Kombinasi angka lebih variatif.</li>
            <li><strong>SULIT:</strong> Operasi matematika 3 angka (Misal: 3 + 5 x 2).</li>
        </ul>
    </li>
    <li>
        <strong>UI/UX Modern:</strong>
        <ul>
            <li>Menu Pause dengan background <em>blur</em> dan panel batu.</li>
            <li>HUD Skor dan Nyawa (Heart Icon) berbasis vektor.</li>
            <li>Efek suara dan visual tombol interaktif (Hover effects).</li>
        </ul>
    </li>
</ul>

<h2 id="-teknologi">Teknologi</h2>
<p>Game ini dibangun menggunakan:</p>
<ul>
    <li><strong>Python 3.x</strong> - Bahasa Pemrograman Utama.</li>
    <li><strong>Pygame</strong> - Engine game loop dan input handling.</li>
    <li><strong>PyCairo</strong> - Rendering grafik vektor 2D berkualitas tinggi.</li>
</ul>

<h2 id="-instalasi">Instalasi & Menjalankan</h2>
<p>Pastikan Python sudah terinstall di komputer Anda. Ikuti langkah berikut:</p>

<h3>1. Clone Repository</h3>
<pre><code>git clone https://github.com/username-anda/angka-anjlok.git
cd angka-anjlok</code></pre>

<h3>2. Install Library yang Dibutuhkan</h3>
<p>Anda perlu menginstall <code>pygame</code> dan <code>pycairo</code>:</p>
<pre><code>pip install pygame pycairo</code></pre>
<p><em>Catatan: Pengguna Windows mungkin perlu menginstall binary PyCairo khusus jika pip gagal mengcompile.</em></p>

<h3>3. Jalankan Game</h3>
<pre><code>python main.py</code></pre>

<h2 id="-cara-bermain">Cara Bermain</h2>
<table border="1" cellpadding="10">
    <thead>
        <tr>
            <th>Tombol</th>
            <th>Fungsi</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>⬅️ <strong>Panah Kiri</strong></td>
            <td>Gerakkan koin ke Kiri</td>
        </tr>
        <tr>
            <td>➡️ <strong>Panah Kanan</strong></td>
            <td>Gerakkan koin ke Kanan</td>
        </tr>
        <tr>
            <td>⬇️ <strong>Panah Bawah / Spasi</strong></td>
            <td>Jatuhkan koin lebih cepat (Drop)</td>
        </tr>
        <tr>
            <td><strong>ESC</strong> / <strong>Klik Ikon II</strong></td>
            <td>Pause Game</td>
        </tr>
    </tbody>
</table>

<h2 id="-struktur">📂 Struktur File</h2>
<ul>
    <li><code>main.py</code>: Logika utama game, loop, dan manajemen state (Menu/Game).</li>
    <li><code>assets.py</code>: Generator aset visual (Fungsi PyCairo untuk menggambar batu, tas, dll).</li>
</ul>

<hr>

<div align="center">
    <p>Dibuat dengan ❤️ dan ☕ menggunakan Python.</p>
</div>
