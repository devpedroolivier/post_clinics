# Spec: cancellation-flow

## Overview
Especificação abordando as amarras e retornos do fluxo de **Cancelamento de Consultas** dentro do ambiente clínico, focando especialmente no comportamento da assistente virtual ao lidar com desmarcações e o rigor da política da empresa (24 horas).

## Details

### 1. Políticas Visíveis (LLM Constraint)
- **Aviso Obrigatório**: Após o cancelamento bem sucedido, o agente deve relembrar que cancelamentos em cima da hora (menor que 24h) impactam os serviços, conforme a regra da clínica inserida no system prompt do `agent.py`.
  
### 2. Validações Core
O método `_cancel_appointment` recebe apenas ID:
- Somente consultas marcadas como "scheduled" ou "confirmed" podem ser canceladas.
- Cancelamentos redundantes (status já `cancelled`) devem retornar uma resposta amigável e limpa.

### 3. Confiabilidade (Reliability)
- O ID do agendamento deve ser encontrado com precisão pela tool `find_patient_appointments(phone)`. O Agente não deve cancelar com base no ID errado se o paciente possuir múltiplas consultas ativas no SQLite. Ex: se ele tem às 08h e às 14h, o Agente precisa desambiguar qual o paciente deseja derrubar antes de emitir a chamada para a tool final.

## Completion Criteria
1. O LLM faz perguntas disambiguadoras *antes* de rodar a `<function=cancel_appointment>`.
2. A política de 24 horas é ativamente comunicada.
3. Tratamento robusto contra double-cancellation (banco evita panic/erro server-side respondendo graciosamente).
