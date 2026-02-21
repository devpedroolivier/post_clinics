# Design: Agent Architecture Expansion

## Context
Atualmente o agente da clínica (Cora) opera baseado em um prompt estático com as diretrizes e num histórico de mensagens em memória (SQLite). À medida que as FAQs crescem, a complexidade médica e comercial também aumenta, o que demanda que:
1. O agente "pesquise" regras de forma semântica (RAG) ao invés de carregar tudo no contexto do Llama 3.1 8b.
2. O agente possua memória de longo prazo persistente de pacientes.
3. Haja um Code Learning Loop que permita ao sistema refinar seu comportamento a partir do feedback.

## Architecture
A nova arquitetura será dividida em camadas de **Memória Híbrida** e **Orquestração RAG**:

1. **Orquestrador de IA (RAG)**:
   - Utilizaremos **LangChain** ou **LlamaIndex** no `src/agent.py` para criar um grafo de raciocínio.
   - O agente fará chamadas condicionais a ferramentas de RAG quando o usuário perguntar sobre tratamentos específicos ou diretrizes que não estão no contexto base.

2. **Armazenamento Vetorial (Vector DB)**:
   - **Recomendação**: **ChromaDB** ou **Qdrant** rodando em container Docker.
   - Ambos são excelentes para self-hosting na VPS atual. Inicialmente, o ChromaDB pode ser integrado como biblioteca (*in-memory/file*) para MVP, facilitando o deploy.
   - Hospedará a base de conhecimento (Knowledge Base) sobre FAQs, serviços, scripts de venda.

3. **Code Learning Loop**:
   - Uma nova tabela/coleção armazenará "Correções" ou "Feedbacks de conversas".
   - Um script assíncrono (como o atual `scheduler`) fará ingestão destas interações e extrairá "Regras Aprendidas" (Learnings) que serão inseridas no Vector DB.
   - O agente, ao responder um paciente específico, puxará os "Learnings" relacionados como contexto prepended.

## Implementation Details
- **Memória de Curto Prazo**: Continuará no SQLite (`conversations.db` gerenciado pelo `SQLiteSession`).
- **Pipeline RAG**:
  - `Document Loader`: Lerá arquivos `.md` ou `.json` contendo diretrizes médicas/administrativas.
  - `Text Splitter`: Chunking com sobreposição para não perder contexto.
  - `Embedder`: Exigirá um modelo de embedding (sugestão: `nomic-embed-text` ou algum modelo leve e rápido da OpenAI/Cohere/HuggingFace).
- **Tooling**: Adição de uma ferramenta `search_knowledge_base(query)` no `src/tools.py`.

## Risks / Trade-offs
- **Consumo de Memória (VPS)**: Modelos de embedding e um servidor de Vector DB (se não for standalone em arquivo) aumentarão a carga na VPS (191.101.235.185). O Chroma em modo local (arquivo) mitiga parte desse risco.
- **Latência**: Adicionar uma etapa de busca vetorial antes da inferência LLM (Llama 3.1 8b) introduzirá centenas de milissegundos adicionais em respostas que usam FAQ.
- **Complexidade de Prompt**: Modelos menores como o Llama 8b podem ter dificuldade de balancear o contexto RAG injetado versus a instrução base (como presenciado no problema anterior da lista de serviços). Tolerância a contexto confuso precisará ser retestada intensamente.
