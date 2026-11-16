"""Konfigurasi server penerjemah.

PENTING: berkas ini TIDAK menyimpan kunci API. Kunci dibaca dari:
  1) variabel lingkungan GATEWAY_KEY
  2) ~/.hermes/.env  (variabel HERMES_CUSTOM_172_26_96_1_20128_API_KEY)
"""
import os
import pathlib
import subprocess

NAMA_VAR_KUNCI = "HERMES_CUSTOM_172_26_96_1_20128_API_KEY"


def _dari_env_file(nama):
    for p in [pathlib.Path.home() / ".hermes/.env", pathlib.Path.home() / ".env"]:
        if p.exists():
            for baris in p.read_text().splitlines():
                if "=" in baris and not baris.strip().startswith("#"):
                    k, v = baris.split("=", 1)
                    if k.strip() == nama:
                        return v.strip().strip('"').strip("'")
    return None


def ip_host_windows():
    """9Router berjalan di Windows; dari WSL dibutuhkan IP host-nya."""
    if os.name == "nt":
        return "127.0.0.1"
    try:
        out = subprocess.run(
            ["bash", "-lc", "ip route | grep default | awk '{print $3}'"],
            capture_output=True, text=True, timeout=5).stdout.strip().splitlines()
        if out:
            return out[0]
    except Exception:
        pass
    return "127.0.0.1"


GATEWAY_URL = os.getenv("GATEWAY_URL") or f"http://{ip_host_windows()}:20128"
GATEWAY_KEY = (os.getenv("GATEWAY_KEY")
               or os.getenv(NAMA_VAR_KUNCI)
               or _dari_env_file(NAMA_VAR_KUNCI))

# Model & suara (bisa diubah lewat variabel lingkungan)
MODEL_TERJEMAH = os.getenv("MODEL_TERJEMAH", "cmc/deepseek/deepseek-v4-flash")
SUARA = {
    "id": os.getenv("SUARA_ID", "id-ID-GadisNeural"),
    "en": os.getenv("SUARA_EN", "en-US-AriaNeural"),
}
BAHASA = {"id": "Indonesian", "en": "English"}
MODEL_STT = os.getenv("MODEL_STT", "small")   # ukuran model faster-whisper

# Lokasi berkas
DIR_SERVER = pathlib.Path(__file__).resolve().parent
DIR_SAMPEL = DIR_SERVER / "sampel_audio"
DIR_SUARA = DIR_SERVER / "suara_hasil"
BERKAS_RIWAYAT = DIR_SERVER / "riwayat.jsonl"
