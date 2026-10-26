"""
Servidor Web do Veraz — Bot Verificador de Notícias e Mídias Eleitorais.
Aceita mensagens de texto, áudio e vídeo e retorna análise ponto a ponto com fontes e datas.
A chave da API é lida exclusivamente no servidor via arquivo .env (protegido pelo .gitignore).
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import Body, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from fact_checker import ElectionFactChecker
from pdf_exporter import render_pdf_bytes
from sample_cases import SAMPLE_MESSAGES

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Veraz | Checagem Ponto a Ponto",
    description="Bot verificador de texto, áudio e vídeo inspirado no Fato ou Fake, Agência Lupa e Aos Fatos.",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/samples")
async def get_samples():
    return {
        "samples": [
            {
                "id": s["id"],
                "titulo": s["titulo"],
                "texto_entrada": s["texto_entrada"],
            }
            for s in SAMPLE_MESSAGES
        ]
    }


@app.get("/api/sample/{sample_id}")
async def get_sample_result(sample_id: str):
    for item in SAMPLE_MESSAGES:
        if item["id"] == sample_id:
            return item
    raise HTTPException(status_code=404, detail="Exemplo não encontrado.")


@app.post("/api/verify")
async def verify_message(
    text_message: Optional[str] = Form(default=None),
    media_file: Optional[UploadFile] = File(default=None),
):
    load_dotenv(override=True)
    effective_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not effective_key and text_message:
        for sample in SAMPLE_MESSAGES:
            if sample["texto_entrada"].strip() == text_message.strip():
                return JSONResponse(content=sample["resultado_demo"])

    media_bytes: Optional[bytes] = None
    media_filename: Optional[str] = None
    media_mime: Optional[str] = None

    if media_file is not None and media_file.filename:
        media_bytes = await media_file.read()
        media_filename = media_file.filename
        media_mime = media_file.content_type

    try:
        checker = ElectionFactChecker(api_key=effective_key)
        result = checker.verify_content(
            text_message=text_message,
            media_bytes=media_bytes,
            media_filename=media_filename,
            media_mime_type=media_mime,
        )
        return JSONResponse(content=result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível concluir a verificação da mídia no momento. Tente novamente em instantes.",
        )


@app.post("/api/export-pdf")
async def export_verification_pdf(payload: Dict[str, Any] = Body(...)):
    try:
        pdf_bytes = render_pdf_bytes(payload)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="veraz-checagem-ponto-a-ponto.pdf"'
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(exc)}")


if __name__ == "__main__":
    print("Iniciando Veraz em http://127.0.0.1:8000 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
