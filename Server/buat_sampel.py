"""Buat audio contoh (bahasa Indonesia & Inggris) untuk bahan uji.

Kegunaan: menguji tahap pengenal suara tanpa harus merekam dengan mikropon.
Hasilnya disimpan di sampel_audio/ sebagai MP3.

Jalankan:
    python3 buat_sampel.py
"""
import pathlib

import pipeline
from konfigurasi import DIR_SAMPEL

FRASA_ID = [
    "Selamat pagi, berapa harga ini?",
    "Bisa kurang sedikit, Pak?",
    "Saya mau beli dua kilogram.",
    "Di mana tempat parkir terdekat?",
    "Terima kasih banyak, sampai jumpa.",
]

FRASA_EN = [
    "Good morning, how much is this?",
    "Can you give me a better price?",
    "Where is the nearest parking area?",
]


def main():
    DIR_SAMPEL.mkdir(parents=True, exist_ok=True)
    dibuat = 0
    for i, kalimat in enumerate(FRASA_ID, 1):
        berkas = DIR_SAMPEL / f"frasa_id_{i}.mp3"
        berkas.write_bytes(pipeline.buat_suara(kalimat, "id"))
        print(f"  {berkas.name}  <- {kalimat}")
        dibuat += 1
    for i, kalimat in enumerate(FRASA_EN, 1):
        berkas = DIR_SAMPEL / f"frasa_en_{i}.mp3"
        berkas.write_bytes(pipeline.buat_suara(kalimat, "en"))
        print(f"  {berkas.name}  <- {kalimat}")
        dibuat += 1
    print(f"\nselesai: {dibuat} berkas di {DIR_SAMPEL}")


if __name__ == "__main__":
    main()
