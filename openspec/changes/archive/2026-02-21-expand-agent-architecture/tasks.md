# Tasks: Agent Architecture Expansion

## 1. Infraestrutura do Vector DB
- [x] 1.1 Adicionar biblioteca ChromaDB ou Qdrant-client ao `requirements.txt`.
- [x] 1.2 Criar módulo `src/vector_store.py` para abstrair a inicialização do DB e armazenamento local.
- [x] 1.3 Criar script de ingestão inicial (carregar `FAQ.md` no Vector DB).
- [x] 1.4 Testar a recuperação semântica básica em um script isolado.

## 2. RAG System (Pesquisa Semântica)
- [x] 2.1 Configurar LangChain/LlamaIndex embeddings model (ex: Nomic via Groq ou local OpenAI).
- [x] 2.2 Criar tool `search_knowledge_base(query)` no `src/tools.py`.
- [x] 2.3 Refatorar o prompt de sistema em `src/agent.py` para instruir o agente a usar a tool `search_knowledge_base` quando perguntado sobre regras que não estão no contexto base.
- [x] 2.4 Testar fluxo de ponta-a-ponta onde o agente responde a uma pergunta médica usando RAG.

## 3. Long-Term Memory (Perfil do Paciente)
- [x] 3.1 Criar tabela SQL `patient_profiles` (ou coleção dedicada no Vector DB) para armazenar preferências (ex: "prefere de manhã").
- [x] 3.2 Criar função que atualiza preferências ao final da interação (usando o LLM para classificar se na conversa houve alguma declaração importante).
- [x] 3.3 Atualizar o fluxo de inicialização da `SQLiteSession` em `src/main.py` para buscar e injetar o perfil do paciente no início de uma nova sessão.

## 4. Code Learning Loop
- [x] 4.1 Criar script assíncrono `learning_loop.py` que lê `conversations.db` procurando sessões encerradas rotuladas como "dúvida mal respondida" ou "correção humana".
- [x] 4.2 Usar LLM nesse script para sumarizar "Aprendizados" das conversas passadas.
- [x] 4.3 Inserir esses aprendizados na collection de `learnings` do Vector DB.
- [x] 4.4 Injetar os Top K `learnings` mais próximos ao contexto atual do agente logo antes de processar uma nova mensagem no `main.py`.

## 5. Deployment e Ajustes Finais
- [x] 5.1 Atualizar `docker-compose.prod.yml` caso não seja usado o backend SQLite standalone do ChromaDB.
- [x] 5.2 Realizar testes de estresse de memória na VPS.
- [x] 5.3 Validar tempo de resposta (latência) no WhatsApp.
