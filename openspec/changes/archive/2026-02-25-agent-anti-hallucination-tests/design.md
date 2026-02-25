## Context

O agente de IA atual tem lidado com perguntas onde o escopo não está perfeitamente delimitado no prompt ou no histórico de contexto, levando a alucinações (respostas com informações incorretas ou suposições inválidas). Para um ambiente crítico (como clínicas/saúde), isso é inaceitável. O Context7 provê um exemplo de como manter referências de contexto sempre atualizadas para modelos locais ou ferramentas de código.

## Goals / Non-Goals

**Goals:**
- Criar um mecanismo confiável para injeção de contexto dinâmico no prompt do agente.
- Desenvolver uma suíte de testes de conversação capaz de medir e validar a incidência de alucinações.
- Garantir que o núcleo do agente saiba responder de forma segura quando não tiver informações suficientes.

**Non-Goals:**
- Treinamento fino (fine-tuning) do modelo base.
- Alteração da infraestrutura de hospedagem da LLM.

## Decisions

1. **Context Injection API Middleware**: O fluxo de mensagens para o agente passará por um middleware que buscará artefatos/documentos contextuais (semelhante ao Context7) e os injetará como system prompts condicionais. 
   - *Rationale*: Evita modificar o orquestrador complexo; injeta o contexto antes do processamento pela LLM.
2. **Conversation Test Suite via Pytest/Jest**: Dependendo da stack atual de testes, utilizaremos testes automatizados na camada de serviço, forçando prompts conhecidos por induzir falhas.
   - *Rationale*: Permite rodar as avaliações no CI/CD a cada PR.
3. **Agent Core "I don't know" heuristic**: Alteração do system prompt base do agent-core instruindo-o explicitamente a não supôr dados não previstos no contexto injetado, pedindo mais informações ou assumindo desconhecimento.

## Risks / Trade-offs

- [Risk] Consumo excessivo de tokens devido ao tamanho dos contextos injetados. ??? Mitigation: Aplicar chunking estrito e limitar o número de documentos recuperados por mensagem via Retrieval-Augmented Generation (RAG).
- [Risk] Demora na geração de respostas (latência aumentada pelo RAG). ??? Mitigation: Uso de embeddings em memória ou indexação rápida para lookup de contexto.
