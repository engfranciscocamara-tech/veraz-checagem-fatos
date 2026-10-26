"""
Motor de verificação de fatos multimodal (Texto, Áudio e Vídeo) com Google Gemini,
otimização de mídia (extração de áudio leve + keyframes de vídeo + transcrição)
e busca jornalística em tempo real nas agências de checagem, órgãos oficiais (IBGE, TSE, BCB) e imprensa.
"""

import json
import mimetypes
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from media_processor import (
    extract_audio_mp3_bytes,
    extract_video_keyframes,
    transcribe_media_locally,
)
from prompts import get_system_prompt
from web_search_helper import (
    ensure_functional_source_url,
    search_fact_checks_for_queries,
)

load_dotenv()

SUPPORTED_AUDIO_MIMES = {
    ".mp3": "audio/mp3",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".opus": "audio/ogg",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".webm": "audio/webm",
}

SUPPORTED_VIDEO_MIMES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".avi": "video/x-msvideo",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpeg",
    ".mkv": "video/x-matroska",
}

FALLBACK_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemma-4-31b-it",
]


def detect_mime_type(filename: str, fallback_mime: Optional[str] = None) -> str:
    ext = Path(filename).suffix.lower()
    if ext in SUPPORTED_VIDEO_MIMES:
        return SUPPORTED_VIDEO_MIMES[ext]
    if ext in SUPPORTED_AUDIO_MIMES:
        return SUPPORTED_AUDIO_MIMES[ext]
    if fallback_mime and fallback_mime != "application/octet-stream":
        return fallback_mime
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"


