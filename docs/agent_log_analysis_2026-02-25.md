# Analise profunda - Conversas e logs de 2026-02-25

## Escopo analisado
- `data/conversations.db` (tabelas `agent_messages`, `agent_sessions`)
- `docker logs --since 2026-02-25T00:00:00 postclinics_prod`
- `docker logs --since 2026-02-25T00:00:00 postclinics_scheduler`
- Requisitos OpenSpec:
  - `openspec/specs/agent-core/spec.md`
  - `openspec/specs/context-injection/spec.md`
  - `openspec/specs/anti-hallucination-tests/spec.md`

## Numeros coletados (hoje)
- Conversas hoje: `42` sessoes
- Mensagens hoje: `634`
- Distribuicao em `agent_messages`:
  - `user`: `182`
  - `assistant`: `118`
  - `function_call`: `167`
  - `function_call_output`: `167`
- Logs app principal: `3288` linhas
- Logs scheduler: `355` linhas

## Achados criticos
1. Falhas por limite de modelo/timeout
- `Error code: 429`: `72` ocorrencias
- `Error code: 413`: `6` ocorrencias
- `CRITICAL Error in background task`: `39`
- `WPP:IN`: `96` vs `WPP:OUT`: `57` (lacuna de resposta em parte dos fluxos)

2. Loop anomalo de ferramentas (alta chance de alucinacao operacional)
- Sessao `zapi:5511942190313` teve:
  - `107` chamadas `find_patient_appointments`
  - `107` outputs seguidos
  - sem resposta final de assistente
- Sintoma: ruido de tool-calling e perda de contexto.

3. Vazamento de tag de ferramenta para usuario
- 1 caso observado com resposta contendo `<function=...>` em texto final.
- Efeito colateral: contexto contaminado com texto tecnico.

4. Handoff humano nao persistente
- Em sessoes com gatilho de preco/financeiro, o agente ainda tentou retomar automacao em mensagens seguintes.
- Exemplo de impacto: paciente insiste em preco e recebe respostas repetitivas antes de encaminhamento consistente.

5. Risco de agendamento sem confirmacao explicita
- Prompt tinha passos de agendamento, mas sem regra estrita de confirmacao final obrigatoria antes de chamar `schedule_appointment`.

## Ajustes aplicados (cirurgicos)
### `src/api/routes/webhooks.py`
- Adicionado **handoff state com TTL** por telefone:
  - `_phone_handoff_until`
  - bloqueia automacao durante handoff para mensagens fora de escopo
  - libera automacao quando o usuario volta para escopo de agendamento
- Adicionado **guardrails de tool tags inline**:
  - limite de chamadas por resposta (`MAX_INLINE_TOOL_CALLS`)
  - limite de repeticao da mesma chamada (`MAX_REPEATED_INLINE_SAME_CALL`)
  - excedeu limite -> fallback + encaminhamento humano
- Melhorias de robustez:
  - fast-path de confirmacao aceita pontuacao (`.` `!` `?`)
  - sessao separada para follow-up de tool inline (evita poluir sessao principal)
  - limpeza extra de payload tecnico em resposta final
  - ativa handoff automaticamente em excecoes criticas

### `src/application/agent.py`
- Regra explicita no prompt:
  - apos `request_human_attendant`, nao continuar fluxo automatizado
  - em agendamento novo, exigir confirmacao explicita do paciente antes de `schedule_appointment`

### Testes atualizados/criados
- `tests/test_webhook_resilience.py`
  - novo: handoff persistente ate retorno ao escopo
  - novo: guardrail de excesso de tool tags inline
- Ajustes de isolamento de estado global nos testes:
  - `tests/test_webhook_resilience.py`
  - `tests/test_service_alias_and_handoff.py`
  - `tests/test_async_webhook.py`

## Aderencia ao OpenSpec
- `agent-core`: reforco de limites de contexto e tratamento seguro em ambiguidade/instabilidade.
- `context-injection`: reducao de ruido por truncamento e isolamento de contexto em fallback.
- `anti-hallucination-tests`: novos cenarios de regressao para handoff persistente e tool-loop guard.

## Proximos passos recomendados
1. Deploy dessas mudancas e monitorar por 24h:
- taxa `WPP:OUT / WPP:IN`
- ocorrencias de `CRITICAL Error in background task`
- ocorrencias de `<function=` em resposta final

2. Opcional (proximo patch):
- mover `schedule_appointment` para criar em `scheduled` (pendente) por padrao, com confirmacao obrigatoria para virar `confirmed`.

