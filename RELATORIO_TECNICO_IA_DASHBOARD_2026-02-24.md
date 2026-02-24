# Relatório Técnico Completo - Integração de Agente IA no Dashboard
Data da análise: 24/02/2026

## 1) Diagnóstico técnico (resumo executivo)

O projeto tem uma base sólida para MVP (FastAPI + React + SQLite + agente IA), mas há **quebras críticas de execução em produção** e **riscos de segurança relevantes** no fluxo do agente:

- **Deploy quebrado por entrypoints incorretos** (`src.main` e `src.scheduler` não existem nos caminhos usados por Docker/Compose).
- **Webhook do agente quebra em runtime** por incompatibilidade de API da lib `openai-agents` (`RunConfig(max_turns=10)` inválido na versão instalada).
- **Superfície de ataque ampla** (CORS totalmente aberto com credenciais, token estático sem expiração e defaults inseguros).
- **Boa parte dos testes existe, mas está inconsistente** (scripts sem autenticação, caminho de import incorreto e dependência de servidor externo).

Conclusão: o sistema está próximo de operar com robustez, mas precisa de correções imediatas em **bootstrap/deploy**, **segurança básica** e **compatibilidade da camada de agente**.

## 2) Auto-detecção de stack e arquitetura

### Stack detectada
- Backend: FastAPI + SQLModel + SQLite.
- IA/Agente: `openai-agents` + Groq (endpoint OpenAI-compatible) + tool-calling via tags.
- Vetor/RAG: ChromaDB + LangChain + `all-MiniLM-L6-v2`.
- Frontend: React 19 + Vite + TypeScript + FullCalendar.
- Infra: Docker multi-stage, Docker Compose (app + scheduler + ngrok), GitHub Actions deploy via SSH.

### Arquitetura atual (serviços)
- `app` (API FastAPI + static do dashboard).
- `scheduler` (envio de lembretes 24h/3h).
- `ngrok` (túnel local em ambiente dev).
- Integrações externas: Groq (LLM) e Z-API (mensageria WhatsApp).

## 3) Revisão arquitetural e validação de fluxos

### Fluxo principal validado
1. Dashboard faz login em `/api/auth/login`.
2. Token Bearer acessa `/api/appointments` (CRUD).
3. Webhook `/webhook/zapi` recebe mensagem, aplica antispam, chama agente, executa tools e responde via Z-API.
4. Scheduler lê appointments e envia lembretes.

### Inconsistências encontradas (com severidade)

| ID | Severidade | Inconsistência | Evidência | Impacto |
|---|---|---|---|---|
| A1 | Crítico | Entrypoint de API errado no Docker (`src.main:app`) | `Dockerfile:38` | Container da API não sobe em produção. |
| A2 | Crítico | Entrypoint do scheduler errado no Compose (`python -m src.scheduler`) | `docker-compose.yml:20`, `docker-compose.prod.yml:22` | Serviço de lembretes não inicia. |
| A3 | Crítico | Webhook quebra ao processar agente por `RunConfig(max_turns=10)` inválido | `src/api/routes/webhooks.py:169` | Mensagens reais podem retornar 500. |
| A4 | Alto | CORS aberto para qualquer origem com credenciais habilitadas | `src/api/main.py:27-30` | Risco de abuso cross-origin e configuração insegura. |
| A5 | Alto | Token estático (sem expiração/rotação) e defaults previsíveis | `src/api/routes/auth.py:9-11`, `src/core/security.py:8` | Compromisso de token dá acesso administrativo contínuo. |
| A6 | Alto | Webhook aceita chamadas sem assinatura/verificação de origem | `src/api/routes/webhooks.py:79-110` | Endpoint suscetível a requisições forjadas. |
| A7 | Alto | Payload completo com PII é logado | `src/api/routes/webhooks.py:90` | Exposição de dados sensíveis em logs. |
| A8 | Médio | Chamada bloqueante (`requests.post`) em fluxo assíncrono | `src/infrastructure/services/zapi.py:29`, chamado em `src/api/routes/webhooks.py:227` | Reduz throughput e aumenta latência sob carga. |
| A9 | Médio | Retorno de tools inclui IDs internos, contrariando regra de prompt | `src/application/tools.py:140`, `src/application/tools.py:245`, regra em `src/application/agent.py:88` | Possível vazamento de identificadores ao usuário final. |
| A10 | Médio | Divergência catálogo de serviços dashboard vs backend | `dashboard/src/pages/Dashboard.tsx:259` vs `src/core/config.py:22-29` | Inconsistência funcional e duração default incorreta. |
| A11 | Médio | Scripts/testes desatualizados (path/import/auth) | `tests/test_groq_init.py:3`, `tests/test_e2e_local.py:34-39`, `scripts/verify_full_system.py:29` | Falso negativo/positivo na validação. |
| A12 | Médio | Migração aponta para módulos antigos (`src.config`, `src.database`) | `src/migrate_db.py:5-6` | Script de migração inutilizável sem ajuste. |
| A13 | Baixo | Dependências sem pinagem de versão | `requirements.txt:1-14` | Maior risco de regressões por update implícito. |
| A14 | Baixo | Bundle JS único acima de 500 kB | build Vite (chunk principal ~513 kB) | Degradação de carregamento inicial em redes lentas. |

## 4) Testes funcionais e de integração (reproduzíveis)

### Execuções realizadas

