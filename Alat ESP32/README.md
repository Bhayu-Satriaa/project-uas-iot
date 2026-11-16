# Alat Penerjemah Saku - ESP32 (versi sederhana)

Satu tombol, tanpa musik. **Tahan tombol → bicara → lepas → terjemahan diucapkan lewat speaker.**
Arah terjemahan ditentukan otomatis oleh server dari bahasa yang terdeteksi.

## Cara pakai

1. Nyalakan alat. LCD menampilkan `WiFi tersambung` dan `Tahan tombol`.
2. **Tahan** tombol, ucapkan satu kalimat pendek (maksimal 4 detik) — LED merah menyala.
3. **Lepas** tombol — LED mati, LCD menampilkan `Memproses...`.
4. Server menerjemahkan (2–5 detik), lalu alat **mengucapkan** hasilnya — LED hijau menyala.
5. LCD menampilkan teks asli (baris 1) dan terjemahan (baris 2).

## Pengkabelan

| Perangkat | Kaki perangkat | Pin ESP32 | Catatan |
|---|---|---|---|
| Mikrofon INMP441 | SCK | GPIO 32 | |
| | WS | GPIO 33 | |
| | SD | GPIO 34 | |
| | VCC / GND | 3V3 / GND | **Jangan 5 V** |
| Amplifier MAX98357A | BCLK | GPIO 26 | |
| | LRC | GPIO 25 | |
| | DIN | GPIO 22 | |
| | VIN / GND | 5V (VIN) / GND | butuh 5 V |
| LCD I2C 16x2 | SDA | GPIO 21 | alamat 0x27 |
| | SCL | GPIO 22 | |
| | VCC / GND | 5V / GND | |
| Tombol | kaki 1 | GPIO 27 | |
| | kaki 2 | GND | memakai `INPUT_PULLUP`, tanpa resistor |
| LED merah | anoda | GPIO 13 | lewat resistor 220 Ω, katoda ke GND |
| LED hijau | anoda | GPIO 12 | lewat resistor 220 Ω |
| Baterai | 5 V | VIN | lihat catatan daya di bawah |

Catatan: Standar pengujian proyek saat ini menggunakan **Mode Headless (#define PAKAI_LCD 0)** bebas konflik pin. Teks terjemahan & transkrip otomatis tersimpan di log server (`riwayat.jsonl`) dan live visualizer (`/monitor`).

## Pengaturan di kode (`src/main.cpp`)

Firmware menggunakan **`WiFiMulti`** sehingga alat otomatis tersambung ke Hotspot HP / WiFi kampus tanpa perlu di-flash ulang:

```cpp
// Daftar Access Point yang otomatis dicoba:
wifiMulti.addAP("Penerjemah_Hotspot", "12345678");
wifiMulti.addAP("Hotspot_Jian", "12345678");
wifiMulti.addAP("Hotspot_Haikal", "12345678");
wifiMulti.addAP("Politani_Samarinda_University", "");

// Alamat server (laptop / cloud tunnel)
const char *SERVER = "http://10.10.14.151:8000";
```

### Indikator Status Lampu LED:
- **LED Merah Berkedip Cepat (150ms):** Sedang memindai dan menyambung ke Hotspot WiFi portabel.
- **LED Hijau Berkedip 2x:** WiFi tersambung dengan sukses dan sistem siap merekam (*Ready*).
- **LED Merah Menyala Terus:** Sedang merekam suara saat tombol Push-to-Talk ditahan.
- **LED Hijau Menyala Terus:** Sedang memutar suara terjemahan dari speaker.

## Membangun & mengirim ke board

```bash
# dari Windows (PowerShell), di folder Alat ESP32
python -m platformio run                       # memeriksa build
python -m platformio run -t upload --upload-port COM7
python -m platformio device monitor --port COM7
```

Hasil build terakhir (dengan WiFiMulti): **SUCCESS** — RAM 14,3 % (46.772 B), Flash 70,2 % (920.261 B).

## Susunan saling bergantung

```
[alat] --rekam--> WAV --HTTP POST--> [laptop: server] --> pengenal suara --> terjemah --> suara
                                                                              |
[alat] <--- MP3/WAV (audio_url) <---- berkas suara <--------------------------+
```

- Suara hasil dikirim server sebagai **WAV PCM 16 kHz mono** supaya alat tidak perlu decoder MP3.
- Bila paket `av` belum terpasang di laptop, server mengirim MP3 (alat belum bisa memutarnya).
  Setelah `av` terpasang, `format_untuk_alat` berubah menjadi `wav` secara otomatis.

## Kebutuhan daya (sesuai rancangan)

| Bagian | Arus kira-kira |
|---|---|
| ESP32 + WiFi aktif | 150 mA |
| LCD (dengan lampu latar) | 25 mA |
| Amplifier saat memutar | 200–600 mA |
| **Rata-rata saat menganggur** | sekitar 175 mA |

Dengan power bank 10.000 mAh: perkiraan **lebih dari 15 jam** menganggur, atau
**4–8 jam** bila terus-menerus memutar suara. Baterai 1 sel 18650 (2.600 mAh) kurang lebih
seperempat dari angka itu.

## Urutan pengujian yang disarankan

1. Uji tanpa board dulu: `python3 uji_pipeline.py --teks "..."` di laptop (sudah berhasil).
2. Uji firmware tanpa audio: sambungkan hanya LCD — pastikan WiFi, tombol, dan tampilan jalan.
3. Uji mikrofon: rekam lalu lihat berapa lama dan berapa byte yang terekam di Serial Monitor.
4. Uji pemutaran: kirim audio contoh dari server, dengarkan melalui amplifier dan speaker.
5. Uji alur penuh: tekan-bicara → terjemahan diucapkan.
