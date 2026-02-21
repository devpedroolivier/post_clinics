# Proposal: Review Appointment Flows

## Why
O clínico precisa garantir que os fluxos de reagendamento e cancelamento pelo WhatsApp (agente Cora) e o reflexo dessas ações no Painel Administrativo estejam ocorrendo corretamente, blindados contra falhas e que a sincronia de dados seja perfeita. A motivação é testar exaustivamente e reajustar possíveis pontas soltas nestes dois fluxos essenciais de gestão de agenda.

## What Changes
1. Análise profunda e testes de ponta-a-ponta nos fluxos de Reagendamento e Cancelamento.
2. Reajuste de prompts no agente (`agent.py`) ou melhoria de ferramentas (`tools.py`) caso os testes apresentem brechas (ex: permissão indevida, falha de atualização de status, exibição confusa).
3. Verificação de concorrência ou erros de atualização de estado no frontend/painel e no backend de mensageria.

## Capabilities
| Capability | Description |
|---|---|
| `rescheduling-flow` | Validação e reajuste de ponta a ponta do fluxo de reagendamento (mudança de horário/data de um agendamento existente). |
| `cancellation-flow` | Validação e reajuste do fluxo de cancelamento (alteração de status para cancelled, liberação de horários associados). |

## Impact
- **Agent/Tools:** `src/agent.py`, `src/tools.py` (ajustes em como as rules são aplicadas e as ferramentas manipuladas).
- **Core Backend:** Possível ajuste em models ou retornos (`src/database.py` ou rotas REST se existirem).
- **Painel Frontend:** Checagem e possíveis ajustes nas UI para exibição consistente de dados alterados.