| Comando | Resultado |
|---|---|
| `npm run build` (dashboard) | Sucesso; alerta de chunk > 500 kB. |
| `python tests/test_scheduling.py` | Sucesso (lógica de agendamento/reagendamento/cancelamento). |
| `python tests/test_openai_direct.py` | Sucesso (conectividade com Groq). |
| `python tests/test_groq_init.py` | Falha: `No module named 'src'` (import path incorreto). |
| `python tests/test_e2e_local.py` | Falha: `HTTP Error 404` em `/api/health` no host local esperado. |
| `python -u tests/test_conversation.py` | Falha por `RateLimitError 429` (TPM excedido no modelo). |
| TestClient (API auth + CRUD) | Sucesso com credencial fallback (`clinica_espaco_interativo_reabilitare/admin`). |
| TestClient (webhook com mocks) | Evidenciou 500 por `RunConfig` inválido + dedup funcionando. |

### Observações de validação
- Funcionalidades centrais de CRUD autenticado funcionam quando executadas via `TestClient`.
- O pipeline real do webhook está instável por incompatibilidade de versão da SDK de agentes.
- E2E externo depende de ambiente local específico (porta 8000 + auth + app correta), hoje inconsistente.

## 5) Análise de performance

- Microbenchmark isolado do `_check_availability` mostrou latência baixa em base temporária (ordem de dezenas de ms em carga sintética), mas:
  - algoritmo atual faz varredura de intervalos em memória com sessão síncrona;
  - não há índice explícito em campos críticos (`Appointment.datetime`, `Patient.phone`);
  - endpoint `/api/appointments` retorna lista completa sem paginação (`src/api/routes/appointments.py:19-36`).
- Build frontend reporta bundle principal acima do limite recomendado pelo Vite (chunk warning).

## 6) Análise de segurança

### Falhas principais
- CORS permissivo em excesso (`*` + credentials).
- Controle de acesso baseado em token fixo, sem expiração/refresh.
- Defaults inseguros documentados em `.env.example` (`ADMIN_PASSWORD=admin`, token previsível).
- Ausência de validação forte da origem no webhook.
- Logs com conteúdo de payload potencialmente sensível.

### Nível de risco agregado
- **Risco atual: Alto** para exposição operacional e indisponibilidade do agente em produção.

## 7) Referência aos padrões Context7 e OpenSpec

### Context7 (referência aplicada)
- Context7 enfatiza documentação **atualizada e específica por versão** para evitar APIs obsoletas e alucinações.
- Inferência aplicada ao projeto: a quebra de `RunConfig(max_turns=10)` é exemplo clássico de drift de versão sem validação compatível.

### OpenSpec (referência aplicada)
- OpenSpec estrutura mudanças via `changes/` e `specs/` com fluxo orientado por proposta/design/tarefas.
- O repositório adota essa estrutura, porém com **drift de especificação** em paths antigos (`src/scheduler.py`, `src/zapi.py`) versus código real em subpastas.

## 8) Melhorias recomendadas (implementáveis)

1. Corrigir entrypoints de runtime:
   - API: `uvicorn src.api.main:app`
   - Scheduler: `python -m src.application.scheduler`
2. Corrigir compatibilidade de SDK de agentes:
   - remover/ajustar `RunConfig(max_turns=10)` conforme assinatura atual.
3. Endurecer segurança:
   - CORS restritivo por ambiente;
   - JWT com expiração curta + refresh;
   - validação de assinatura/token específico do webhook;
   - sanitização de logs (sem payload completo).
4. Uniformizar catálogo de serviços:
   - fonte única backend -> frontend.
5. Tornar testes confiáveis:
   - suíte `pytest` real;
   - fixtures para auth e TestClient;
   - E2E com ambiente dockerizado controlado.
6. Melhorar performance:
   - paginação em `/api/appointments`;
   - índices DB;
   - `httpx.AsyncClient` no envio Z-API.
7. Governança de dependências:
   - pinagem/lockfile;
   - rotina de atualização controlada e smoke tests.

## 9) Plano de ação priorizado

### P0 (0-2 dias)
- Corrigir A1/A2/A3 (deploy + webhook breaking).
- Ajustar testes mínimos de fumaça para startup de API/scheduler/webhook.

### P1 (3-7 dias)
- Corrigir A4/A5/A6/A7 (segurança crítica).
- Padronizar autenticação com tokens expirados.

### P2 (1-2 semanas)
- Corrigir A8/A10/A11/A12 (confiabilidade operacional).
- Revisar scripts de validação e remover drift de paths.

### P3 (2-4 semanas)
- Endereçar A13/A14 (governança de dependências e otimização frontend).
- Formalizar política OpenSpec: atualizar specs/tarefas junto a qualquer refactor de estrutura.

## 10) Evidências de rastreabilidade (amostra)

- API/CORS/health: `src/api/main.py:25-39`.
- Auth/token defaults: `src/api/routes/auth.py:9-15`, `src/core/security.py:7-10`.
- Webhook/antispam/Runner/erro 500: `src/api/routes/webhooks.py:79-235`.
- Tool outputs com IDs: `src/application/tools.py:140`, `src/application/tools.py:245`.
- Entrypoints incorretos: `Dockerfile:38`, `docker-compose.yml:20`, `docker-compose.prod.yml:22`.
- Drift de migração: `src/migrate_db.py:5-6`.
- Spec-driven local: `openspec/config.yaml:1`; drift em tarefas legadas: `openspec/changes/improve-agent-core-logic/tasks.md:25-29`.

---

## Fontes externas consultadas
- Context7 Docs (Intro): https://context7.com/docs/overview
- Context7 Docs (Best Practices): https://context7.com/docs/tips
- OpenSpec (README oficial): https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/README.md

