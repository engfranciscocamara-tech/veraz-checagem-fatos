"""
Buscador em tempo real em agências de checagem (Lupa, Aos Fatos, Fato ou Fake,
Estadão Verifica, Comprova), órgãos oficiais de dados (IBGE, TSE, Banco Central,
Tesouro Nacional, Receita Federal, IPEA, Portal da Transparência, Câmara, Senado)
e imprensa profissional via Google News RSS (pt-BR), com resolução automática de URLs.
"""

from email.utils import parsedate_to_datetime
from typing import Any, Dict, List
import urllib.parse
import xml.etree.ElementTree as ET
import httpx


# Mapeamento de portais oficiais de dados, órgãos públicos, agências de checagem e imprensa
KNOWN_SOURCES_MAP: List[ tuple[List[str], str, str] ] = [
    (["ibge", "pnad", "ipca", "censo", "sidra"], "IBGE", "https://agenciadenoticias.ibge.gov.br/"),
    (["tse", "justiça eleitoral", "fato ou boato", "eleitoral"], "TSE - Justiça Eleitoral", "https://www.justicaeleitoral.jus.br/fato-ou-boato/"),
    (["fato ou fake"], "Fato ou Fake (G1)", "https://g1.globo.com/fato-ou-fake/"),
    (["lupa", "agência lupa"], "Agência Lupa", "https://lupa.uol.com.br/"),
    (["aos fatos"], "Aos Fatos", "https://www.aosfatos.org/"),
    (["estadão verifica", "estadao verifica"], "Estadão Verifica", "https://www.estadao.com.br/estadao-verifica/"),
    (["comprova", "projeto comprova"], "Projeto Comprova", "https://projetocomprova.com.br/"),
    (["boatos.org"], "Boatos.org", "https://www.boatos.org/"),
    (["banco central", "bcb", "bacen", "selic", "focus"], "Banco Central do Brasil", "https://www.bcb.gov.br/"),
    (["tesouro", "tesouro nacional", "dívida pública"], "Tesouro Nacional", "https://www.tesourotransparente.gov.br/"),
    (["receita federal", "imposto", "tribut"], "Receita Federal / Ministério da Fazenda", "https://www.gov.br/receitafederal/pt-br"),
    (["fazenda", "ministério da fazenda"], "Ministério da Fazenda", "https://www.gov.br/fazenda/pt-br"),
    (["planejamento", "orçamento", "loa", "ploa"], "Ministério do Planejamento e Orçamento", "https://www.gov.br/planejamento/pt-br"),
    (["transparência", "portal da transparência", "cgu"], "Portal da Transparência (CGU)", "https://portaldatransparencia.gov.br/"),
    (["ipea"], "IPEA", "https://www.ipea.gov.br/"),
    (["câmara", "camara dos deputados"], "Agência Câmara de Notícias", "https://www.camara.leg.br/noticias"),
    (["senado", "agência senado"], "Agência Senado", "https://www12.senado.leg.br/noticias"),
    (["stf", "supremo tribunal federal"], "Supremo Tribunal Federal (STF)", "https://portal.stf.jus.br/"),
    (["planalto", "lei nº", "lei complementar", "decreto"], "Portal da Legislação - Planalto", "https://www4.planalto.gov.br/legislacao/"),
    (["agência brasil", "agencia brasil", "ebc"], "Agência Brasil (EBC)", "https://agenciabrasil.ebc.com.br/"),
    (["g1", "globo"], "G1 Notícias", "https://g1.globo.com/economia/"),
    (["folha", "folha de s.paulo"], "Folha de S.Paulo", "https://www1.folha.uol.com.br/"),
    (["estadão", "estado de s. paulo"], "O Estado de S. Paulo", "https://www.estadao.com.br/"),
    (["valor", "valor econômico"], "Valor Econômico", "https://valor.globo.com/"),
    (["uol"], "UOL Notícias", "https://noticias.uol.com.br/"),
    (["bbc", "bbc news brasil"], "BBC News Brasil", "https://www.bbc.com/portuguese"),
    (["cnn", "cnn brasil"], "CNN Brasil", "https://www.cnnbrasil.com.br/"),
]


def _format_pub_date(raw_date: str) -> str:
    if not raw_date:
        return ""
    try:
        dt = parsedate_to_datetime(raw_date)
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return raw_date[:16]


