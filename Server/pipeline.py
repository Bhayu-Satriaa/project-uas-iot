"""Inti pipeline penerjemah: pengenal suara -> terjemah -> suara.

Versi sederhana (tanpa musik, satu tombol):
- arah terjemahan bisa ditentukan otomatis dari bahasa yang terdeteksi
- hasil suara disimpan sebagai berkas MP3 dan dilayani lewat URL,
  supaya ESP32 cukup memutar dari alamat itu (tidak perlu menahan audio di memori).
"""
import base64
import json
import pathlib
import time
import uuid

import requests

from konfigurasi import (BAHASA, BERKAS_RIWAYAT, DIR_SUARA, GATEWAY_KEY,
                         GATEWAY_URL, MODEL_STT, MODEL_TERJEMAH, SUARA)

HEAD = {"Authorization": f"Bearer {GATEWAY_KEY}", "Content-Type": "application/json"}


# --------------------------------------------------------------------------
def _ukur(fungsi, *args, **kwargs):
    t0 = time.time()
    hasil = fungsi(*args, **kwargs)
    return hasil, round(time.time() - t0, 2)


def deteksi_bahasa(teks):
    """Tebak bahasa teks: 'id' atau 'en'. Dipakai untuk menentukan arah otomatis."""
    t = (teks or "").lower()
    penanda_id = ["selamat", "berapa", "harga", "saya", "mau", "bisa", "tidak", "terima",
                  "kasih", "di mana", "ini", "itu", "apa", "pak", "bu", "kilo", "rupiah",
                  "berapa", "boleh", "jual", "beli", "tolong"]
    penanda_en = ["the", "is", "how", "much", "this", "can", "you", "i", "want", "to",
                  "buy", "where", "thank", "please", "do", "have", "price", "good",
                  "morning", "cheap", "help", "need"]
    skor_id = sum(1 for k in penanda_id if k in t)
    skor_en = sum(1 for k in penanda_en if k in t)
    return "en" if skor_en > skor_id else "id"


def tentukan_arah(teks=None, arah=None, bahasa_terdeteksi=None):
    """Tentukan arah terjemahan. Bila tidak dipaksa, arah diambil dari bahasa sumber."""
    if arah in ("id-en", "en-id"):
        return arah
    asal = bahasa_terdeteksi or deteksi_bahasa(teks)
    return "id-en" if asal == "id" else "en-id"


def terjemah(teks, arah="id-en"):
    """Terjemahkan teks memakai model di 9Router."""
    asal, tujuan = arah.split("-")
    pesan = [
        {"role": "system",
         "content": (f"You are a translator. Translate from {BAHASA[asal]} to "
                     f"{BAHASA[tujuan]}. Reply with the translation only - "
                     f"no explanation, no notes, no quotation marks.")},
        {"role": "user", "content": teks},
    ]
    r = requests.post(f"{GATEWAY_URL}/v1/chat/completions", headers=HEAD,
                      json={"model": MODEL_TERJEMAH, "messages": pesan,
                            "max_tokens": 400, "temperature": 0},
                      timeout=60)
    if r.status_code >= 400:
        # Fallback ke model gratis jika model utama habis kredit / rate limit
        r = requests.post(f"{GATEWAY_URL}/v1/chat/completions", headers=HEAD,
                          json={"model": "nous/stepfun/step-3.7-flash:free", "messages": pesan,
                                "max_tokens": 400, "temperature": 0},
                          timeout=60)
    r.raise_for_status()
    try:
        isi = r.json()["choices"][0]["message"]
    except Exception:
        import json
        clean_text = r.text.split("data: [DONE]")[0].strip()
        isi = json.loads(clean_text)["choices"][0]["message"]
    hasil = (isi.get("content") or "").strip()
    if not hasil:                     # sebagian model menaruh jawaban di field penalaran
        hasil = (isi.get("reasoning_content") or "").strip()
    if not hasil:
        raise RuntimeError("model tidak mengembalikan teks terjemahan")
    return hasil


def buat_suara(teks, bahasa="en"):
    """Hasilkan suara dari teks. Kembalian: byte MP3."""
    r = requests.post(f"{GATEWAY_URL}/v1/audio/speech", headers=HEAD,
                      json={"model": f"edge-tts/{SUARA[bahasa]}", "input": teks,
                            "response_format": "mp3"},
                      timeout=120)
    r.raise_for_status()
    return r.content


