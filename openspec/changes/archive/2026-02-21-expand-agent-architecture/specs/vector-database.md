# Spec: Vector Database Integration

## ADDED Requirements

### Requirement: Document Embedding and Storage
A infraestrutura DEVE suportar a ingestão de documentos de texto, dividindo-os em chunks, gerando embeddings vetoriais e armazenando-os para busca semântica rápida.

#### Scenario: Storing Medical Guidelines
- **GIVEN** a new `guidelines.md` file is added to the clinical knowledge base directory
- **WHEN** the ingestion script is executed
- **THEN** the text is read, chunked by character limits or semantics
- **AND** the chunks are converted to vectors via an embedding model
- **AND** the vectors are inserted into ChromaDB/Qdrant

### Requirement: Semantic Similarity Search
A infraestrutura DEVE expor uma API interna ou função em Python rápida para retornar os `K` chunks mais próximos a uma query textual do usuário.

#### Scenario: Agent Queries DB
- **GIVEN** the agent determines it needs context on "canal radicular tempo de repouso"
- **WHEN** it queries the vector DB
- **THEN** the DB computes the embedding of the query
- **AND** returns the top 3 closest chunks from the stored medical guidelines in under 500ms
