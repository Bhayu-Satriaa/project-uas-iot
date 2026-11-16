# 📋 DAFTAR KOMPONEN, ESTIMASI BUDGET & LOKASI PEMBELIAN
## Proyek IoT: Speaker Pintar Penerjemah Dua Arah (Voice Translator Device)

Dokumen ini adalah acuan resmi pengadaan perangkat keras, perakitan sirkuit, dan estimasi biaya untuk proyek **Speaker Pintar Penerjemah Dua Arah** berbasis ESP32.

---

## 1. Identitas Proyek & Akademik

- **Institusi:** Politeknik Pertanian Negeri Samarinda (Politani)
- **Program Studi:** Teknologi Rekayasa Perangkat Lunak (TRPL), Kelas 3A
- **Mata Kuliah:** Internet of Things (IoT) — Semester Ganjil
- **Dosen Pengampu:** Bapak Imron
- **Tim Pelaksana (Kelompok 3):**
  1. Bhayu Satria Sugara (Jian) — NIM: H253600447
  2. Haikal
  3. Egi
- **Konsep Desain:** **Headless Portable Communicator (Tanpa LCD, Baterai Mandiri & Casing Saku)**
  - Interaksi murni mengandalkan **suara lantang dari speaker** dan **sinyal visual lampu LED** (layaknya walkie-talkie pintar).
  - **Portabilitas Opsi B:** Ditenagai baterai Li-Ion 18650 internal (disediakan dosen), modul charger TP4056 + step-up 5V, saklar daya On/Off, dan dikemas rapi dalam Kotak Proyek X6.
  - Teks asli & terjemahan tetap otomatis tercatat di log server laptop (`riwayat.jsonl`) dan live visualizer (`/monitor`).

---

## 2. Daftar Komponen yang Digunakan (Bill of Materials)

```
========================================================================================
STATUS           | NAMA KOMPONEN                     | KETERANGAN & FUNGSINYA
========================================================================================
SUDAH ADA        | ESP32 DevKit V1 (30 / 38 pin)     | Otak sistem, kontroler WiFi & audio I2S
SUDAH ADA        | Kabel Data Micro-USB / Type-C     | Jalur flash program & charger baterai
DISEDIAKAN DOSEN | Baterai Li-Ion 18650 3.7V         | Sumber daya utama portabel mandiri
----------------------------------------------------------------------------------------
AKAN DIBELI      | Modul Mikrofon Digital INMP441    | Sensor suara I2S digital (Telinga alat)
AKAN DIBELI      | Modul Amplifier Digital MAX98357A | Penguat audio DAC I2S Class D 3W
AKAN DIBELI      | Speaker Mini 8 Ohm 3 Watt (40mm)  | Pengucap suara terjemahan (Mulut alat)
AKAN DIBELI      | Mini Breadboard 400 Titik / PCB   | Papan perakitan kompak (muat di kotak)
AKAN DIBELI      | Kabel Jumper (M-M & M-F)          | Kabel penghubung sirkuit
AKAN DIBELI      | Push Button Tactile Switch        | Tombol pemicu rekam (Push-to-Talk)
AKAN DIBELI      | LED 5mm Diffuse (1 Pcs)           | Indikator Tunggal Status Sistem
AKAN DIBELI      | Resistor 220 Ohm (1/4 Watt)       | Resistor pembatas arus LED
----------------------------------------------------------------------------------------
PORTABEL (OPSI B)| Holder Baterai 18650 1 Slot       | Dudukan baterai dengan kabel merah-hitam
PORTABEL (OPSI B)| Modul TP4056 + Boost Step-Up 5V   | Charger baterai Li-Ion + konverter 5V
PORTABEL (OPSI B)| Saklar Geser On/Off Mini (SPDT)   | Saklar pemutus daya utama baterai
PORTABEL (OPSI B)| Kotak Proyek Plastik X6           | Casing enclosure genggam saku (12x8x4cm)
========================================================================================
```

---

## 3. Rincian Estimasi Budget & Simulasi Patungan

Seluruh komponen pendukung (selain ESP32 yang sudah ada dan Baterai yang disediakan Dosen) direncanakan dibeli dengan rincian biaya:

