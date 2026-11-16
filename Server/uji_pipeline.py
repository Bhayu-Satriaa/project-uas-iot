"""Uji pipeline dari terminal, tanpa mikropon dan tanpa board.

Contoh:
    python3 uji_pipeline.py --teks "Selamat pagi, berapa harga ini?" --arah id-en
    python3 uji_pipeline.py --berkas sampel_audio/frasa_id_1.wav --arah id-en
    python3 uji_pipeline.py --teks "How much is this?" --arah en-id --keluaran luar.mp3
"""
import argparse
import base64
import pathlib
import sys

import pipeline
from konfigurasi import DIR_SAMPEL


def main():
    p = argparse.ArgumentParser(description="Uji pipeline penerjemah")
    p.add_argument("--arah", default="id-en", choices=["id-en", "en-id"])
    p.add_argument("--teks", help="uji tanpa pengenal suara (langsung ke terjemah)")
    p.add_argument("--berkas", help="berkas audio untuk diuji pengenal suaranya")
    p.add_argument("--keluaran", default=None, help="berkas MP3 hasil (opsional)")
    a = p.parse_args()

    if not a.teks and not a.berkas:
        p.error("isi salah satu: --teks atau --berkas")

    if a.berkas and not pipeline.stt_siap():
        print("Catatan: pengenal suara lokal belum terpasang, tahap STT akan gagal.\n"
              "Pakai --teks untuk menguji terjemah + suara saja.\n")

    hasil = pipeline.proses(arah=a.arah, teks=a.teks, berkas_audio=a.berkas)

    print("=" * 62)
    print(f"arah        : {hasil['arah']}")
    print(f"teks asli   : {hasil['asli']}")
    print(f"terjemahan  : {hasil['terjemahan']}")
    print(f"ukuran audio: {hasil['ukuran_audio']:,} byte MP3")
    print("-" * 62)
    for tahap, detik in hasil["waktu"].items():
        print(f"  {tahap:10s}: {detik:>6.2f} detik")
    print(f"  {'TOTAL':10s}: {hasil['total']:>6.2f} detik")
    print("=" * 62)

    keluar = pathlib.Path(a.keluaran) if a.keluaran else (
        DIR_SAMPEL / f"hasil_{a.arah}.mp3")
    keluar.parent.mkdir(parents=True, exist_ok=True)
    keluar.write_bytes(base64.b64decode(hasil["audio_b64"]))
    print("berkas suara hasil:", keluar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