def normalize_classification(raw_status: str) -> str:
    """Padroniza a classificação em REAL, PARCIALMENTE VERDADE ou MENTIRA."""
    val = (raw_status or "").strip().upper()
    if any(k in val for k in ["PARCIAL", "IMPRECIS", "CONTEXTO", "EXAGER", "INCOMPLET", "NÃO É BEM ASSIM", "ENGANOS"]):
        return "PARCIALMENTE VERDADE"
    if any(k in val for k in ["MENTIRA", "FAKE", "FALSO", "FALSA", "BOATO", "MONTAGEM"]):
        return "MENTIRA"
    if any(k in val for k in ["REAL", "VERDADE", "FATO", "CORRET", "CERTO"]):
        return "REAL"
    return "PARCIALMENTE VERDADE"


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extrai o objeto JSON da resposta do modelo mesmo se vier envolto em blocos markdown."""
    cleaned = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1)
    else:
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            cleaned = cleaned[first_brace : last_brace + 1]

    return json.loads(cleaned)


def build_whatsapp_summary(result: Dict[str, Any]) -> str:
    """Gera um texto formatado pronto para compartilhamento no WhatsApp, incluindo links das fontes."""
    lines = [
        "*🔎 CHECAGEM PONTO A PONTO (Veraz)*",
        f"📌 *Panorama:* {result.get('panorama_veredito', 'Análise concluída')}",
        "",
    ]

    icons = {
        "REAL": "🟢 *VERDADEIRO (REAL)*",
        "PARCIALMENTE VERDADE": "🟡 *PARCIALMENTE VERDADE*",
        "MENTIRA": "🔴 *FALSO (MENTIRA)*",
    }

    for pt in result.get("pontos", []):
        status = normalize_classification(pt.get("classificacao", ""))
        badge = icons.get(status, f"⚪ *{status}*")
        lines.append(f"*{pt.get('numero', 1)}. \"{pt.get('afirmacao_original', '')}\"*")
        lines.append(f"Veredito: {badge}")
        lines.append(f"✅ *A verdade:* {pt.get('informacao_verdadeira', '')}")

        fontes = pt.get("fontes", [])
        if fontes:
            lines.append("📚 *Fontes:*")
            for f in fontes[:4]:
                nome = f.get("nome", "Fonte")
                dt = f.get("data", "Recente")
                url = f.get("url", "")
                if url:
                    lines.append(f"• {nome} ({dt}): {url}")
                else:
                    lines.append(f"• {nome} ({dt})")
        lines.append("")

    lines.append(
        "⚖️ *Atenção:* Criar ou espalhar fake news é crime previsto no Código Eleitoral (arts. 323 e 326-A) e no Código Penal (arts. 138 a 140)."
    )
    return "\n".join(lines).strip()


class ElectionFactChecker:
    """Cliente de checagem de fatos eleitorais com suporte a texto, áudio e vídeo."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.5-flash"):
        load_dotenv(override=True)
        self.api_key = (
            (api_key or "").strip()
            or os.getenv("GEMINI_API_KEY", "").strip()
            or os.getenv("GOOGLE_API_KEY", "").strip()
        )
        if not model_name or "2.5" in model_name or "2.0" in model_name or "1.5" in model_name:
            self.model_name = "gemini-3.5-flash"
        else:
            self.model_name = model_name

    def _get_model_candidates(self) -> List[str]:
        candidates = [self.model_name]
        for m in FALLBACK_MODELS:
            if m not in candidates:
                candidates.append(m)
        return candidates

    def _generate_with_fallback(
        self,
        client: genai.Client,
        contents: List[Any],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> str:
        last_err = None
        for model_id in self._get_model_candidates():
            try:
                cfg = types.GenerateContentConfig(temperature=temperature)
                if system_instruction and not model_id.startswith("gemma"):
                    cfg.system_instruction = system_instruction

                resp = client.models.generate_content(
                    model=model_id,
                    contents=contents,
                    config=cfg,
                )
                if resp and resp.text:
                    return resp.text
            except Exception as exc:
                last_err = exc
                continue
        raise RuntimeError(f"Não foi possível obter resposta dos modelos Gemini: {last_err}")

    def verify_content(
        self,
        text_message: Optional[str] = None,
        media_bytes: Optional[bytes] = None,
        media_filename: Optional[str] = None,
        media_mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError(
                "Serviço de verificação não configurado no servidor (variável de ambiente ausente)."
            )

        if not text_message and not media_bytes:
            raise ValueError("Envie ao menos uma mensagem de texto, um arquivo de áudio ou um vídeo para análise.")

        client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=2)
            ),
        )

        media_parts: List[Any] = []
        detected_media_kind = "texto"
        local_transcript = ""

        # 1. Processa arquivo de mídia (Áudio ou Vídeo) de forma otimizada
        if media_bytes and media_filename:
            mime = detect_mime_type(media_filename, media_mime_type)
            is_video = mime.startswith("video/") or Path(media_filename).suffix.lower() in SUPPORTED_VIDEO_MIMES
            is_audio = mime.startswith("audio/") or Path(media_filename).suffix.lower() in SUPPORTED_AUDIO_MIMES

            if is_video:
                detected_media_kind = "video" if not text_message else "multimodal"
            elif is_audio:
                detected_media_kind = "audio" if not text_message else "multimodal"

            suffix = Path(media_filename).suffix or (".mp4" if is_video else ".mp3")
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_media:
                tmp_media.write(media_bytes)
                tmp_media_path = tmp_media.name

            try:
                compressed_mp3 = extract_audio_mp3_bytes(tmp_media_path)
                if compressed_mp3:
                    media_parts.append(
                        types.Part.from_bytes(data=compressed_mp3, mime_type="audio/mp3")
                    )
                elif len(media_bytes) <= 10 * 1024 * 1024:
                    media_parts.append(
                        types.Part.from_bytes(data=media_bytes, mime_type=mime)
                    )

                if is_video:
                    keyframes = extract_video_keyframes(tmp_media_path, max_frames=6)
                    for frame_jpeg in keyframes:
                        media_parts.append(
                            types.Part.from_bytes(data=frame_jpeg, mime_type="image/jpeg")
                        )

                if not compressed_mp3:
                    local_transcript = transcribe_media_locally(tmp_media_path)
            finally:
                if os.path.exists(tmp_media_path):
                    try:
                        os.remove(tmp_media_path)
                    except OSError:
                        pass

        # 2. Passo 1: extrai transcrição e termos de busca para agências e órgãos oficiais (IBGE, BCB, TSE, etc.)
        search_queries: List[str] = []
        pre_extraction_summary = ""

        if media_parts:
            extract_prompt = (
                "Analise o áudio e os quadros do vídeo enviados.\n"
                "1) Transcreva fielmente o que é falado e todos os textos/manchetes visíveis na tela.\n"
                "2) Liste de 3 a 4 termos curtos de busca (queries jornalísticas) para verificarmos cada alegação em órgãos oficiais (IBGE, Banco Central, Tesouro Nacional, Receita Federal, TSE), imprensa e agências (Lupa, Aos Fatos, Fato ou Fake).\n"
                "Responda em JSON no formato: {\"transcricao_completa\": \"...\", \"queries_busca\": [\"query 1\", \"query 2\"]}"
            )
            try:
                raw_extract = self._generate_with_fallback(
                    client=client,
                    contents=media_parts + [extract_prompt],
                    temperature=0.1,
                )
                extracted_data = extract_json_from_text(raw_extract)
                pre_extraction_summary = extracted_data.get("transcricao_completa", "")
                search_queries = extracted_data.get("queries_busca", [])
            except Exception:
                pass

        if not search_queries and text_message:
            words = re.sub(r"[^\w\s]", " ", text_message).split()
            if words:
                search_queries = [" ".join(words[:10])]

        # 3. Busca em tempo real nas agências de checagem, dados oficiais (IBGE, BCB, TSE) e imprensa
        web_sources = search_fact_checks_for_queries(search_queries)
        web_context_lines = []
        for idx, src in enumerate(web_sources, start=1):
            web_context_lines.append(
                f"[{idx}] Veículo: {src['nome']} | Data: {src['data']} | Título: {src['titulo']} | URL: {src['url']}"
            )
        web_context_block = "\n".join(web_context_lines)

        # 4. Monta o prompt de verificação ponto a ponto
        user_prompt_parts = [
            "Analise rigorosamente o conteúdo enviado abaixo, decomponha TODAS as afirmações factuais ponto a ponto e verifique cada uma.",
            "Para cada ponto, classifique estritamente como 'REAL', 'PARCIALMENTE VERDADE' ou 'MENTIRA', explique qual é a informação verdadeira com dados exatos e cite as fontes com nome, título, data e URL funcional (incluindo órgãos oficiais de dados como IBGE, Banco Central, Tesouro Nacional, Receita Federal, TSE, além de notícias oficiais e agências de checagem).",
        ]

        if pre_extraction_summary:
            user_prompt_parts.append(
                f"\n--- TRANSCRIÇÃO E ELEMENTOS VISUAIS EXTRAÍDOS DO ÁUDIO/VÍDEO ---\n{pre_extraction_summary}\n--- FIM DA TRANSCRIÇÃO ---"
            )
        elif local_transcript:
            user_prompt_parts.append(
                f"\n--- TRANSCRIÇÃO DO ÁUDIO/VÍDEO ---\n{local_transcript}\n--- FIM DA TRANSCRIÇÃO ---"
            )

        if text_message and text_message.strip():
            user_prompt_parts.append(
                f"\n--- MENSAGEM / TEXTO ENVIADO PELO USUÁRIO ---\n{text_message.strip()}\n--- FIM DA MENSAGEM ---"
            )

        if web_context_block:
            user_prompt_parts.append(
                "\n--- CHECAGENS, DADOS OFICIAIS E REPORTAGENS ENCONTRADOS NA BUSCA EM TEMPO REAL (USE ESTAS FONTES REAIS, DATAS E URLS QUANDO PERTINENTES) ---\n"
                + web_context_block
                + "\n--- FIM DAS FONTES DE BUSCA ---"
            )

        user_prompt_parts.append(
            "\nResponda APENAS com o objeto JSON válido especificado nas instruções do sistema. Toda fonte citada DEVE ter o campo 'url' preenchido com link https:// funcional."
        )

        final_contents: List[Any] = []
        if media_parts:
            final_contents.extend(media_parts)
        final_contents.append("\n".join(user_prompt_parts))

        raw_response_text = self._generate_with_fallback(
            client=client,
            contents=final_contents,
            system_instruction=get_system_prompt(),
            temperature=0.1,
        )

        # 5. Faz o parse do JSON
        try:
            parsed = extract_json_from_text(raw_response_text)
        except Exception:
            format_text = self._generate_with_fallback(
                client=client,
                contents=[
                    "Converta a análise de checagem de fatos abaixo exatamente para o esquema JSON solicitado no sistema, preservando todos os pontos, dados reais, datas, fontes e URLs:\n\n"
                    + raw_response_text
                ],
                system_instruction=get_system_prompt(),
                temperature=0.0,
            )
            parsed = extract_json_from_text(format_text)

        # 6. Normaliza cada ponto e garante que TODAS as fontes (IBGE, BCB, TSE, imprensa, agências) tenham URL clicável funcional
        parsed["tipo_midia_analisada"] = parsed.get("tipo_midia_analisada") or detected_media_kind
        if not parsed.get("transcricao_ou_descricao") and (pre_extraction_summary or local_transcript):
            parsed["transcricao_ou_descricao"] = pre_extraction_summary or local_transcript

        pontos = parsed.get("pontos", [])
        for idx, pt in enumerate(pontos, start=1):
            pt["numero"] = idx
            pt["classificacao"] = normalize_classification(pt.get("classificacao", ""))
            raw_fontes = pt.get("fontes", [])
            if not isinstance(raw_fontes, list):
                raw_fontes = []

            enriched_fontes = [
                ensure_functional_source_url(f, pt.get("afirmacao_original", ""), web_sources)
                for f in raw_fontes
                if isinstance(f, dict)
            ]
            pt["fontes"] = enriched_fontes

        parsed["pontos"] = pontos
        parsed["fontes_grounding_google"] = web_sources
        parsed["texto_compartilhavel_whatsapp"] = build_whatsapp_summary(parsed)
        return parsed
