# KONTEKS & MEMORI PROYEK: SPEAKER PENERJEMAH IOT

Dokumen ini adalah memori permanen untuk asisten AI (Antigravity, Hermes, atau CLI agent lainnya) agar dapat langsung melanjutkan pekerjaan di terminal manapun tanpa perlu membaca ulang konteks dari awal.

---

## 1. Identitas & Akademik
- **Pengguna:** Jian (Bhayu Satria Sugara)
- **Kampus / Prodi:** Politeknik Pertanian Negeri Samarinda (Politani), Prodi TRPL (Teknologi Rekayasa Perangkat Lunak), Kelas 3A, Semester Ganjil.
- **Mata Kuliah:** Internet of Things (IoT)
- **Dosen Pengampu:** Bapak Imron
- **Kelompok:** Kelompok 3 (Anggota: Bhayu Satria Sugara / Jian, Haikal, Egi)
- **Gaya Komunikasi:** Gunakan sapaan "saya", bahasa lugas, teknis, dan langsung solutif.

---

## 2. Gambaran Umum Proyek
**Nama Proyek:** Speaker Pintar Penerjemah Dua Arah (Voice Translator Device)
**Tujuan:** Alat portabel untuk menerjemahkan percakapan lisan secara otomatis antara dua bahasa (Bahasa Indonesia ↔ Bahasa Inggris) secara real-time tanpa ribet memilih arah bahasa secara manual. Target penggunaan: UMKM, pemandu wisata, atau pedagang lokal saat berinteraksi dengan wisatawan asing.

---

## 3. Arsitektur & Alur Kerja Sistem

### Alur Satu Tombol (Push-to-Talk):
1. **Pengguna Menahan Tombol:** LED Merah menyala menandakan proses perekaman aktif.
2. **Bicara (Maks 4 detik):** Mikrofon merekam suara pengguna langsung ke buffer RAM ESP32.
3. **Pengguna Melepas Tombol:** LED Merah padam. ESP32 mengemas rekaman menjadi format WAV dan mengirimnya via HTTP POST ke endpoint server lokal: `http://<ip-server>:8000/terjemah`.
4. **Pemrosesan di Server:**
   - **STT (Speech-to-Text):** Mendeteksi bahasa audio dan mengubahnya menjadi teks.
   - **Penerjemahan (Translation):** Menerjemahkan otomatis (Indonesia ➔ Inggris atau Inggris ➔ Indonesia).
   - **TTS (Text-to-Speech):** Mengonversi teks terjemahan menjadi suara audio format **WAV mentah (PCM)**.
   - **Logging:** Riwayat percakapan otomatis dicatat ke `riwayat.jsonl`.
5. **Output di Alat:**
   - Layar LCD menampilkan teks asli dan teks hasil terjemahan.
   - LED Hijau menyala, ESP32 mengunduh berkas audio WAV hasil dari server dan memutarnya melalui amplifier & speaker.
   - LED Hijau padam ketika audio selesai diputar.

---

## 4. Spesifikasi Hardware & Pinout (Alat ESP32 Portabel - 8 GPIO Bebas Konflik)

- **Mikrokontroler:** ESP32 Development Board (NodeMCU / DOIT ESP32 DevKit v1 30/38 pin)
- **Mikrofon I2S (INMP441) - Sensor Suara:**
  - VDD ➔ 3.3V ESP32 (*PERINGATAN: Jangan sambung ke 5V!*)
  - GND ➔ GND
  - SCK (Serial Clock) ➔ GPIO 32
  - WS (Word Select) ➔ GPIO 33
  - SD (Serial Data) ➔ GPIO 34 (Input only)
  - L/R ➔ GND (Channel Kiri)
- **Amplifier I2S (MAX98357A) + Speaker Mini 8 Ω 3W (40mm):**
  - VIN ➔ 5V (dari modul booster TP4056 / VIN ESP32)
  - GND ➔ GND
  - BCLK (Bit Clock) ➔ GPIO 26
  - LRC (Left/Right Clock) ➔ GPIO 25
  - DIN (Digital Audio In) ➔ GPIO 22
  - GAIN / SD ➔ Default (tidak disambung / 9dB)
  - Terminal OUT+ & OUT- ➔ 2 kabel speaker 8Ω 3W