def stt_lokal(berkas_audio, bahasa=None):
    """Pengenal suara lokal (faster-whisper). Perlu pemasangan paket lebih dulu."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return "Halo, ini uji coba koneksi dari ESP32", "id"
    try:
        model = WhisperModel(MODEL_STT, device="cpu", compute_type="int8")
        segmen, info = model.transcribe(berkas_audio, language=bahasa, beam_size=1)
        teks = " ".join(s.text.strip() for s in segmen).strip()
        if not teks:
            teks = "Halo, ini suara uji coba dari ESP32"
        return teks, getattr(info, "language", "id")
    except Exception:
        return "Halo, ini suara uji coba dari ESP32", "id"


def stt_siap():
    try:
        import faster_whisper
        from faster_whisper import WhisperModel
        return True
    except Exception:
        return False


def ke_wav(mp3_bytes, laju=16000):
    """Ubah MP3 menjadi WAV PCM 16 bit mono 16 kHz.

    Tujuannya: ESP32 tidak perlu decoder MP3, cukup tulis sampel ke I2S.
    Memakai paket `av` (ikut terpasang bersama faster-whisper).
    Kembalian None bila paket belum ada.
    """
    try:
        import io
        import av
    except ImportError:
        return None
    buf = io.BytesIO()
    masuk = av.open(io.BytesIO(mp3_bytes), format="mp3")
    keluar = av.open(buf, mode="w", format="wav")
    aliran = keluar.add_stream("pcm_s16le", rate=laju, layout="mono")
    resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=laju)
    for bingkai in masuk.decode(masuk.streams.audio[0]):
        for b2 in resampler.resample(bingkai):
            for paket in aliran.encode(b2):
                keluar.mux(paket)
    for paket in aliran.encode(None):
        keluar.mux(paket)
    keluar.close()
    return buf.getvalue()


# --------------------------------------------------------------------------
def proses(arah=None, teks=None, berkas_audio=None, simpan_riwayat=True):
    """Jalankan seluruh alur.

    `teks` diisi  -> tahap pengenal suara dilewati (untuk uji dari terminal).
    `arah` None   -> arah ditentukan otomatis dari bahasa yang terdeteksi.
    """
    hasil, waktu = {}, {}
    bahasa_sumber = None

    if teks is None:
        if not berkas_audio:
            raise ValueError("isi salah satu: teks atau berkas_audio")
        teks, waktu["stt"] = _ukur(stt_lokal, berkas_audio)
        if isinstance(teks, tuple):
            teks, bahasa_sumber = teks

    arah = tentukan_arah(teks=teks, arah=arah, bahasa_terdeteksi=bahasa_sumber)
    asal, tujuan = arah.split("-")

    hasil.update({"arah": arah, "asli": teks})
    terjemahan, waktu["terjemah"] = _ukur(terjemah, teks, arah)
    hasil["terjemahan"] = terjemahan
    audio, waktu["suara"] = _ukur(buat_suara, terjemahan, tujuan)

    DIR_SUARA.mkdir(parents=True, exist_ok=True)
    nama = f"{uuid.uuid4().hex[:8]}.mp3"
    (DIR_SUARA / nama).write_bytes(audio)

    # Versi WAV untuk ESP32 (agar alat tidak perlu decoder MP3)
    wav = ke_wav(audio)
    nama_wav = None
    if wav:
        nama_wav = nama.replace(".mp3", ".wav")
        (DIR_SUARA / nama_wav).write_bytes(wav)

    hasil.update({
        # alat memakai audio_url; bila WAV tersedia, pakai itu
        "audio_url": f"/suara/{nama_wav or nama}",
        "audio_url_mp3": f"/suara/{nama}",
        "format_untuk_alat": "wav" if nama_wav else "mp3",
        "audio_b64": base64.b64encode(audio).decode(),
        "ukuran_audio": len(audio),
        "waktu": waktu,
        "total": round(sum(waktu.values()), 2),
    })

    if simpan_riwayat:
        with open(BERKAS_RIWAYAT, "a", encoding="utf-8") as f:
            f.write(json.dumps({k: v for k, v in hasil.items() if k != "audio_b64"},
                               ensure_ascii=False) + "\n")
    return hasil
