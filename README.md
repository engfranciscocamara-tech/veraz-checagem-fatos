# Veraz — Bot Verificador de Notícias, Áudios e Vídeos

Aplicação web de checagem de fatos ponto a ponto (Texto, Áudio e Vídeo), baseada nas metodologias do **Fato ou Fake (Grupo Globo)**, **Agência Lupa** e **Aos Fatos**.

## Funcionalidades

1. **Entrada Multimodal (Texto, Áudio e Vídeo)**:
   - **Texto**: Correntes de WhatsApp, postagens de redes sociais, transcrições ou discursos.
   - **Áudio**: Upload de arquivos `.ogg`/`.opus` (áudios encaminhados do WhatsApp), `.mp3`, `.wav`, `.m4a` ou gravação direta pelo microfone no navegador.
   - **Vídeo**: Upload de vídeos `.mp4`, `.mov`, `.webm`, `.avi` com extração automática da fala e captura de quadros-chave para leitura de textos sobrepostos na tela.
2. **Decomposição Ponto a Ponto e Carimbos (Selos)**:
   - Separa cada afirmação factual presente na mensagem e classifica com carimbos:
     - `VERDADEIRO • REAL`
     - `ENGANOSO • PARCIALMENTE VERDADE`
     - `FALSO • MENTIRA`
3. **Informação Verdadeira e Fontes com Data**:
   - Apresenta o contexto correto com dados oficiais e links das fontes consultadas (*Fato ou Fake*, *Agência Lupa*, *Aos Fatos*, *Estadão Verifica*, *Projeto Comprova*, *TSE* e *IBGE*) com a respectiva data.
4. **Cópia para WhatsApp**:
   - Botão para copiar a checagem formatada com marcadores e negrito do WhatsApp para resposta rápida em grupos.

## Segurança e Compartilhamento no GitHub

- Nenhuma chave de API aparece no código-fonte ou na interface do navegador.
- A chave é lida exclusivamente pelo servidor a partir do arquivo local `.env`, que está listado no [.gitignore](file:///c:/Users/francisco.camara/OneDrive%20-%20IMAFLORA/%C3%81rea%20de%20Trabalho/Antigravity/Revisor_Legislacao/.gitignore) para não ser enviado ao GitHub.
- Ao clonar o repositório em outra máquina, basta copiar o arquivo [.env.example](file:///c:/Users/francisco.camara/OneDrive%20-%20IMAFLORA/%C3%81rea%20de%20Trabalho/Antigravity/Revisor_Legislacao/.env.example) para `.env` e definir a variável `GEMINI_API_KEY`.

## Como Executar

```bash
pip install -r requirements.txt
python app.py
```

Acesse no navegador: `http://127.0.0.1:8000`
