"""Server penerjemah - versi sederhana (satu tombol, tanpa musik).

Alur yang dipakai alat:
    1. tombol ditekan-tahan -> ESP32 merekam suara
    2. tombol dilepas       -> ESP32 kirim audio ke POST /terjemah
    3. server              -> pengenal suara -> terjemah -> suara
    4. ESP32 memutar MP3 dari alamat yang dikembalikan (audio_url)

Cara menjalankan:
    python3 server_terjemah.py            # port 8000

Endpoint:
    GET  /sehat                            status server + kesiapan pengenal suara
    POST /terjemah?arah=id-en              body: audio WAV mentah  (dari ESP32)
    POST /terjemah?teks=Selamat+pagi       uji tanpa mikropon (arah otomatis bila kosong)
    GET  /audio/<nama>.mp3                 berkas suara hasil (diputar ESP32)
    GET  /riwayat                          20 percakapan terakhir
"""
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse

import pipeline
from konfigurasi import (BERKAS_RIWAYAT, DIR_SERVER, DIR_SUARA, GATEWAY_URL,
                         MODEL_STT, MODEL_TERJEMAH)

app = FastAPI(title="Server Penerjemah - satu tombol", version="2.0")


@app.get("/sehat")
def sehat():
    return {
        "status": "ok",
        "gateway": GATEWAY_URL,
        "model_terjemah": MODEL_TERJEMAH,
        "pengenal_suara_lokal": pipeline.stt_siap(),
        "model_pengenal_suara": MODEL_STT if pipeline.stt_siap() else None,
    }


@app.post("/terjemah")
async def terjemah(request: Request, arah: str | None = None, teks: str | None = None):
    if arah not in (None, "id-en", "en-id"):
        raise HTTPException(400, "arah harus 'id-en', 'en-id', atau dikosongkan (otomatis)")

    if teks:
        return JSONResponse(pipeline.proses(arah=arah, teks=teks))

    audio_masuk = await request.body()
    if not audio_masuk:
        raise HTTPException(400, "body audio kosong; kirim WAV atau pakai parameter teks")

    berkas = DIR_SERVER / "masuk.wav"
    berkas.write_bytes(audio_masuk)
    try:
        return JSONResponse(pipeline.proses(arah=arah, berkas_audio=str(berkas)))
    except RuntimeError as e:
        raise HTTPException(503, str(e))


@app.get("/suara/{nama}")
def suara(nama: str):
    berkas = DIR_SUARA / nama
    if not berkas.exists() or berkas.suffix not in (".mp3", ".wav"):
        raise HTTPException(404, "berkas suara tidak ditemukan")
    jenis = "audio/wav" if berkas.suffix == ".wav" else "audio/mpeg"
    return FileResponse(berkas, media_type=jenis)


@app.get("/riwayat")
def riwayat(batas: int = 20):
    if not BERKAS_RIWAYAT.exists():
        return {"jumlah": 0, "data": []}
    baris = BERKAS_RIWAYAT.read_text(encoding="utf-8").strip().splitlines()
    data = [json.loads(b) for b in baris[-batas:]]
    return {"jumlah": len(data), "data": data}


@app.get("/monitor", response_class=HTMLResponse)
def halaman_monitor():
    berkas = DIR_SERVER / "templates" / "monitor.html"
    if not berkas.exists():
        raise HTTPException(404, "Berkas template monitor.html tidak ditemukan")
    return HTMLResponse(content=berkas.read_text(encoding="utf-8"))


@app.get("/", response_class=PlainTextResponse)
def akar():
    return ("Server penerjemah (satu tombol) aktif.\n"
            "Dashboard : GET /monitor\n"
            "Status    : GET /sehat\n"
            "Uji cepat : POST /terjemah?teks=Selamat%20pagi%2C%20berapa%20harga%20ini\n"
            "Dari alat : POST /terjemah  (body audio WAV)\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
