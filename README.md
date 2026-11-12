# Unfollow IG

Jika ada pertanyaan bisa hubungi saya via instagram @itsme.cuya
buy script? request script tertentu,kontak wa +628172300004

Script Python untuk meng-unfollow akun Instagram yang **tidak follback** secara otomatis, pelan-pelan, dengan satu perintah.

> **Syarat pemakaian:** script ini mewajibkan kamu follow **[@itsme.cuya](https://instagram.com/itsme.cuya)**. Saat dijalankan, script akan menanyakan apakah kamu mau follow akun tersebut. Kalau kamu menolak, script berhenti dan tidak ada akun yang di-unfollow.

## Fitur

- Mengambil daftar following dan followers **terbaru langsung dari Instagram**, tanpa perlu file ekspor data.
- Akun yang sudah nonaktif atau dihapus tidak ikut diproses, jadi tidak buang waktu.
- Jeda acak antar unfollow supaya lebih aman.
- Batas harian bisa diatur (default 60 unfollow per jalan).
- Mencatat progres. Kalau dijalankan lagi, lanjut dari sisa daftar.
- Whitelist: akun yang tidak ingin kamu unfollow bisa didaftarkan.

## Kebutuhan

- Windows, macOS, atau Linux
- [Python](https://www.python.org/downloads/) 3.10 atau lebih baru (di Windows, centang **Add python.exe to PATH** saat instalasi)
- [Git](https://git-scm.com/downloads)
- Akun Instagram aktif

## Cara pakai (Windows)

1. Buka **cmd**, lalu jalankan:

   ```
   git clone https://github.com/adminpapsky/unfollow-ig.git
   cd unfollow-ig
   pip install -r requirements.txt
   ```

2. (Opsional) Buka `unfollow_auto.py` dengan Notepad dan atur bagian atas file:
   - `PER_HARI`: jumlah unfollow per jalan. **Untuk percobaan pertama, ubah jadi 3.**
   - `WHITELIST`: username yang tidak boleh di-unfollow.

3. Jalankan:

   ```
   python unfollow_auto.py
   ```

4. Ikuti petunjuk di layar:
   - Ketik username Instagram kamu.
   - Ketik password. **Password tidak terlihat saat diketik**, itu normal, bukan error. Tekan Enter setelah selesai.
   - Kalau akunmu memakai 2FA, masukkan kode verifikasi.
   - Jawab `y` saat ditanya follow `@itsme.cuya`.

5. Biarkan jendela cmd terbuka sampai muncul tulisan **Selesai**. Jalankan lagi besok untuk melanjutkan sisa daftar.

## Memperbarui script

Di dalam folder `unfollow-ig`, jalankan:

```
git pull
```

## Privasi dan keamanan

- Username dan password hanya diketik di laptopmu dan hanya dikirim ke Instagram. Tidak dikirim ke server lain.
- Password tidak disimpan di file mana pun. Yang tersimpan hanya file sesi (`session.json`) dan catatan progres di laptopmu sendiri.
- Seluruh kode terbuka, jadi kamu bisa membacanya sebelum menjalankan.
- Jangan membagikan folder `unfollow-ig` ke orang lain setelah kamu memakainya, karena berisi `session.json` yang terhubung ke akunmu.

## Risiko (baca dulu)

Instagram tidak menyediakan API resmi untuk unfollow. Script ini memakai library tidak resmi ([instagrapi](https://github.com/subzeroid/instagrapi)) yang meniru aplikasi Instagram. Artinya:

- Ini bertentangan dengan ketentuan layanan Instagram.
- Ada risiko akun dibatasi sementara, diminta verifikasi, atau dalam kasus terburuk dibanned.
- Semakin banyak unfollow dalam waktu singkat, semakin tinggi risikonya.

Tips supaya lebih aman:

- Jangan naikkan `PER_HARI` di atas 60, dan jalankan paling banyak sekali sehari.
- Jangan menjalankan script di banyak perangkat sekaligus.
- Kalau muncul pesan "Kena limit/verifikasi", berhenti dulu. Buka aplikasi Instagram, konfirmasi **Ini saya**, lalu coba lagi besok.
- Untuk akun yang sangat penting, pertimbangkan untuk tidak memakai script ini.

**Kamu memakai script ini dengan risikomu sendiri.** Pembuat script tidak bertanggung jawab
