# Proposal: Expand Agent Architecture

## Motivation
Atualmente, a assistente Cora atua em um contexto delimitado pelo histórico recente de conversas e regras estáticas inseridas no system prompt. Para que a clínica possa escalar seu atendimento com maior inteligência comercial, suporte a FAQs complexas, e para que o agente possa "aprender" com interações passadas, precisamos expandir sua arquitetura fundamental.

A introdução de um **Code Learning Loop**, aliado à **RAG** (Retrieval-Augmented Generation) e uma **Memória de Longo Prazo** suportada por um **Banco de Dados Vetorial**, permitirá que o agente:
1. Acesse bases de conhecimento clínicas (manuais, FAQs estendidos, diretrizes de atendimento) de forma eficiente.
2. Recupere histórico longo e preferências de pacientes.
3. Adapte-se às regras de negócios e refine suas respostas ao longo do tempo (Learning Loop).

## Capabilities
- `code-learning-loop`: Mecanismo para retroalimentar o agente com base em correções e interações passadas.
- `rag-system`: Pipeline de Retrieval-Augmented Generation para buscar e injetar contexto de documentos externos no prompt.
- `long-term-memory`: Sistema de memória para lembrar preferências de pacientes e histórico sem onerar o limite de contexto do modelo.
- `vector-database`: Infraestrutura de armazenamento e busca semântica em alta dimensionalidade (escolha exata do DB será definida na fase de Design).

## Impact
- `src/agent.py`: Será refatorado para suportar o pipeline RAG e injeção dinâmica de contexto de memória.
- `src/tools.py`: Novas ferramentas para ler/escrever na memória de longo prazo e buscar na base de conhecimento vetorial.
- **Armazenamento**: Introdução de um novo serviço/dependência (Vector DB) complementando o SQLite logado.
- **Infraestrutura**: Atualização do `docker-compose.prod.yml` para soluções self-hosted (ex: Chroma, Qdrant) ou configuração de APIs para SaaS (ex: Pinecone).