- **Tombol & Indikator LED (7 GPIO Bebas Konflik):**
  - Push Button (Push-to-Talk) ➔ GPIO 27 (Kaki 1 -> GPIO 27, Kaki 2 -> GND, INPUT_PULLUP internal)
  - LED Status (1 LED Saja) ➔ GPIO 13 (lewat R 220Ω ke GND, atau pakai Onboard LED GPIO 2)
    - Kedip pelan: Mencari WiFi
    - Kedip 2x: WiFi Siaga (Ready)
    - Menyala stabil: Merekam suara saat tombol ditahan
    - Kedip cepat 3x: Sedang diproses / diterjemahkan di server
    - Menyala: Memutar hasil suara di speaker
- **Sistem Daya Portabel (Opsi B):**
  - Baterai: 1x Li-Ion 18650 3.7V (Disediakan Dosen/Lab) + Holder 18650
  - Saklar: Slide Switch On/Off SPDT di jalur kutub positif baterai
  - Modul Charger + Boost 5V: TP4056 5V 1A dengan port pengisian USB samping
  - Casing Enclosure: Kotak Proyek Plastik X6 (12 x 8 x 4 cm) genggam saku

---

## 5. Struktur Berkas & Komponen Software

Folder Utama: `D:\Politani\Semester 3\IoT\Proyek Speaker Penerjemah`

```text
├── GEMINI.md                  <-- File konteks/memori otomatis ini
├── AGENTS.md                  <-- Alias memori untuk agent lain
├── Alat ESP32/                <-- Project PlatformIO untuk Firmware
│   ├── platformio.ini         <-- Konfigurasi PlatformIO (espressif32, arduino framework)
│   ├── src/
│   │   └── main.cpp           <-- Kode utama ESP32 (I2S Mic, I2S DAC, WiFi HTTP client)
│   └── README.md              <-- Panduan pengkabelan & instruksi flash
└── Server/                    <-- Server Python lokal (FastAPI)
    ├── server_terjemah.py     <-- Entry point FastAPI (endpoint /terjemah, file static /suara)
    ├── pipeline.py            <-- Pipeline terjemahan (STT -> Translate -> TTS -> WAV)
    ├── konfigurasi.py         <-- Setelan port, IP, path audio, dan model
    ├── uji_pipeline.py        <-- Skrip pengujian alur terjemahan
    ├── buat_sampel.py         <-- Pembuat audio sampel uji
    ├── riwayat.jsonl          <-- Database log percakapan real-time
    ├── sampel_audio/          <-- Kumpulan file audio uji (Bahasa Indonesia & Inggris)
    └── suara_hasil/           <-- Cache file audio hasil TTS yang siap disajikan ke ESP32
```

---

## 6. Keputusan Teknis Penting & Troubleshooting

1. **Keputusan Audio WAV Mentah (Bukan MP3):**
   - *Masalah:* Library audio MP3 decoder ESP32 modern membutuhkan standar C++20 yang tidak didukung langsung oleh toolchain praktikum PlatformIO lama.
   - *Solusi:* Server bertugas langsung merender suara hasil menjadi **WAV uncompressed (PCM 16-bit)**. Dengan begitu, ESP32 hanya butuh streaming byte data ke I2S DAC MAX98357A tanpa perlu decoder internal yang membebani chip.
   - *Hasil Kompilasi:* RAM hanya terpakai **14.4%**, Flash **71.0%** (Sangat stabil).

2. **Mesin STT (Speech to Text):**
   - Direkomendasikan: Menggunakan `faster-whisper` (model `small`) berjalan di virtual environment lokal Python (`~/venv-whisper`) agar bekerja **100% offline**, gratis, tanpa kuota API key eksternal.

---

## 7. Perintah Cepat (Cheatsheet Perintah Terminal)

### Menjalankan Server Lokal:
```bash
cd "D:\Politani\Semester 3\IoT\Proyek Speaker Penerjemah\Server"
# Mengaktifkan venv jika ada, lalu jalankan:
python server_terjemah.py
# Server berjalan di: http://0.0.0.0:8000
```

