# Spec: RAG System

## ADDED Requirements

### Requirement: Knowledge Retrieval Tool
O agente DEVE ter acesso a uma ferramenta explícita (`search_knowledge_base`) ou usar roteamento LangChain para pesquisar informações não triviais na base de conhecimento.

#### Scenario: Searching for Clinic FAQs
- **GIVEN** a patient asks a complex question about insurance or specific treatment details
- **WHEN** the agent determines the answer is not in its core system prompt
- **THEN** it executes a semantic search against the Vector Database
- **AND** retrieves the most relevant chunks to formulate the response

### Requirement: Context Size Management
O sistema de RAG DEVE limitar a quantidade de texto injetada para não estourar o limite de janela de contexto do LLM.

#### Scenario: Limiting Injected Chunks
- **GIVEN** a search returns multiple matching documents
- **WHEN** the results are passed back to the agent
- **THEN** only the top-k (e.g., top 3) most relevant chunks are provided
- **AND** chunks are truncated if they exceed maximum token allowances
