# Spec: rescheduling-flow

## Overview
Esta especificação define os requisitos para a análise, ajuste e homologação do fluxo de **Reagendamento** (Reschedule) tanto via Webhook (assistente inteligente) quanto pelo reflexo das operações no Dashboard frontend.

## Details

### 1. Testes de Casos de Borda (Edge Cases)
- **Tentar reagendar um agendamento já cancelado**: A tool deve bloquear e solicitar um novo agendamento, informando o usuário educadamente se for via chat.
- **Tentar reagendar para um horário já ocupado**: O sistema (em `src/tools.py`) deve informar conflito, citando a lógica de duração dinâmica do serviço selecionado.
- **Verificar liberação de slots**: Se um atendimento for movido das 10:00 para as 14:00, o horário das 10:00 deve voltar a estar elegível no `check_availability` no exato momento.

### 2. Tratamento Correto pelo LLaMa 3.1
O prompt em `agent.py` já mapeia os passos:
1. Puxar as consultas do paciente (`find_patient_appointments`)
2. Mostrar as descobertas de forma contextual, sem expor ID de banco.
3. Perguntar novo horário e checar disponibilidade.
4. Chamar `<function=reschedule_appointment>`.
No entanto é preciso depurar os logs em `main.py` para atestar que o agente não "pula" etapas ou tenta embutir sintaxes espúrias se a base falhar.

### 3. Reflexos Visuais
- A UI do dashboard que exibe os horários não pode desincronizar com os dados do SQLite após o commit do reagendamento.
- Testar exibição de "Last Updated" ou logs de movimentação (se existirem na modelagem do frontend)

## Completion Criteria
1. Reagendamento não permite colisão por Duration do Procedimento.
2. Reagendamento sem ID numérico da Tool exposto para o usuário no bot.
3. Reagendamento reflete instantaneamente nas lists do lado Web (Dashboard Otimista ou Server-Fetch natural).