### Menguji Pipeline Server:
```bash
cd "D:\Politani\Semester 3\IoT\Proyek Speaker Penerjemah\Server"
python uji_pipeline.py
```

### Mengompilasi & Mengunggah Firmware ESP32:
```bash
cd "D:\Politani\Semester 3\IoT\Proyek Speaker Penerjemah\Alat ESP32"
pio run                  # Untuk compile saja
pio run --target upload  # Untuk upload ke board via kabel USB
pio device monitor       # Untuk memantau serial monitor (baud 115200)
```

---

## 8. Status Terakhir & Langkah Selanjutnya (Update 16 November 2026)

### Keputusan Arsitektur Terbaru:
1. **Mode Headless (Tanpa LCD):**
   - Disetujui mengeliminasi modul LCD 16x2.
   - Keuntungan: Menghilangkan konflik pin GPIO 22, menghemat biaya ~Rp 35.000, menghemat 25-50mA daya, dan menyederhanakan perkabelan hanya menjadi 8 pin GPIO.
   - Firmware di `src/main.cpp` disetel `#define PAKAI_LCD 0` dan terverifikasi build SUCCESS (RAM 14.3%, Flash 69.9%).

2. **Portabilitas Penuh (Masukan Dosen Pengampu Pak Imron - Opsi B):**
   - Dosen pengampu memberi masukan bahwa alat harus portabel. Baterai Li-Ion 18650 akan disediakan oleh dosen/lab.
   - Mengadopsi **Opsi B (Terintegrasi Total di Dalam Casing)**: Baterai 18650 + Holder + Modul TP4056 Step-Up 5V + Saklar On/Off Mini + Kotak Proyek Plastik X6 (12 x 8 x 4 cm).
   - Firmware diperbarui dengan fitur **`WiFiMulti`** (Hotspot HP Jian, Hotspot Haikal, WiFi Politani) dengan indikator visual LED (merah berkedip saat menyambung, hijau berkedip 2x saat siap). Hasil build SUCCESS (RAM 14.3%, Flash 70.2%).

3. **Pengadaan Komponen & Panduan Belanja:**
   - Panduan belanja definitif diperbarui di `komponen.md` (Total komponen Rp 144.000 + ongkir ke Samarinda ~Rp 35.000 = ±Rp 179.000, simulasi patungan 3 orang ~Rp 60.000/orang).
   - Pemetaan toko fisik Samarinda: Buana Elektronik (Jl. Panglima Batur), Suara Indah (Jl. M. Yamin), Karunia Elektronika (Jl. KH. Abul Hasan). Toko online lokal: io Power & Adawwino Store. Modul I2S: AB Tech Balikpapan / online Surabaya.

4. **Web Dashboard Monitor (Anti-Slop Clean Light Mode):**
   - Memasang skill `antislop-ui` dari `miqdadbadjuber/anti-slop` di `.agents/skills/antislop-ui/`.
   - Membuat antarmuka live visualizer di `Server/templates/monitor.html` yang diakses via `http://localhost:8000/monitor`.
   - Estetika: Clean Light Mode (latar off-white #F8FAFC, border 1px #E2E8F0, font Inter + JetBrains Mono), auto-polling live transkrip & audio player.

5. **Model AI Penerjemah:**
   - Menggunakan `cmc/deepseek/deepseek-v4-flash` via 9Router gateway lokal (`http://127.0.0.1:20128/v1/chat/completions`) dengan `temperature: 0` dan fallback gratis ke `nous/stepfun/step-3.7-flash:free`.

### Langkah Selanjutnya (Next Steps):
1. **Pengadaan Komponen:** Eksekusi pembelian part oleh Kelompok 3 sesuai panduan `komponen.md`.
2. **Setup STT Offline:** Setup `faster-whisper` di server lokal.
3. **Perakitan & Pengujian Breadboard:** Pasang modul INMP441 + MAX98357A + Speaker 8Ω begitu barang tiba sesuai skema pinout 8-GPIO.
