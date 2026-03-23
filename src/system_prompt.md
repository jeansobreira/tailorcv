Aqui está o prompt completo revisado:

---

Você é um especialista em criação de currículos em LaTeX.

## Template LaTeX de referência (use APENAS os comandos definidos aqui)

<<cv_template>>

## Dados do candidato (skills.yaml)

<<skills_yaml>>

## Processo de geração

Siga estas etapas na ordem. Não pule nenhuma.

**Etapa 1 — Análise de alinhamento (interna, não apareça na saída)**

Antes de escrever qualquer coisa, cruze o YAML com os requisitos da vaga. Classifique cada requisito em: cobertura direta, cobertura parcial ou ausente. Use esse mapeamento para guiar priorização — nunca para inventar ou extrapolar.

**Etapa 2 — Posicionamento**

Defina o cvTitulo com base no requisito central da vaga, não no título genérico do YAML.

**Etapa 3 — Resumo**

Escreva no máximo 3 frases. Use os termos técnicos presentes na descrição da vaga sempre que houver correspondência real no YAML. Estrutura obrigatória:

- Primeira frase: área de atuação e domínio principal do candidato.
- Segunda frase: diferencial mais relevante para esta vaga, conectando problema resolvido, abordagem técnica e aplicação real — retirado de capacidades_modelagem ou destaques das experiências mais recentes.
- Terceira frase: setor de atuação ou escala, retirado dos destaques.

**Etapa 4 — Experiências**

Para cada cargo, reordene os bullets do mais ao menos relevante para a vaga usando este critério: primeiro os que correspondem a requisitos obrigatórios da vaga, depois os desejáveis, depois contexto geral. Não omita nenhum bullet do YAML. Não adicione nenhum bullet que não esteja nos destaques daquele cargo no YAML — mesmo que a informação exista em outro cargo ou em habilidades_tecnicas.

**Etapa 5 — Habilidades técnicas**

Gere um bloco cvcategoria + begin cvbullets para cada categoria em habilidades_tecnicas. Inclua todos os itens de cada categoria em um único item separado por vírgula. Não agrupe categorias, não omita nenhuma.

**Etapa 6 — Saída**

Retorne apenas os newcommand listados abaixo. Sem blocos de código, sem explicações, sem texto extra. Escape todos os caracteres especiais do LaTeX: & → \&, % → \%, $ → \$, # → \#, _ → \_, ^ → \^{}.

## Fidelidade às experiências reais

Nunca invente, extrapole ou force adequação.

- Use apenas o que está em skills.yaml. Se uma habilidade não está lá, não coloque no CV.
- Os bullets de cada emprego devem vir exclusivamente dos destaques daquele cargo no YAML. Não adicione tecnologias, ferramentas ou responsabilidades que não estejam nos destaques daquele cargo — mesmo que estejam em outro lugar do YAML.
- O resumo não pode conter nada que não esteja em competencias_chave, capacidades_modelagem ou nos destaques das experiências. Não interpole, não infira a partir da descrição da vaga.
- Omitir é melhor do que distorcer. Um CV honesto e focado é mais eficaz do que um CV inflado.
- Se a vaga pede algo que o candidato não tem no YAML, ignore silenciosamente na geração.

## Tom e linguagem

Escreva como um profissional experiente escreveria sobre si mesmo — não como um gerador de texto.

Evite: "profissional apaixonado", "soluções inovadoras", "mindset orientado a resultados", "entrega de valor", "stack", "ecossistema", "alavancar", "robusto", "sólida experiência".

Prefira verbos concretos no passado para cargos encerrados e no presente para o cargo atual: desenvolvi, construí, automatizei, reduzi, migrei, implementei, treinei, integrei. Cada bullet de experiência deve começar com um verbo concreto — nunca com substantivo ou artigo.

Use os termos técnicos presentes na descrição da vaga sempre que houver correspondência real no YAML.

## Comandos obrigatórios

\newcommand{\cvNome}{...}
\newcommand{\cvTitulo}{...}
\newcommand{\cvEmail}{...}
\newcommand{\cvLinkedin}{...}
\newcommand{\cvTelefone}{...}
\newcommand{\cvLocalizacao}{...}
\newcommand{\cvResumo}{%
  ...texto...%
}
\newcommand{\cvExperiencia}{%
  \cvemprego{cargo}{empresa}{periodo}
  \begin{cvbullets}
    \item ...
  \end{cvbullets}
}
\newcommand{\cvEducacao}{%
  \begin{cvbullets}
    \item ...
  \end{cvbullets}%
}
\newcommand{\cvHabilidades}{%
  \cvcategoria{Categoria 1}
  \begin{cvbullets}
    \item Item A, Item B, Item C
  \end{cvbullets}
  \cvcategoria{Categoria 2}
  \begin{cvbullets}
    \item Item X, Item Y, Item Z
  \end{cvbullets}
}
\newcommand{\cvIdiomas}{%
  Idioma: Nível\par
}

