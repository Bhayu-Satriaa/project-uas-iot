# 🧠 MEMORI SESI: SMART PORTABLE VOICE TRANSLATOR (SPEAKER PENERJEMAH IOT)
*Tanggal Sesi: 16 November 2026 | Kelompok 3 TRPL 3A Politani Samarinda*

Dokumen ini mencatat seluruh kronologi diskusi, keputusan arsitektur krusial, pembaruan kode, hasil pengujian, serta referensi teknis yang dihasilkan selama sesi ini.

---

## 1. Identitas Proyek & Tim
- **Pengguna:** Jian (Bhayu Satria Sugara) — NIM: H253600447
- **Anggota Kelompok 3:** Bhayu Satria Sugara (Jian), Haikal, Egi
- **Kampus / Prodi:** Politeknik Pertanian Negeri Samarinda (Politani), D4 TRPL, Kelas 3A
- **Mata Kuliah:** Internet of Things (IoT) — Semester Ganjil
- **Dosen Pengampu:** Bapak Imron
- **Nama Proyek:** Smart Portable Voice Translator (Speaker Pintar Penerjemah Dua Arah)

---

## 2. Rangkuman Keputusan Teknis Penting Sesi Ini

### A. Tindak Lanjut Masukan Dosen: "Alat Harus Portable"
- **Masukan Dosen Pengampu (Pak Imron):** Alat tidak boleh statis terikat kabel laptop; harus berbentuk perangkat genggam mandiri (*handheld portable*).
- **Keputusan Sumber Daya:** Dipilih **Opsi B (Terintegrasi Total di Dalam Casing)**.
- **Poin Krusial:** **Baterai Li-Ion 18650 3.7V akan disediakan oleh Dosen / Laboratorium IoT TRPL** (Biaya baterai Rp 0).
- **Komponen Pendukung Daya yang Ditambahkan:**
  1. Holder Baterai 18650 1 Slot dengan kabel (Rp 4.000)
  2. Modul Charger TP4056 + Step-Up Booster 5V (Rp 10.000)
  3. Saklar Geser On/Off Mini SPDT (Rp 1.500)
  4. Casing Kotak Proyek Plastik X6 ukuran 12 x 8 x 4 cm (Rp 10.000 di Karunia Elektronika Samarinda)
- **Status Anggaran:** Total biaya komponen mandiri Rp 144.000 + ongkir Rp 35.000 = **±Rp 179.000** (Simulasi patungan 3 orang: **Rp 60.000 / orang**).

### B. Penyederhanaan Indikator Visual: "Hanya Pakai 1 LED"
- Pengguna memutuskan untuk beralih dari rancangan 2 LED menjadi **1 LED Status Tunggal**.
- **Keuntungan:** Sirkuit menjadi sangat ringkas, hanya menggunakan **7 pin GPIO bebas konflik**, menghemat jalur kabel di breadboard dan resistor.
- **Pola Status 1 LED (di GPIO 13, atau Onboard LED GPIO 2):**
  - *Kedip pelan (150ms):* Sedang mencari dan menghubungkan ke WiFi/Hotspot.
  - *Kedip 2x pendek lalu mati:* WiFi terhubung, sistem siap (*Standby/Ready*).
  - *Menyala solid/stabil:* Tombol Push-to-Talk sedang ditahan & sedang merekam suara.
  - *Kedip cepat 3x:* Audio sedang dikirim dan diproses/diterjemahkan di server AI.
  - *Menyala:* Speaker sedang membacakan audio hasil terjemahan.
  - *Mati:* Selesai, kembali ke mode siaga (*Standby*).
  - *Kedip cepat 5x:* Indikasi gagal koneksi / error.

### C. Pembaruan Konektivitas: Integrasi `WiFiMulti`
- Menghindari masalah *hardcoded* WiFi yang membuat alat gagal tersambung saat dibawa mobile.
- Firmware `Alat ESP32/src/main.cpp` kini menyimpan daftar access point:
  1. `Penerjemah_Hotspot` (Hotspot HP tim)
  2. `Hotspot_Jian`
  3. `Hotspot_Haikal`
  4. `Politani_Samarinda_University` (WiFi Kampus)
  5. `Wokwi-GUEST` (Simulator Wokwi)
- Dilengkapi auto-reconnect di latar belakang (`wifiMulti.run()`).

