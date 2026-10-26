"""
Gerador de PDF vetorial do Veraz (puro Python via fpdf2) com layout fiel à tela
e links das fontes 100% clicáveis e funcionais no arquivo PDF.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Tuple
from fpdf import FPDF
from web_search_helper import ensure_functional_source_url


def _clean_text(text: Any) -> str:
    """Normaliza caracteres especiais para renderização limpa nas fontes do sistema."""
    s = str(text or "")
    replacements = {
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u2022": "-",
        "\u00a0": " ",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s.strip()


def _stamp_style(status: str) -> Tuple[str, Tuple[int, int, int], Tuple[int, int, int]]:
    """Retorna (texto_carimbo, cor_texto_borda_rgb, cor_fundo_rgb)."""
    s = (status or "").upper()
    if s == "REAL":
        return ("VERDADEIRO - REAL", (30, 126, 72), (237, 248, 241))
    if "PARCIAL" in s:
        return ("ENGANOSO - PARCIALMENTE VERDADE", (212, 117, 34), (253, 245, 236))
    return ("FALSO - MENTIRA", (201, 53, 44), (253, 240, 239))


class VerazPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=14)
        self._load_fonts()

    def _load_fonts(self):
        win_fonts = r"C:\Windows\Fonts"
        self.has_custom_fonts = False
        try:
            if os.path.exists(os.path.join(win_fonts, "segoeui.ttf")):
                self.add_font("Sans", "", os.path.join(win_fonts, "segoeui.ttf"))
                self.add_font("Sans", "B", os.path.join(win_fonts, "segoeuib.ttf"))
                self.add_font("Sans", "I", os.path.join(win_fonts, "segoeuii.ttf"))
                self.add_font("Serif", "", os.path.join(win_fonts, "georgia.ttf"))
                self.add_font("Serif", "B", os.path.join(win_fonts, "georgiab.ttf"))
                self.add_font("Serif", "I", os.path.join(win_fonts, "georgiai.ttf"))
                self.add_font("Mono", "", os.path.join(win_fonts, "consola.ttf"))
                self.add_font("Mono", "B", os.path.join(win_fonts, "consolab.ttf"))
                self.has_custom_fonts = True
        except Exception:
            self.has_custom_fonts = False

    def set_veraz_font(self, family: str = "Sans", style: str = "", size: float = 10):
        if self.has_custom_fonts:
            self.set_font(family, style, size)
        else:
            fallback = {"Sans": "helvetica", "Serif": "times", "Mono": "courier"}.get(family, "helvetica")
            self.set_font(fallback, style, size)

    def header(self):
        # Pinta o fundo papel creme da página inteira
        self.set_fill_color(245, 242, 234)  # #F5F2EA
        self.rect(0, 0, 210, 297, style="F")

    def footer(self):
        self.set_y(-11)
        self.set_veraz_font("Mono", "", 7.5)
        self.set_text_color(112, 108, 100)
        self.cell(
            0,
            6,
            f"Veraz | Checagem Ponto a Ponto | Pagina {self.page_no()}",
            align="C",
        )


def render_pdf_bytes(data: Dict[str, Any]) -> bytes:
    """Gera o PDF vetorial completo com visual idêntico ao Veraz e links das fontes clicáveis."""
    pdf = VerazPDF()
    pdf.add_page()

    pontos: List[Dict[str, Any]] = data.get("pontos", []) or []
    real_c = sum(1 for p in pontos if (p.get("classificacao") or "").upper() == "REAL")
    partial_c = sum(1 for p in pontos if "PARCIAL" in (p.get("classificacao") or "").upper())
    fake_c = len(pontos) - real_c - partial_c

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    resumo_geral = _clean_text(data.get("resumo_geral", ""))
    transcricao = _clean_text(data.get("transcricao_ou_descricao", ""))

    # 1. Cabeçalho Editorial Veraz
    pdf.set_fill_color(22, 21, 19)  # #161513
    pdf.rect(12, 12, 8, 8, style="F")
    pdf.set_xy(12, 12)
    pdf.set_veraz_font("Sans", "B", 11)
    pdf.set_text_color(245, 242, 234)
    pdf.cell(8, 8, "V", align="C")

    pdf.set_xy(22, 11.5)
    pdf.set_veraz_font("Serif", "B", 16)
    pdf.set_text_color(22, 21, 19)
    pdf.cell(60, 9, "Veraz")

    pdf.set_xy(110, 13)
    pdf.set_veraz_font("Mono", "", 8)
    pdf.set_text_color(112, 108, 100)
    pdf.cell(88, 5, f"GERADO EM {now_str}", align="R")

    pdf.set_draw_color(22, 21, 19)
    pdf.set_line_width(0.5)
    pdf.line(12, 22, 198, 22)

    # 2. Título "Checagem Ponto a Ponto"
    pdf.set_xy(12, 25)
    pdf.set_veraz_font("Mono", "", 7.5)
    pdf.set_text_color(112, 108, 100)
    pdf.cell(0, 4, "ANALISE DECOMPOSTA - PADRAO LUPA, AOS FATOS E FATO OU FAKE", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(12)
    pdf.set_veraz_font("Serif", "B", 20)
    pdf.set_text_color(22, 21, 19)
    pdf.cell(0, 9, "Checagem Ponto a Ponto", new_x="LMARGIN", new_y="NEXT")

    if resumo_geral:
        pdf.ln(1)
        pdf.set_x(12)
        pdf.set_veraz_font("Sans", "", 10)
        pdf.set_text_color(61, 58, 53)
        pdf.multi_cell(186, 5.2, resumo_geral)

    pdf.ln(3)

    # 3. Placar (4 Cartões lado a lado exatamente como na tela)
    y_score = pdf.get_y()
    card_w = 44.2
    gap = 3.0
    scores = [
        (str(len(pontos)), "PONTOS ANALISADOS", (22, 21, 19)),
        (str(real_c), "VERDADEIRO (REAL)", (30, 126, 72)),
        (str(partial_c), "PARCIALMENTE VERDADE", (212, 117, 34)),
        (str(fake_c), "FALSO (MENTIRA)", (201, 53, 44)),
    ]

    for idx, (num_val, label_val, color_rgb) in enumerate(scores):
        x_pos = 12 + idx * (card_w + gap)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(221, 216, 204)
        pdf.set_line_width(0.3)
        pdf.rect(x_pos, y_score, card_w, 16, style="DF")

        pdf.set_xy(x_pos + 3, y_score + 2)
        pdf.set_veraz_font("Serif", "B", 14)
        pdf.set_text_color(*color_rgb)
        pdf.cell(card_w - 6, 6.5, num_val)

        pdf.set_xy(x_pos + 3, y_score + 9.5)
        pdf.set_veraz_font("Mono", "", 6.8)
        pdf.set_text_color(112, 108, 100)
        pdf.cell(card_w - 6, 4, label_val)

    pdf.set_y(y_score + 20)

    # 4. Transcrição / Descrição do Áudio ou Vídeo (se houver)
    if transcricao:
        pdf.set_x(12)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(22, 21, 19)
        pdf.set_line_width(0.35)
        pdf.set_veraz_font("Mono", "B", 7.5)
        pdf.set_text_color(112, 108, 100)
        pdf.cell(186, 5.5, "  TRANSCRICAO E ELEMENTOS VISUAIS IDENTIFICADOS NA MIDIA", fill=True, border="LTR", new_x="LMARGIN", new_y="NEXT")

        pdf.set_x(12)
        pdf.set_veraz_font("Sans", "", 9)
        pdf.set_text_color(61, 58, 53)
        pdf.multi_cell(186, 4.8, transcricao, border="LBR", fill=True)
        pdf.ln(4)

    # 5. Cartões Ponto a Ponto
    for pt in pontos:
        if pdf.get_y() > 235:
            pdf.add_page()

        num_str = f"PONTO {int(pt.get('numero', 1)):02d}"
        stamp_text, stamp_fg, stamp_bg = _stamp_style(pt.get("classificacao", ""))
        quote = _clean_text(pt.get("afirmacao_original", ""))
        analise = _clean_text(pt.get("explicacao_analise", ""))
        verdade = _clean_text(pt.get("informacao_verdadeira", ""))
        fontes = pt.get("fontes", []) or []

        # Topo do ponto: Número + Carimbo (Selo)
        y_top = pdf.get_y()
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(221, 216, 204)
        pdf.set_line_width(0.35)

        pdf.set_xy(12, y_top)
        pdf.set_veraz_font("Mono", "B", 8.5)
        pdf.set_text_color(112, 108, 100)
        pdf.cell(90, 8, f"  {num_str}", fill=True, border="LT")

        # Selo colorido à direita
        pdf.set_xy(102, y_top)
        pdf.cell(96, 8, "", fill=True, border="RT")

        stamp_w = max(48, len(stamp_text) * 2.15 + 6)
        stamp_x = 195 - stamp_w
        pdf.set_fill_color(*stamp_bg)
        pdf.set_draw_color(*stamp_fg)
        pdf.set_line_width(0.45)
        pdf.rect(stamp_x, y_top + 1.3, stamp_w, 5.5, style="DF")
        pdf.set_xy(stamp_x, y_top + 1.3)
        pdf.set_veraz_font("Mono", "B", 7.2)
        pdf.set_text_color(*stamp_fg)
        pdf.cell(stamp_w, 5.5, stamp_text, align="C")

        pdf.set_y(y_top + 8)

        # Citação original em fundo creme
        pdf.set_x(12)
        pdf.set_fill_color(245, 242, 234)
        pdf.set_draw_color(221, 216, 204)
        pdf.set_line_width(0.35)
        pdf.set_veraz_font("Serif", "I", 10.5)
        pdf.set_text_color(22, 21, 19)
        pdf.multi_cell(186, 5.6, f'"{quote}"', border="LR", fill=True)

        # Análise da checagem
        pdf.set_x(12)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_veraz_font("Sans", "", 9.5)
        pdf.set_text_color(61, 58, 53)
        pdf.multi_cell(186, 5.0, f"Analise da checagem: {analise}", border="LR", fill=True)

        # Caixa Verde: Qual é a verdadeira informação
        pdf.set_x(12)
        pdf.set_fill_color(237, 248, 241)
        pdf.set_veraz_font("Mono", "B", 7.5)
        pdf.set_text_color(19, 78, 46)
        pdf.cell(186, 5.0, "  QUAL E A VERDADEIRA INFORMACAO:", border="LR", fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.set_x(12)
        pdf.set_veraz_font("Sans", "", 9.5)
        pdf.set_text_color(19, 78, 46)
        pdf.multi_cell(186, 5.0, verdade, border="LR", fill=True)

        # Fontes com Links Clicáveis Funcionais
        pdf.set_x(12)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_veraz_font("Mono", "B", 7.2)
        pdf.set_text_color(112, 108, 100)
        pdf.cell(186, 5.0, "  FONTES CONSULTADAS (CLIQUE NO LINK PARA ABRIR):", border="LR", fill=True, new_x="LMARGIN", new_y="NEXT")

        if not fontes:
            pdf.set_x(12)
            pdf.set_veraz_font("Sans", "", 8.5)
            pdf.set_text_color(112, 108, 100)
            pdf.cell(186, 5.5, "  Verificacao baseada em dados publicos oficiais.", border="LBR", fill=True, new_x="LMARGIN", new_y="NEXT")
        else:
            for idx_f, raw_f in enumerate(fontes):
                f = ensure_functional_source_url(raw_f, quote)
                is_last = idx_f == len(fontes) - 1
                b_style = "LBR" if is_last else "LR"
                nome = _clean_text(f.get("nome") or "Fonte Oficial")
                dt = _clean_text(f.get("data") or "Recente")
                titulo = _clean_text(f.get("titulo") or "")
                raw_url = (f.get("url") or "").strip()

                line_txt = f"  [Fonte] {nome} ({dt})" + (f" - {titulo}" if titulo else "")
                if len(line_txt) > 105:
                    line_txt = line_txt[:102] + "..."

                pdf.set_x(12)
                pdf.set_fill_color(255, 255, 255)
                pdf.set_veraz_font("Sans", "U", 8.8)
                pdf.set_text_color(29, 78, 216)  # Azul link clicável
                pdf.cell(186, 5.8, line_txt, border=b_style, fill=True, link=raw_url, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(4)

    return bytes(pdf.output())
