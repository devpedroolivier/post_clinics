# Tasks: Review Appointment Flows

## 1. Mapeamento e Testes (Setup)
- [x] 1.1 Criar um script de teste unitário ou de integração (`scripts/test_appointment_flows.py`) focado em simular inputs de Reagendamento e Cancelamento mockando os retornos do BD.
- [ ] 1.2 Depurar a ferramenta existente `_reschedule_appointment` em cenários críticos (conflito de agenda, horários passados).

## 2. Ajustes de Código (Core & Tools)
- [x] 2.1 Refinar a tool `reschedule_appointment` garantindo liberação do horário inicial e validação rigorosa de slot pelo `duration` no novo horário.
- [x] 2.2 Refinar a tool `cancel_appointment` para barrar "double cancellation" ou estados de banco corrompidos.
- [x] 2.3 Refatorar as instruções no system prompt (`agent.py`) para obrigar The Agent a sanear e pedir confirmação antes de disparar o call da ferramenta, avisando a regra de 24 horas no caso do Cancel.

## 3. Validação do Dashboard & Webhook
- [x] 3.1 Disparar requisições simuladas via API REST (ou script de POST manual equivalente ao WhatsApp) validando a regex e a parsing de chamada.
- [x] 3.2 Verificar o reflexo (frontend UI) do Painel Administrativo. A view deve exibir o novo horário (Reagendamento) ou sumir/marcar como cancelado instantaneamente em caso de exclusão.
