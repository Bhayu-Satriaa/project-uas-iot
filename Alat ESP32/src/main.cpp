/* Alat penerjemah saku - ESP32 (versi sederhana: satu tombol, tanpa musik)
 *
 * Cara pakai:
 *   TAHAN tombol -> merekam (LED merah)  |  LEPAS -> dikirim, diterjemahkan, diucapkan (LED hijau)
 *   Arah terjemahan ditentukan otomatis oleh server dari bahasa yang terdeteksi.
 *
 * Suara hasil dikirim server sebagai WAV (PCM 16 kHz mono), jadi alat ini
 * TIDAK butuh decoder MP3 - cukup tulis sampel ke I2S.
 *
 * Pengkabelan:
 *   Mikrofon INMP441   : SCK->32, WS->33, SD->34, VCC->3V3, GND
 *   Amplifier MAX98357A: BCLK->26, LRC->25, DIN->22, VIN->5V, GND
 *   LCD I2C (opsional) : SDA->21, SCL->22, VCC->5V, GND
 *   Tombol             : kaki 1->27, kaki 2->GND
 *   LED Status (1 LED) : GPIO 13 (lewat resistor 220 ohm, katoda ke GND)
 *                        *Bisa juga memakai onboard LED bawaan ESP32 di GPIO 2 tanpa resistor
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <driver/i2s.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ------------------------------ PENGATURAN ------------------------------
// WiFi Multi: Alat otomatis tersambung ke hotspot terdekat tanpa flash ulang
WiFiMulti wifiMulti;

// Server penerjemah (Laptop / Cloud tunnel)
const char *SERVER = "http://10.10.14.151:8000";   // Sesuaikan IP laptop di hotspot atau URL Cloudflare Tunnel

#define PIN_TOMBOL 27
#define PIN_LED    13           // 1 LED Status (Gunakan GPIO 2 bila ingin memakai onboard LED ESP32)
#define PAKAI_LCD  0            // 0 = tanpa LCD (Headless Voice Mode)

const int      LAJU_SAMPEL = 16000;             // Hz
const uint32_t MAKS_DETIK  = 3;                 // batas durasi rekaman (3 detik)
const size_t   MAKS_SAMPEL = (size_t)LAJU_SAMPEL * MAKS_DETIK;
const size_t   UKURAN_WAV  = MAKS_SAMPEL * 2 + 44;

#define PORT_I2S I2S_NUM_0
#define MIC_SCK 32
#define MIC_WS  33
#define MIC_SD  34
#define AMP_BCLK 26
#define AMP_LRC  25
#define AMP_DIN  22

#if PAKAI_LCD
LiquidCrystal_I2C lcd(0x27, 16, 2);
#endif

static uint8_t *wav = nullptr;                  // buffer kirim (WAV)
static uint8_t *bufPutar = nullptr;             // buffer potongan saat memutar
static bool micSiap = false, ampSiap = false;

// ------------------------------ UTILITAS ------------------------------
void setLed(bool nyala) {
  digitalWrite(PIN_LED, nyala ? HIGH : LOW);
}

void kedipLed(int kali, int onMs = 150, int offMs = 100) {
  for (int i = 0; i < kali; i++) {
    digitalWrite(PIN_LED, HIGH);
    delay(onMs);
    digitalWrite(PIN_LED, LOW);
    if (i < kali - 1) delay(offMs);
  }
}

void tampil(const char *b1, const char *b2 = "") {
#if PAKAI_LCD
  lcd.clear(); lcd.setCursor(0, 0); lcd.print(b1);
  if (b2[0]) { lcd.setCursor(0, 1); lcd.print(b2); }
#endif
  Serial.printf("[layar] %s | %s\n", b1, b2);
}

void matikanI2S() {
  if (micSiap) { i2s_driver_uninstall(PORT_I2S); micSiap = false; }
  if (ampSiap) { i2s_driver_uninstall(PORT_I2S); ampSiap = false; }
}

void siapkanMic() {
  matikanI2S();
  i2s_config_t cfg = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
      .sample_rate = (uint32_t)LAJU_SAMPEL,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,     // INMP441 mengirim 32 bit
      .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
      .communication_format = I2S_COMM_FORMAT_STAND_I2S,
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = 8, .dma_buf_len = 256, .use_apll = false,
  };
  i2s_pin_config_t pin = {.bck_io_num = MIC_SCK, .ws_io_num = MIC_WS,
                          .data_out_num = I2S_PIN_NO_CHANGE, .data_in_num = MIC_SD};
  i2s_driver_install(PORT_I2S, &cfg, 0, nullptr);
  i2s_set_pin(PORT_I2S, &pin);
  i2s_zero_dma_buffer(PORT_I2S);
  micSiap = true;
}

void siapkanAmp() {
  matikanI2S();
  i2s_config_t cfg = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
      .sample_rate = (uint32_t)LAJU_SAMPEL,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
      .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
      .communication_format = I2S_COMM_FORMAT_STAND_I2S,
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = 8, .dma_buf_len = 256, .use_apll = false,
  };
  i2s_pin_config_t pin = {.bck_io_num = AMP_BCLK, .ws_io_num = AMP_LRC,
                          .data_out_num = AMP_DIN, .data_in_num = I2S_PIN_NO_CHANGE};
  i2s_driver_install(PORT_I2S, &cfg, 0, nullptr);
  i2s_set_pin(PORT_I2S, &pin);
  ampSiap = true;
}

void tulisHeaderWav(uint8_t *b, size_t panjangData) {
  uint32_t total = panjangData + 36, lajuByte = LAJU_SAMPEL * 2;
  auto t32 = [&](int o, uint32_t v) { memcpy(b + o, &v, 4); };
  auto t16 = [&](int o, uint16_t v) { memcpy(b + o, &v, 2); };
  memcpy(b, "RIFF", 4); t32(4, total); memcpy(b + 8, "WAVEfmt ", 8);
  t32(16, 16); t16(20, 1); t16(22, 1); t32(24, LAJU_SAMPEL);
  t32(28, lajuByte); t16(32, 2); t16(34, 16);
  memcpy(b + 36, "data", 4); t32(40, panjangData);
}

// ------------------------------ REKAM ------------------------------
size_t rekam() {
  siapkanMic();
  int16_t *sampel = (int16_t *)(wav + 44);
  size_t terkumpul = 0;
  int32_t buf32[256];

  while (digitalRead(PIN_TOMBOL) == LOW && terkumpul < MAKS_SAMPEL) {
    size_t dibaca = 0;
    if (i2s_read(PORT_I2S, buf32, sizeof(buf32), &dibaca, pdMS_TO_TICKS(200)) != ESP_OK) break;
    size_t n = dibaca / sizeof(int32_t);
    for (size_t i = 0; i < n && terkumpul < MAKS_SAMPEL; i++)
      sampel[terkumpul++] = (int16_t)(buf32[i] >> 14);        // 32 bit -> 16 bit
  }
  Serial.printf("rekam: %.1f detik\n", (float)terkumpul / LAJU_SAMPEL);
  return terkumpul * 2;
}

// ------------------------------ PUTAR ------------------------------
void putarDariServer(const String &url) {
  siapkanAmp();
  HTTPClient http;
  http.begin(url);
  http.setTimeout(20000);
  int kode = http.GET();
  if (kode != 200) {
    Serial.printf("gagal ambil suara: %d\n", kode); http.end(); return;
  }
  WiFiClient *aliran = http.getStreamPtr();
  uint8_t header[44];
  size_t dapat = aliran->readBytes(header, 44);              // buang header WAV
  Serial.printf("memutar %s (header %u byte)\n", url.c_str(), (unsigned)dapat);

  size_t n;
  while (aliran->connected() || aliran->available()) {
    n = aliran->readBytes(bufPutar, 2048);
    if (!n) break;
    size_t ditulis = 0;
    i2s_write(PORT_I2S, bufPutar, n, &ditulis, portMAX_DELAY);
    if (!ditulis) break;
  }
  http.end();
  i2s_zero_dma_buffer(PORT_I2S);
}

// ------------------------------ KIRIM KE SERVER ------------------------------
bool kirimDanPutar(size_t panjangData) {
  tulisHeaderWav(wav, panjangData);
  HTTPClient http;
  http.begin(String(SERVER) + "/terjemah");
  http.setTimeout(30000);  // 30 detik timeout
  http.addHeader("Content-Type", "audio/wav");
  int kode = http.POST(wav, panjangData + 44);
  if (kode != 200) {
    Serial.printf("server menjawab %d: %s\n", kode, http.getString().c_str());
    http.end(); return false;
  }
  String balasan = http.getString();
  http.end();

  DynamicJsonDocument doc(1024);                           // ArduinoJson 6
  if (deserializeJson(doc, balasan)) { Serial.println("balasan tidak terbaca"); return false; }

  const char *asli = doc["asli"] | "";
  const char *terj = doc["terjemahan"] | "";
  const char *urlSuara = doc["audio_url"] | "";
  Serial.printf("asli: %s\nterjemahan: %s\ntotal: %.2f detik\n",
                asli, terj, (float)(doc["total"] | 0.0));
  tampil(String(asli).substring(0, 16).c_str(), String(terj).substring(0, 16).c_str());

  if (!urlSuara[0]) return false;
  setLed(true);                                // LED menyala saat memutar suara
  putarDariServer(String(SERVER) + urlSuara);
  setLed(false);
  return true;
}

// ------------------------------ UTAMA ------------------------------
void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(PIN_TOMBOL, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  setLed(false);

#if PAKAI_LCD
  Wire.begin(21, 22);
  lcd.init(); lcd.backlight();
#endif
  tampil("Alat penerjemah", "menyambung WiFi");

  wav = (uint8_t *)malloc(UKURAN_WAV);
  bufPutar = (uint8_t *)malloc(2048);
  Serial.printf("Buffer rekaman: %.0f KB (Free Heap: %d KB, Max Block: %d KB)\n", 
                UKURAN_WAV / 1024.0, ESP.getFreeHeap() / 1024, ESP.getMaxAllocHeap() / 1024);
  if (!wav || !bufPutar) {
    tampil("Memori kurang", "kurangi durasi");
  } else {
    Serial.println("Alokasi buffer WAV: BERHASIL!");
  }

  WiFi.mode(WIFI_STA);
  // Daftar AP portabel (Hotspot HP tim, WiFi Kampus & Simulator Wokwi)
  wifiMulti.addAP("Penerjemah_Hotspot", "12345678");
  wifiMulti.addAP("Hotspot_Jian", "12345678");
  wifiMulti.addAP("Hotspot_Haikal", "12345678");
  wifiMulti.addAP("Politani_Samarinda_University", "");
  wifiMulti.addAP("Wokwi-GUEST", "");

  Serial.println("Mencari jaringan WiFi portabel...");
  tampil("Mencari WiFi...", "Hotspot / Kampus");

  uint32_t t0 = millis();
  while (wifiMulti.run() != WL_CONNECTED && millis() - t0 < 15000) {
    setLed(true);
    delay(150);
    setLed(false);
    delay(150);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("WiFi Tersambung! SSID: %s | IP: %s\n", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());
    // Indikasi LED berkedip 2x: Sistem Siap
    kedipLed(2, 200, 100);
    tampil("WiFi tersambung", "Tahan tombol");
  } else {
    Serial.println("WiFi gagal terhubung");
    tampil("WiFi gagal", "Cek Hotspot HP");
    // Indikasi LED berkedip 5x cepat: Gagal koneksi
    kedipLed(5, 80, 80);
  }
}

void loop() {
  // Jaga koneksi WiFi tetap terhubung secara otomatis di background
  wifiMulti.run();

  if (digitalRead(PIN_TOMBOL) == LOW) {
    setLed(true);                              // LED menyala stabil saat merekam
    tampil("Merekam...", "lepas utk kirim");
    size_t panjang = rekam();
    setLed(false);

    if (panjang < LAJU_SAMPEL) {                   // kurang dari 1 detik
      tampil("Terlalu pendek", "coba lagi");
      delay(600); tampil("Siap", "Tahan tombol");
      return;
    }
    tampil("Memproses...", "mohon tunggu");
    // Kedip cepat menandakan sedang proses kirim dan terjemah di server
    kedipLed(3, 80, 60);

    if (!kirimDanPutar(panjang)) {
      tampil("Gagal", "cek laptop/WiFi");
      kedipLed(4, 100, 100);
      delay(1200);
    }
    tampil("Selesai", "Tahan tombol");
  }
  delay(20);
}
