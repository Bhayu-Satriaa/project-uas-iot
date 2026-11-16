# Server Penerjemah - Smart Speaker (Tingkat 1: laptop + internet)

Sisi server dari project *Speaker Penerjemah Indonesia <-> Inggris*.
Bagian ini bisa diuji **tanpa board ESP32**: cukup laptop.

## Alur

```
(ESP32) audio WAV  ->  POST /terjemah?arah=id-en
                          |
                          +-- 1. pengenal suara (faster-whisper, lokal)   -> teks asli
                          +-- 2. terjemah (model lewat 9Router)           -> teks terjemahan
                          +-- 3. suara hasil (edge-tts lewat 9Router)     -> MP3
                          |
       MP3 (base64)  <-  balasan JSON
```

## Berkas

| Berkas | Kegunaan |
|---|---|
| `konfigurasi.py` | alamat & kunci gateway (dibaca dari lingkungan, **tidak** disimpan di berkas) |
| `pipeline.py` | tiga tahap: pengenal suara, terjemah, suara + pengukur waktu |
| `server_terjemah.py` | server HTTP untuk dipanggil ESP32 |
| `uji_pipeline.py` | uji dari terminal tanpa mikropon |
| `buat_sampel.py` | membuat audio contoh untuk uji pengenal suara |
| `riwayat.jsonl` | catatan percakapan (untuk dashboard) |
| `templates/monitor.html` | antarmuka web visualizer live (`/monitor`) |

## Cara pakai (Windows PowerShell / Linux)

### Menjalankan di Windows (Laptop Jian):
```powershell
cd "D:\Politani\Semester 3\IoT\Proyek Speaker Penerjemah\Server"

# 1. Jalankan server FastAPI
python server_terjemah.py

# 2. Buka dashboard monitor di browser:
#    http://localhost:8000/monitor

# 3. Uji cepat pipeline dari terminal terpisah:
python uji_pipeline.py --teks "Selamat pagi, berapa harga ini?" --arah id-en
```

### Opsi Portabel: Menjalankan Cloudflare Tunnel (Tanpa Kabel & Tanpa Masalah IP)
Agar ESP32 dapat memanggil server dari hotspot HP manapun tanpa repot mencari IP laptop:
```powershell
# Jalankan cloudflared tunnel gratis (quick tunnel)
cloudflared tunnel --url http://localhost:8000
# Salin domain *.trycloudflare.com yang muncul ke variabel SERVER di main.cpp
```

## Pengenal suara (STT) - faster-whisper

Tahap STT memakai pengenal suara lokal **faster-whisper**:

```powershell
# Windows PowerShell:
pip install faster-whisper av fastapi uvicorn requests
```

Model `small` (~500 MB) diunduh otomatis saat pemakaian pertama. Ukuran model diatur di
`konfigurasi.py` (`MODEL_STT`): `base` (lebih cepat) atau `small` (lebih akurat).

## Pengaturan

| Variabel | Bawaan | Keterangan |
|---|---|---|
| `GATEWAY_URL` | `http://<ip-host-windows>:20128` | alamat 9Router |
| `GATEWAY_KEY` | dari `~/.hermes/.env` | kunci gateway |
| `MODEL_TERJEMAH` | `cmc/deepseek/deepseek-v4-flash` | terukur 1,6 - 2,0 detik |
| `SUARA_ID` / `SUARA_EN` | `id-ID-GadisNeural` / `en-US-AriaNeural` | suara edge-tts |
| `MODEL_STT` | `small` | ukuran model whisper lokal |

## Hasil uji (12 Nov 2026, dari laptop Jian)

| Arah | Kalimat | Hasil | Terjemah | Suara | Total |
|---|---|---|---|---|---|
| id-en | Selamat pagi, berapa harga ini? | Good morning, how much is this? | 1,99 s | 1,75 s | **3,74 s** |
| en-id | Good morning, how much is this? | Selamat pagi, berapa harga ini? | 1,61 s | 1,33 s | **2,94 s** |

Tambahan waktu pengenal suara lokal (perkiraan 1 - 3 detik per kalimat pendek) dan waktu
kirim audio dari alat (0,1 - 0,3 detik) = total di alat sekitar **4 - 8 detik** per kalimat.

## Catatan penting

- Laptop harus menyala dan berada di jaringan yang sama dengan alat (WiFi rumah atau hotspot HP).
- Terjemah & suara hasil memakai layanan **online** lewat 9Router - butuh internet.
- Yang bisa lepas dari internet hanya tahap pengenal suara (karena dijalankan lokal).
- WiFi dan Bluetooth tidak dipakai bersamaan: mode terjemah (WiFi) dan mode musik (Bluetooth) dipisah.
