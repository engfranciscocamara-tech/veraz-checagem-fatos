"""
Casos reais de exemplo de checagem eleitoral (padrão Fato ou Fake, Agência Lupa e Aos Fatos)
para teste rápido da interface e demonstração da decomposição ponto a ponto.
"""

from typing import Dict, Any, List

SAMPLE_MESSAGES: List[Dict[str, Any]] = [
    {
        "id": "urnas_biometria_abstencao",
        "titulo": "Corrente sobre Urnas Eletrônicas, Biometria e Multa de Abstenção",
        "texto_entrada": (
            "URGENTE PESSOAL! Repassem nos grupos! 1) O TSE confirmou que quem não cadastrou a biometria "
            "até o mês passado teve o título cancelado automaticamente e está proibido de votar no domingo! "
            "2) Além disso, as urnas eletrônicas brasileiras são da primeira geração de 1996 e não passam por "
            "nenhum teste público externo antes da eleição. 3) E cuidado: quem faltar ao primeiro turno "
            "fica proibido de votar no segundo turno se não pagar a multa na hora!"
        ),
        "resultado_demo": {
            "tipo_midia_analisada": "texto",
            "transcricao_ou_descricao": (
                "Mensagem em formato de corrente alarmista contendo três alegações sobre regras de votação, "
                "biometria, auditoria das urnas eletrônicas e participação no segundo turno."
            ),
            "resumo_geral": (
                "A mensagem mistura um procedimento real da Justiça Eleitoral (a coleta biométrica) com três "
                "informações falsas sobre impedimento de voto, funcionamento das urnas e participação no 2º turno."
            ),
            "panorama_veredito": "Totalmente Mentira",
            "pontos": [
                {
                    "numero": 1,
                    "afirmacao_original": (
                        "Quem não cadastrou a biometria teve o título cancelado automaticamente e está proibido de votar no domingo."
                    ),
                    "classificacao": "MENTIRA",
                    "explicacao_analise": (
                        "A ausência de biometria cadastrada não impede o eleitor com título regular de votar. "
                        "Apenas eleitores que deixaram de comparecer a revisões obrigatórias específicas em municípios "
                        "convocados ou que não votaram nem justificaram por três turnos consecutivos têm o título cancelado."
                    ),
                    "informacao_verdadeira": (
                        "Segundo o Tribunal Superior Eleitoral (TSE), o eleitor que está com o título regular, mas ainda "
                        "não possui biometria coletada, vota normalmente apresentando um documento oficial com foto "
                        "(como RG, CNH, passaporte ou e-Título com foto) na seção eleitoral."
                    ),
                    "fontes": [
                        {
                            "nome": "TSE - Fato ou Boato",
                            "titulo": "Eleitor sem biometria cadastrada pode votar normalmente apresentando documento com foto",
                            "data": "Setembro/2026",
                            "url": "https://www.justicaeleitoral.jus.br/fato-ou-boato/"
                        },
                        {
                            "nome": "Fato ou Fake (G1 / Grupo Globo)",
                            "titulo": "É #FAKE que eleitor sem biometria esteja proibido de votar nas eleições",
                            "data": "Outubro/2026",
                            "url": "https://g1.globo.com/fato-ou-fake/"
                        }
                    ]
                },
                {
                    "numero": 2,
                    "afirmacao_original": (
                        "As urnas eletrônicas brasileiras são da primeira geração de 1996 e não passam por nenhum teste público externo antes da eleição."
                    ),
                    "classificacao": "MENTIRA",
                    "explicacao_analise": (
                        "As urnas de 1996 já foram desativadas e recicladas há décadas, e o sistema passa por "
                        "múltiplas etapas públicas e obrigatórias de auditoria com participação de universidades, "
                        "Polícia Federal, OAB, Ministério Público e partidos políticos."
                    ),
                    "informacao_verdadeira": (
                        "As eleições utilizam modelos recentes (como a UE2020 e a UE2022). Antes de cada pleito, o TSE "
                        "realiza o Teste Público de Segurança (TPS), em que investigadores externos examinam o código-fonte, "
                        "além da Cerimônia de Lacração dos Sistemas e do Teste de Integridade no próprio dia da votação, "
                        "auditado em tempo real e filmado."
                    ),
                    "fontes": [
                        {
                            "nome": "Agência Lupa",
                            "titulo": "Urnas eletrônicas passam por auditorias públicas e modelos antigos já foram descartados",
                            "data": "Outubro/2026",
                            "url": "https://lupa.uol.com.br/"
                        },
                        {
                            "nome": "Aos Fatos",
                            "titulo": "Como funcionam o Teste Público de Segurança e o Teste de Integridade das urnas do TSE",
                            "data": "Setembro/2026",
                            "url": "https://www.aosfatos.org/"
                        }
                    ]
                },
                {
                    "numero": 3,
                    "afirmacao_original": (
                        "Quem faltar ao primeiro turno fica proibido de votar no segundo turno se não pagar a multa na hora."
                    ),
                    "classificacao": "MENTIRA",
                    "explicacao_analise": (
                        "A legislação eleitoral brasileira trata cada turno como uma eleição independente. "
                        "A ausência no 1º turno gera dever de justificativa em até 60 dias, mas não bloqueia o voto no 2º turno."
                    ),
                    "informacao_verdadeira": (
                        "De acordo com o Código Eleitoral e as resoluções do TSE, o eleitor que não compareceu ao 1º turno "
                        "pode e deve votar normalmente no 2º turno, desde que seu título estivesse regular antes do pleito. "
                        "O prazo para justificar a ausência no 1º turno é de 60 dias após a votação (pelo app e-Título ou Sistema Justifica)."
                    ),
                    "fontes": [
                        {
                            "nome": "Tribunal Superior Eleitoral (TSE)",
                            "titulo": "Eleitor que não votou no 1º turno pode votar normalmente no 2º turno",
                            "data": "Outubro/2026",
                            "url": "https://www.tse.jus.br/"
                        },
                        {
                            "nome": "Estadão Verifica",
                            "titulo": "Faltar ao primeiro turno não impede eleitor de votar no segundo turno",
                            "data": "Outubro/2026",
                            "url": "https://www.estadao.com.br/estadao-verifica/"
                        }
                    ]
                }
            ],
            "texto_compartilhavel_whatsapp": (
                "*🔎 CHECAGEM PONTO A PONTO (Padrão Fato ou Fake / Lupa / Aos Fatos)*\n"
                "📌 *Panorama:* Totalmente Mentira\n\n"
                "*1. \"Quem não cadastrou a biometria teve o título cancelado e está proibido de votar\"*\n"
                "Veredito: 🔴 *MENTIRA*\n"
                "✅ *A verdade:* Eleitores com título regular que ainda não têm biometria cadastrada votam normalmente apresentando documento oficial com foto.\n"
                "📚 *Fontes:* TSE - Fato ou Boato (Set/2026); Fato ou Fake / G1 (Out/2026)\n\n"
                "*2. \"Urnas são de 1996 e não passam por teste público externo\"*\n"
                "Veredito: 🔴 *MENTIRA*\n"
                "✅ *A verdade:* As urnas antigas foram descartadas. O TSE usa modelos modernos (UE2020/UE2022) e realiza o Teste Público de Segurança (TPS) e o Teste de Integridade com auditoria externa.\n"
                "📚 *Fontes:* Agência Lupa (Out/2026); Aos Fatos (Set/2026)\n\n"
                "*3. \"Quem faltar ao 1º turno fica proibido de votar no 2º turno\"*\n"
                "Veredito: 🔴 *MENTIRA*\n"
                "✅ *A verdade:* Cada turno é independente. Quem faltou ao 1º turno pode votar normalmente no 2º turno e tem até 60 dias para justificar a ausência.\n"
                "📚 *Fontes:* TSE (Out/2026); Estadão Verifica (Out/2026)"
            )
        }
    },
    {
        "id": "dados_eleitorado_fundo_eleitoral",
        "titulo": "Mensagem Mista: Eleitorado Brasileiro, Horário Unificado e Fundo Eleitoral",
        "texto_entrada": (
            "Olha os dados desta eleição: 1) O Brasil ultrapassou a marca de 155 milhões de eleitores aptos a votar "
            "segundo o TSE, e as mulheres são a maioria do eleitorado. 2) Desde 2022, a votação acontece em horário "
            "unificado pelo horário de Brasília das 8h às 17h em todo o país. 3) Só que o TSE aprovou ontem uma "
            "regra secreta dobrando o Fundo Eleitoral para R$ 15 bilhões na reta final da campanha!"
        ),
        "resultado_demo": {
            "tipo_midia_analisada": "texto",
            "transcricao_ou_descricao": (
                "Mensagem com três afirmações distintas sobre estatísticas do eleitorado brasileiro, "
                "horário de funcionamento das seções eleitorais e o valor do Fundo Especial de Financiamento de Campanha."
            ),
            "resumo_geral": (
                "A mensagem apresenta dois fatos verdadeiros sobre o perfil do eleitorado e o horário unificado de votação, "
                "mas inclui uma afirmação falsa no final sobre um suposto aumento secreto do Fundo Eleitoral pelo TSE."
            ),
            "panorama_veredito": "Mistura fatos e distorções",
            "pontos": [
                {
                    "numero": 1,
                    "afirmacao_original": (
                        "O Brasil ultrapassou a marca de 155 milhões de eleitores aptos a votar segundo o TSE, e as mulheres são a maioria do eleitorado."
                    ),
                    "classificacao": "REAL",
                    "explicacao_analise": (
                        "Os números coincidem com as estatísticas oficiais divulgadas pelo Tribunal Superior Eleitoral."
                    ),
                    "informacao_verdadeira": (
                        "De acordo com o cadastro eleitoral oficial do TSE, o Brasil conta com mais de 155 milhões de eleitores aptos, "
                        "sendo o público feminino maioria (cerca de 52,5% do total do eleitorado nacional)."
                    ),
                    "fontes": [
                        {
                            "nome": "TSE - Estatísticas do Eleitorado",
                            "titulo": "Cadastro Eleitoral: Brasil tem mais de 155 milhões de eleitores aptos; mulheres representam 52%",
                            "data": "Julho/2026",
                            "url": "https://sig.tse.jus.br/ords/dwapr/r/seai/sig-eleicao/home"
                        }
                    ]
                },
                {
                    "numero": 2,
                    "afirmacao_original": (
                        "Desde 2022, a votação acontece em horário unificado pelo horário de Brasília das 8h às 17h em todo o país."
                    ),
                    "classificacao": "REAL",
                    "explicacao_analise": (
                        "A unificação do horário de votação pelo fuso de Brasília foi implementada pelo TSE a partir das eleições gerais de 2022."
                    ),
                    "informacao_verdadeira": (
                        "Todas as seções eleitorais do país funcionam das 8h às 17h pelo horário oficial de Brasília. "
                        "Locais com fuso horário diferente (como Acre, Amazonas, Rondônia, Roraima, Mato Grosso e Mato Grosso do Sul) "
                        "ajustam seus relógios locais para abrir e fechar simultaneamente com Brasília."
                    ),
                    "fontes": [
                        {
                            "nome": "Agência Brasil / TSE",
                            "titulo": "Horário de votação é unificado pelo fuso de Brasília das 8h às 17h",
                            "data": "Outubro/2026",
                            "url": "https://www.tse.jus.br/"
                        }
                    ]
                },
                {
                    "numero": 3,
                    "afirmacao_original": (
                        "O TSE aprovou ontem uma regra secreta dobrando o Fundo Eleitoral para R$ 15 bilhões na reta final da campanha."
                    ),
                    "classificacao": "MENTIRA",
                    "explicacao_analise": (
                        "O TSE não tem competência legal para definir nem aumentar o valor do Fundo Especial de Financiamento de Campanha (FEFC), "
                        "e o valor de R$ 15 bilhões é falso."
                    ),
                    "informacao_verdadeira": (
                        "O valor do Fundo Eleitoral é definido pelo Congresso Nacional na aprovação da Lei Orçamentária Anual (LOA) "
                        "e sancionado pelo Poder Executivo (em 2024 e 2026 o montante aprovado na LOA foi de cerca de R$ 4,96 bilhões). "
                        "Ao TSE cabe apenas distribuir os recursos aos partidos conforme os critérios objetivos da Lei nº 9.504/1997."
                    ),
                    "fontes": [
                        {
                            "nome": "Aos Fatos",
                            "titulo": "Fundo Eleitoral é aprovado pelo Congresso no Orçamento, não pelo TSE, e valor é de R$ 4,96 bilhões",
                            "data": "Agosto/2026",
                            "url": "https://www.aosfatos.org/"
                        },
                        {
                            "nome": "Agência Lupa",
                            "titulo": "É falso que TSE tenha criado regra secreta para elevar Fundo Eleitoral a R$ 15 bilhões",
                            "data": "Outubro/2026",
                            "url": "https://lupa.uol.com.br/"
                        }
                    ]
                }
            ],
            "texto_compartilhavel_whatsapp": (
                "*🔎 CHECAGEM PONTO A PONTO (Padrão Fato ou Fake / Lupa / Aos Fatos)*\n"
                "📌 *Panorama:* Mistura fatos e distorções\n\n"
                "*1. \"O Brasil ultrapassou 155 milhões de eleitores aptos e as mulheres são maioria\"*\n"
                "Veredito: 🟢 *REAL*\n"
                "✅ *A verdade:* Dados oficiais do TSE confirmam mais de 155 milhões de eleitores aptos, sendo cerca de 52,5% mulheres.\n"
                "📚 *Fontes:* TSE - Estatísticas do Eleitorado (Jul/2026)\n\n"
                "*2. \"Desde 2022, a votação acontece em horário unificado pelo horário de Brasília (8h às 17h)\"*\n"
                "Veredito: 🟢 *REAL*\n"
                "✅ *A verdade:* A votação ocorre simultaneamente em todo o país das 8h às 17h pelo horário de Brasília.\n"
                "📚 *Fontes:* TSE / Agência Brasil (Out/2026)\n\n"
                "*3. \"O TSE aprovou regra secreta dobrando o Fundo Eleitoral para R$ 15 bilhões\"*\n"
                "Veredito: 🔴 *MENTIRA*\n"
                "✅ *A verdade:* O TSE apenas distribui os recursos previstos em lei. O valor do Fundo Eleitoral (R$ 4,96 bilhões) é definido pelo Congresso Nacional na Lei Orçamentária Anual.\n"
                "📚 *Fontes:* Aos Fatos (Ago/2026); Agência Lupa (Out/2026)"
            )
        }
    }
]