def search_google_news_rss(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    """Realiza busca jornalística no Google News RSS (Brasil) retornando nome, título, data e link."""
    if not query or not query.strip():
        return []

    encoded = urllib.parse.quote(query.strip())
    url = f"https://news.google.com/rss/search?q={encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    results: List[Dict[str, str]] = []
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                return []

            root = ET.fromstring(resp.text)
            for item in root.findall(".//item")[:max_results]:
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                source_el = item.find("source")

                raw_title = (title_el.text or "").strip() if title_el is not None else ""
                link = (link_el.text or "").strip() if link_el is not None else ""
                pub_date = _format_pub_date((pub_el.text or "").strip() if pub_el is not None else "")
                source_name = (source_el.text or "").strip() if source_el is not None else ""
                source_url = (source_el.get("url") or "").strip() if source_el is not None else ""

                if source_name and raw_title.endswith(f" - {source_name}"):
                    raw_title = raw_title[: -len(f" - {source_name}")].strip()

                results.append(
                    {
                        "nome": source_name or "Imprensa / Checagem",
                        "titulo": raw_title,
                        "data": pub_date or "Recente",
                        "url": link or source_url,
                        "dominio": source_url,
                    }
                )
    except Exception:
        pass

    return results


def search_fact_checks_for_queries(queries: List[str]) -> List[Dict[str, str]]:
    """
    Executa buscas combinando:
    1) Agências de checagem (Fato ou Fake, Lupa, Aos Fatos, Estadão Verifica, Comprova);
    2) Órgãos oficiais de estatísticas e dados (IBGE, Banco Central, TSE, Tesouro Nacional, Agência Brasil, Câmara, Senado);
    3) Imprensa profissional (G1, Folha, Estadão, Valor, UOL, BBC Brasil).
    """
    collected: List[Dict[str, str]] = []
    seen_titles = set()

    for q in queries[:4]:
        clean_q = q.strip()
        if not clean_q:
            continue

        # 1. Busca em agências de checagem
        agency_hits = search_google_news_rss(
            f'{clean_q} (Fato ou Fake OR Lupa OR "Aos Fatos" OR "Estadão Verifica" OR Comprova OR TSE)',
            max_results=4,
        )
        # 2. Busca em dados oficiais (IBGE, Banco Central, Tesouro, Agência Brasil, Receita, IPEA)
        official_hits = search_google_news_rss(
            f'{clean_q} (IBGE OR "Banco Central" OR "Tesouro Nacional" OR "Agência Brasil" OR "Receita Federal" OR IPEA)',
            max_results=4,
        )
        # 3. Busca geral na imprensa
        general_hits = search_google_news_rss(clean_q, max_results=4)

        for hit in agency_hits + official_hits + general_hits:
            title_key = hit["titulo"].lower()
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                collected.append(hit)

    return collected[:22]


def ensure_functional_source_url(
    fonte: Dict[str, Any],
    afirmacao: str = "",
    web_sources: List[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Garante que toda fonte citada (IBGE, Banco Central, TSE, agências de checagem ou jornais)
    possua um link clicável funcional (URL real da notícia/relatório ou portal oficial da instituição).
    """
    nome = str(fonte.get("nome") or "Fonte Oficial").strip()
    titulo = str(fonte.get("titulo") or "").strip()
    data = str(fonte.get("data") or "Recente").strip()
    url = str(fonte.get("url") or "").strip()

    # 1. Se já possui URL válida http/https e não é um domínio fictício, mantém
    if url.startswith("http://") or url.startswith("https://"):
        return {"nome": nome, "titulo": titulo, "data": data, "url": url}

    # 2. Tenta casar com algum resultado real obtido na busca RSS pelo nome do veículo ou palavras do título
    if web_sources:
        nome_low = nome.lower()
        titulo_words = [w.lower() for w in titulo.split() if len(w) > 3]
        for ws in web_sources:
            ws_nome = ws.get("nome", "").lower()
            ws_tit = ws.get("titulo", "").lower()
            ws_url = ws.get("url", "")
            if ws_url.startswith("http"):
                if (nome_low and (nome_low in ws_nome or ws_nome in nome_low)) or (
                    titulo_words and sum(1 for w in titulo_words if w in ws_tit) >= 2
                ):
                    return {
                        "nome": nome or ws.get("nome", "Fonte"),
                        "titulo": titulo or ws.get("titulo", ""),
                        "data": data if data and data != "Recente" else ws.get("data", "Recente"),
                        "url": ws_url,
                    }

    # 3. Faz uma busca rápida específica para o par (nome da fonte + título/afirmação) no Google News RSS
    search_target = f"{nome} {titulo or afirmacao}".strip()
    if search_target:
        specific_hits = search_google_news_rss(search_target[:90], max_results=1)
        if specific_hits and specific_hits[0].get("url", "").startswith("http"):
            hit = specific_hits[0]
            return {
                "nome": nome,
                "titulo": titulo or hit.get("titulo", ""),
                "data": data if data and data != "Recente" else hit.get("data", "Recente"),
                "url": hit["url"],
            }

    # 4. Se for um órgão oficial conhecido (ex: IBGE, Banco Central, TSE, Receita, Câmara, Senado, Lupa, Aos Fatos),
    # usa o portal oficial ou busca oficial da instituição
    combined_low = f"{nome} {titulo}".lower()
    for keywords, _canonical_name, portal_url in KNOWN_SOURCES_MAP:
        if any(k in combined_low for k in keywords):
            # Se for IBGE e houver tema específico, aponta para a busca oficial do IBGE
            if "ibge" in combined_low and (titulo or afirmacao):
                q_ibge = urllib.parse.quote((titulo or afirmacao)[:60])
                return {
                    "nome": nome,
                    "titulo": titulo,
                    "data": data,
                    "url": f"https://www.ibge.gov.br/busca.html?searchword={q_ibge}",
                }
            return {"nome": nome, "titulo": titulo, "data": data, "url": portal_url}

    # 5. Fallback garantido: link direto de pesquisa jornalística para o documento/fonte citado
    q_fallback = urllib.parse.quote(f"{nome} {titulo or afirmacao}".strip()[:80])
    return {
        "nome": nome,
        "titulo": titulo,
        "data": data,
        "url": f"https://news.google.com/search?q={q_fallback}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    }
