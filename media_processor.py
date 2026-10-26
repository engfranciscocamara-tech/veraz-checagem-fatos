"""
Processador local de Áudio e Vídeo para o Bot Verificador Eleitoral.
Extrai áudio otimizado, transcreve falas com timestamps (via faster-whisper ou Gemini)
e captura frames-chave (keyframes) de vídeos para leitura de legendas e elementos visuais na tela.
"""

import io
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import imageio_ffmpeg
from PIL import Image

_WHISPER_MODEL = None


def get_whisper_model(model_size: str = "base"):
    """Carrega o modelo faster-whisper sob demanda com cache em memória."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        from faster_whisper import WhisperModel
        _WHISPER_MODEL = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _WHISPER_MODEL


def extract_audio_mp3_bytes(input_media_path: str, max_duration_sec: int = 300) -> Optional[bytes]:
    """
    Extrai a faixa de áudio de um arquivo de vídeo ou áudio em formato MP3 mono leve (32kbps, 16kHz),
    ideal para envio rápido à API Gemini ou transcrição local.
    """
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_out:
        out_path = tmp_out.name

    try:
        cmd = [
            ffmpeg_exe,
            "-y",
            "-i",
            input_media_path,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-b:a",
            "32k",
            "-t",
            str(max_duration_sec),
            out_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            return Path(out_path).read_bytes()
    except Exception:
        return None
    finally:
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                pass
    return None


def transcribe_media_locally(input_media_path: str) -> str:
    """
    Transcreve o áudio de um arquivo de áudio ou vídeo localmente com faster-whisper,
    incluindo marcações de tempo [MM:SS] para cada trecho.
    """
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        wav_path = tmp_wav.name

    try:
        cmd = [
            ffmpeg_exe,
            "-y",
            "-i",
            input_media_path,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            wav_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        model = get_whisper_model("base")
        segments, _ = model.transcribe(wav_path, language="pt", beam_size=5)

        lines = []
        for seg in segments:
            mins = int(seg.start // 60)
            secs = int(seg.start % 60)
            text = (seg.text or "").strip()
            if text:
                lines.append(f"[{mins:02d}:{secs:02d}] {text}")

        return "\n".join(lines).strip()
    except Exception:
        return ""
    finally:
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except OSError:
                pass


def extract_video_keyframes(input_video_path: str, max_frames: int = 6) -> List[bytes]:
    """
    Extrai até `max_frames` quadros distribuídos ao longo do vídeo em formato JPEG compacto,
    permitindo ao modelo ler textos sobrepostos na tela (ex: manchetes, listas de impostos, legendas).
    """
    frames_bytes: List[bytes] = []
    try:
        import av

        container = av.open(input_video_path)
        video_stream = next((s for s in container.streams if s.type == "video"), None)
        if video_stream is None:
            container.close()
            return []

        all_pil_frames: List[Image.Image] = []
        # Decodifica apenas keyframes (quadros-chave) para ser instantâneo
        video_stream.codec_context.skip_frame = "NONKEY"
        for frame in container.decode(video_stream):
            img = frame.to_image()
            all_pil_frames.append(img)
            if len(all_pil_frames) >= 60:
                break

        container.close()

        if not all_pil_frames:
            return []

        # Seleciona até max_frames uniformemente espaçados
        total = len(all_pil_frames)
        if total <= max_frames:
            selected = all_pil_frames
        else:
            indices = [int(i * (total - 1) / (max_frames - 1)) for i in range(max_frames)]
            selected = [all_pil_frames[idx] for idx in indices]

        for img in selected:
            img_copy = img.copy()
            img_copy.thumbnail((720, 720))
            buf = io.BytesIO()
            img_copy.convert("RGB").save(buf, format="JPEG", quality=78)
            frames_bytes.append(buf.getvalue())

    except Exception:
        pass

    return frames_bytes