---

## 3. Spesifikasi Pinout Definitif (7 GPIO Bebas Konflik)

| Modul Hardware | Pin Modul | Pin ESP32 DevKit | Keterangan & Pengkabelan |
|:---|:---:|:---:|:---|
| **Mikrofon Digital INMP441** | VDD | **3.3V** | *Wajib 3.3V, jangan pernah ke 5V!* |
| | GND | **GND** | Ground bersama |
| | SCK | **GPIO 32** | Serial Clock I2S Input |
| | WS | **GPIO 33** | Word Select / L-R Clock |
| | SD | **GPIO 34** | Serial Data (Input only) |
| | L/R | **GND** | Channel Kiri |
| **Amplifier DAC MAX98357A** | VIN | **5V (Boost Out)** | Tegangan penguat 3 Watt |
| | GND | **GND** | Ground bersama |
| | BCLK | **GPIO 26** | Bit Clock I2S Output |
| | LRC | **GPIO 25** | Left/Right Clock (WSEL) |
| | DIN | **GPIO 22** | Digital Audio In |
| | OUT+ & OUT- | Speaker 8Ω 3W | Terminal 2 kabel speaker mini |
| **Push Button (Push-to-Talk)** | Kaki 1 / 2 | **GPIO 27 & GND** | Internal `INPUT_PULLUP` (tanpa resistor luar) |
| **LED Indikator Status (1 LED)** | Anoda / Katoda | **GPIO 13 & GND** | Seri R 220Ω (Opsi alternatif: Onboard GPIO 2) |

---

## 4. Simulasi Wokwi yang Disiapkan

Telah disediakan berkas pendukung simulasi Wokwi di folder `Alat ESP32/`:
1. **`diagram_native.json`:** Menggunakan komponen bawaan Wokwi (`wokwi-microphone` & `wokwi-buzzer`). Langsung muncul gambar mikrofon dan speaker bulat di browser tanpa konfigurasi tambahan.
2. **`diagram.json`:** Menggunakan custom breakout chip `chip-inmp441` dan `chip-max98357a`.
3. **`inmp441.chip.json` & `max98357a.chip.json`:** Definisi pin kaki untuk custom chip I2S.
4. **`wokwi.toml`:** Konfigurasi simulator untuk satu klik via ekstensi VS Code Wokwi.

---

## 5. Bukti Validasi & Kompilasi (PlatformIO)
Kompilasi firmware terakhir pada `Alat ESP32` berhasil 100%:
```text
Processing esp32dev (platform: espressif32@6.8.1; board: esp32dev; framework: arduino)
RAM:   [=         ]  14.3% (used 46772 bytes from 327680 bytes)
Flash: [=======   ]  70.2% (used 920249 bytes from 1310720 bytes)
========================= [SUCCESS] Took 10.07 seconds =========================
```

---

## 6. Referensi Proyek Dunia Nyata (Benchmarking)
1. **`techiesms` (YouTube):** *"ESP32 Voice Assistant with ChatGPT"* (Stack sama persis: ESP32 + INMP441 + MAX98357A).
2. **`letranminhdat1516/esp32-translator` (GitHub):** Real-time conversational two-way translator (English ↔ Vietnamese).
3. **`Antara Pocket Translator`:** Translator saku berbasis tombol push-to-talk.
4. **Keunggulan Sistem Kita:** Menggunakan streaming WAV PCM mentah 16-bit dari server sehingga ESP32 tidak perlu decoder MP3 internal yang rawan kehabisan RAM.

---

## 7. Status Berkas Repositori Terkini
- `README.md` (Root): Berkas utama laporan & panduan sistem telah dibuat lengkap.
- `memori.md`: Catatan memori sesi permanen ini.
- `komponen.md`: Rincian BOM belanja & toko Samarinda (Buana, Suara Indah, Karunia).
- `AGENTS.md` & `GEMINI.md`: Memori agen sinkron dengan pinout 7-GPIO & portabilitas Opsi B.
- `Alat ESP32/src/main.cpp`: Firmware aktif dengan 1 LED, WiFiMulti, dan I2S DMA.
- `Server/server_terjemah.py`: Backend FastAPI siap uji dengan endpoint `/terjemah`, `/suara`, dan live dashboard `/monitor`.
