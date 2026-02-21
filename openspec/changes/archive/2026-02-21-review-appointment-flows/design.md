# Design: Review Appointment Flows

## Architecture
O foco arquitetural será uma varredura nas ferramentas existentes em `src/tools.py` (`_cancel_appointment`, `_reschedule_appointment`, `_find_patient_appointments`), e como o Agente em `src/agent.py` as consome. Não há injeção de novos microsserviços, mas sim um polimento do "Tool Call Flow" entre o LLaMa 3.1 e o banco SQLite.

## Data Model
Não haverá migração estrutural no Data Model existente (`Appointment`, `Patient`), a não ser que o debug exija a inclusão de algum tracking state de conversação extra. Por enquanto, as entities originais do SQLModel dão conta da lógica de State (confirmed, cancelled, scheduled).

## APIs & Interfaces
1. **Tool `cancel_appointment`**: Garantir que trata graciosamente agendamentos com status diferente de pendente/confirmado.
2. **Tool `reschedule_appointment`**: Garantir verificação rigorosa de conflito de datas usando as funções de overlaps `_get_service_duration`. E que cancela/libera a data anterior.
3. **Frontend**: Verificar como a interface de reagendamento renderiza as atualizações otimistas para evitar descompasso com o DB SQLite.

## Security & Performance
- **Segurança**: Confirmar que o RLS (ou verificação de posse) de que um paciente (via número de telefone) só consegue cancelar seus *próprios* agendamentos listados pela ferramenta `find_patient_appointments`.
- **Desempenho**: Prevenir long polling desnecessário; testar a latência do webhook WhatsApp durante as requisições de reagendamento.