| No | Nama Barang | Jumlah | Estimasi Harga Satuan | Subtotal |
|:---|:---|:---:|:---:|:---:|
| 1 | Modul Mikrofon Digital INMP441 I2S | 1 pcs | Rp 25.000 | Rp 25.000 |
| 2 | Modul Amplifier Digital MAX98357A I2S Mono 3W | 1 pcs | Rp 45.000 | Rp 45.000 |
| 3 | Speaker Mini 8 Ohm 3 Watt (Diameter 40mm) | 1 pcs | Rp 15.000 | Rp 15.000 |
| 4 | Mini Breadboard 400 titik (Half-size) | 1 pcs | Rp 12.000 | Rp 12.000 |
| 5 | Kabel Jumper Male-to-Male (1 strip isi 20) | 1 strip | Rp 8.000 | Rp 8.000 |
| 6 | Kabel Jumper Male-to-Female (1 strip isi 20) | 1 strip | Rp 8.000 | Rp 8.000 |
| 7 | Push Button Tactile Switch 6x6x5mm | 1 pack (5 pcs) | Rp 2.500 | Rp 2.500 |
| 8 | LED 5mm Diffuse (Merah & Hijau) | 1 pack (4 pcs) | Rp 2.000 | Rp 2.000 |
| 9 | Resistor 220 Ohm 1/4W Metal Film | 1 strip (10 pcs) | Rp 1.000 | Rp 1.000 |
| 10 | Holder Baterai 18650 1 Slot kabel | 1 pcs | Rp 4.000 | Rp 4.000 |
| 11 | Modul TP4056 + Booster 5V (2-in-1 Powerbank) | 1 pcs | Rp 10.000 | Rp 10.000 |
| 12 | Saklar Geser On/Off Mini SPDT | 1 pcs | Rp 1.500 | Rp 1.500 |
| 13 | Kotak Proyek Plastik X6 (Karunia Elektronika) | 1 pcs | Rp 10.000 | Rp 10.000 |
| **SUBTOTAL HARGA KOMPONEN** | | | | **Rp 144.000** |
| **ESTIMASI ONGKOS KIRIM (Jawa ke Samarinda)** | Regular 1 kg | | | **Rp 35.000** |
| **TOTAL KESELURUHAN ESTIMASI BUDGET** | | | | **± Rp 179.000** |

### 💡 Simulasi Patungan Tim (Kelompok 3):
- **Bhayu Satria Sugara (Jian):** Rp 60.000
- **Haikal:** Rp 60.000
- **Egi:** Rp 60.000
- *Total terkumpul:* **Rp 180.000** (Cukup untuk menutupi seluruh part, casing, dan modul daya).

---

## 4. Panduan & Direktori Lokasi Pembelian

### A. Toko Fisik Offline di Kota Samarinda (Bisa Didatangi Hari Ini)

Jika ingin mendapatkan barang hari ini juga tanpa menunggu paket kiriman:

1. **Buana Elektronik (Spesialis Speaker Mini & Audio)**
   - **Alamat:** Jl. Panglima Batur No. 64, Pelabuhan, Samarinda Kota
   - **Telepon:** (0541) 741937
   - **Target Barang:** Speaker mini 8Ω 3W (40mm), kabel audio, timah solder.
2. **Suara Indah Groups (Audio & Sound System)**
   - **Alamat:** Jl. M. Yamin Artanusa Indah No. 28, Gunung Kelua, Samarinda Ulu
   - **Kontak/WA:** 0853-1168-3333
   - **Catatan:** Dekat kawasan kampus (area Unmul & Politani). Alternatif mencari speaker mini.
3. **Karunia Elektronika & Toko Aladin (Komponen Pasif & Prototyping)**
   - **Alamat:** Jl. KH. Abul Hasan No. 14, Pasar Pagi, Samarinda Kota
   - **Target Barang:** Breadboard, kabel jumper, push button, LED merah/hijau, resistor 220Ω, pin header.

---

### B. Toko Online Lokal Samarinda (Pengiriman Instan GoSend / Grab)

Bisa dipesan melalui marketplace dan sampai di hari yang sama:
- **io Power** (Tokopedia — Filter Kota Samarinda): Menyediakan kabel jumper, modul sensor, breadboard, ESP32.
- **Adawwino Store** (Shopee — Lokasi Kota Samarinda): Menyediakan part robotika dan modul elektronika dasar.

---

### C. Toko untuk Modul Audio Khusus (INMP441 & MAX98357A)

Karena modul I2S digital jarang distok di toko fisik konvensional Samarinda:

1. **Opsi Regional Terdekat: AB Tech / Arduino Balikpapan**
   - **Lokasi:** Jl. Karang Jawa, Mekar Sari, Balikpapan Tengah
   - **Katalog:** `abpos.online` / Tokopedia AB Tech Balikpapan
   - **Kelebihan:** Pengiriman ke Samarinda hanya butuh 1 hari (via travel atau kurir lokal).
2. **Opsi Checkout 1 Keranjang Online (Surabaya / Bandung):**
   - **Digiware Store Surabaya** (Tokopedia): Pengiriman dari Surabaya ke Samarinda via kargo udara cepat (2-3 hari).
   - **CNC Store Bandung** (Tokopedia / Shopee): Katalog modul I2S (INMP441 & MAX98357A) sangat lengkap bersama breadboard dan jumper.

---

## 5. Template Chat / Catatan untuk Penjual Online

Salin dan gunakan pesan ini saat hendak checkout di Tokopedia/Shopee:

> *"Halo Gan, mau konfirmasi pesanan:
> 1. Apakah modul INMP441 dan MAX98357A-nya sudah termasuk pin header kakinya?
> 2. Apakah speaker mini 8 Ohm 3 Watt, breadboard MB-102 830 titik, dan kabel jumpernya ready stock untuk dikirim hari ini?
> Terima kasih!"*

---

## 6. Skema Pinout Hardware (8 GPIO Bebas Konflik)

Susunan pinout yang sudah disesuaikan pada firmware ESP32:

```
====================================================================================
MODUL INMP441 (Mikrofon Digital I2S Input) --> ESP32 DevKit:
  - VDD   -----> 3.3V ESP32  (PERINGATAN KERAS: Jangan sambung ke 5V!)
  - GND   -----> GND
  - SCK   -----> GPIO 32     (Serial Clock)
  - WS    -----> GPIO 33     (Word Select)
  - SD    -----> GPIO 34     (Serial Data)
  - L/R   -----> GND         (Mengunci ke Channel Kiri)

MODUL MAX98357A (Amplifier I2S DAC Output) --> ESP32 DevKit:
  - VIN   -----> 5V / VIN ESP32
  - GND   -----> GND
  - BCLK  -----> GPIO 26     (Bit Clock)
  - LRC   -----> GPIO 25     (Left/Right Clock)
  - DIN   -----> GPIO 22     (Digital Audio IN)
  - GAIN  -----> Tidak disambung / GND (Gain default 9dB)
  - SD    -----> Tidak disambung (Default ON)
  - Terminal Sekrup (OUT+ & OUT-) -----> 2 Kabel Speaker 8 Ohm 3 Watt

TOMBOL & LAMPU STATUS (7 GPIO TOTAL):
  - Push Button  : Kaki 1 -> GPIO 27  |  Kaki 2 -> GND (INPUT_PULLUP internal)
  - LED Status   : Anoda  -> GPIO 13 (lewat R 220Ω) | Katoda -> GND (Atau pakai Onboard LED GPIO 2)

SISTEM DAYA BATERAI PORTABEL (OPSI B):
  - Baterai 18650 (3.7V) -> Holder 18650
  - Kabel Merah Holder (+) -> Saklar Geser On/Off -> Pin B+ Modul TP4056 Boost
  - Kabel Hitam Holder (-) -> Pin B- Modul TP4056 Boost
  - Output Modul TP4056 (VOUT+ 5V) -> VIN ESP32 & VIN MAX98357A
  - Output Modul TP4056 (GND)      -> GND ESP32 & GND MAX98357A
  - Port Cas (Type-C / Micro-USB)  -> Ditempatkan menghadap luar dinding Kotak X6
====================================================================================
```

---

## 7. Panduan Alur Kerja Alat di Lapangan

1. **Hubungkan Daya:** Pasang kabel USB ESP32 ke laptop atau power bank 5V. ESP32 otomatis tersambung ke WiFi/Hotspot HP.
2. **Mulai Merekam:** **Tahan** tombol Push Button (GPIO 27). LED Merah menyala. Ucapkan satu kalimat (maksimal 4 detik).
3. **Proses Terjemahan:** **Lepas** tombol. LED Merah padam. Audio dikirim ke server FastAPI di laptop. Server mendeteksi bahasa, menerjemahkan, dan menyiapkan audio suara WAV PCM 16-bit.
4. **Mendengar Terjemahan:** LED Hijau menyala. Speaker otomatis membacakan hasil terjemahan secara jernih dan lantang. Setelah selesai, LED Hijau padam dan sistem kembali standby.
