<img src="logo.svg" alt="TailorCV" width="200"/>

Gera currículos em PDF adaptados a cada vaga a partir de um arquivo YAML de habilidades e um template LaTeX. Um LLM seleciona e prioriza o conteúdo; `pdflatex` compila o PDF.

## Como funciona

1. Você mantém suas habilidades e experiências em `skills.yaml`
2. Cola a descrição da vaga na interface
3. O LLM preenche o template LaTeX com o conteúdo mais relevante para aquela vaga
4. O PDF é gerado e fica disponível para download e edição

## Pré-requisitos

**Para rodar com Docker (recomendado):**
- Docker e Docker Compose

**Para rodar localmente:**
- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- `pdflatex` (via `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-lang-portuguese`, `cm-super`)

## Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/jeansobreira/tailorcv.git
cd tailorcv
```

### 2. Crie o arquivo de ambiente

```bash
cp .env.example .env
```

Edite `.env` e preencha a chave do provedor de LLM que deseja usar. Apenas uma seção é necessária — a prioridade é OpenAI → Anthropic → Gemini.

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Anthropic
ANTHROPIC_API_KEY=ant-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# Google Gemini
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Crie seu `skills.yaml`

```bash
cp skills.yaml.example skills.yaml
```

Edite `skills.yaml` com seus dados reais. O arquivo `skills.yaml.example` documenta todos os campos disponíveis. Os campos principais são:

- `perfil` — dados de contato
- `habilidades_tecnicas` — categorias e ferramentas
- `capacidades_modelagem` — problemas resolvidos, abordagens e aplicações
- `competencias_chave` — diferenciais profissionais
- `experiencia` — histórico profissional com `destaques` por empresa
- `educacao` e `idiomas`

> `skills.yaml` não é versionado (está no `.gitignore`). Seus dados ficam apenas na sua máquina.

### 4. Adapte o template LaTeX (opcional)

O arquivo `cv_template.tex` define o layout visual do CV. Edite-o para ajustar fontes, cores, margens e estrutura de seções. O conteúdo é sempre injetado via `cv_content.tex` — nunca edite esse arquivo diretamente.

## Rodando

### Com Docker

```bash
docker compose up --build
```

Acesse `http://localhost:8000`.

### Localmente

```bash
uv sync
uv run uvicorn app:app --app-dir src --reload
```

Acesse `http://localhost:8000`.

## Uso

1. Cole a descrição da vaga no campo de texto
2. Clique em **Gerar CV**
3. O PDF gerado aparece no painel direito
4. Edite o LaTeX no campo de texto se necessário
5. Clique em **Recompilar** para atualizar o PDF
6. Clique em **Download** para salvar o PDF

## Estrutura do projeto

```
skills.yaml          # seus dados (não versionado)
cv_template.tex      # layout LaTeX (versionado — personalize à vontade)
skills.yaml.example  # exemplo documentado da estrutura do YAML
.env.example         # variáveis de ambiente necessárias
src/
├── main.py          # orquestrador: skills + vaga → LLM → LaTeX → PDF
├── llm.py           # roteamento de provedores de LLM
├── prompts.py       # construção dos prompts
├── system_prompt.md # instruções do LLM (editável sem tocar Python)
└── app.py           # API FastAPI
frontend/
├── index.html
├── style.css
└── app.js
tests/               # testes Python (pytest) e JS (Jest)
```

## Desenvolvimento

```bash
# Instalar dependências (incluindo dev)
uv sync

# Rodar testes Python
uv run pytest

# Rodar testes JavaScript
npm test
```

## Provedores de LLM suportados

| Provedor | Variável de chave | Variável de modelo | Padrão |
|---|---|---|---|
| OpenAI | `OPENAI_API_KEY` | `OPENAI_MODEL` | `gpt-4o-mini` |
| Anthropic | `ANTHROPIC_API_KEY` | `ANTHROPIC_MODEL` | `claude-haiku-4-5-20251001` |
| Google Gemini | `GOOGLE_API_KEY` | `GEMINI_MODEL` | `gemini-1.5-flash` |

Se mais de uma chave estiver configurada, a prioridade é OpenAI → Anthropic → Gemini.

## Licença

MIT © [Jean Sobreira](https://github.com/jeansobreira)
