## Why

A análise de logs recentes (2026-02-25) evidenciou que o encaminhamento para atendentes humanos ("handoff") não é persistente; o assistente (Cora) por vezes continua respondendo indevidamente. Além disso, identificamos a necessidade de gerenciar o ciclo de vida da sessão (encerrando atendimentos ociosos e reativando-os conforme necessário) e a oportunidade de coletar feedback dos pacientes após agendamentos bem-sucedidos para aprimorar o comportamento e a qualidade do atendimento da Cora.

## What Changes

- **Handoff Persistente**: Garantir que, uma vez que o paciente escolha falar com um atendente, o assistente pare de enviar mensagens automatizadas até que o fluxo seja explicitamente retomado ou encerrado pelo humano.
- **Timeout e Encerramento Automático**: Implementar um mecanismo de inatividade que encerra automaticamente o atendimento se o paciente não responder dentro de um tempo limite predefinido.
- **Reativação de Sessão**: Permitir que a sessão seja reativada ou reiniciada caso o paciente volte a enviar mensagens após o encerramento por inatividade.
- **Avaliação e Feedback**: Adicionar uma etapa ao final de um agendamento bem-sucedido para solicitar uma avaliação/feedback do paciente.
- **Melhoria Contínua**: Estabelecer um fluxo onde o feedback coletado seja usado (armazenado e recuperado como contexto/memória) para melhorar as interações futuras da assistente Cora.

## Capabilities

### New Capabilities
- `session-lifecycle`: Define regras de inatividade (timeout), encerramento automático do atendimento e reativação da sessão mediante novas mensagens do paciente.
- `patient-feedback`: Define o fluxo de solicitação, armazenamento e utilização das avaliações dos pacientes para aprimoramento contínuo da assistente.

### Modified Capabilities
- `agent-core`: Adiciona regras rigorosas para o bloqueio de respostas automatizadas durante o estado de *handoff* (encaminhamento humano).

## Impact

- `src/application/agent.py` e `src/api/routes/webhooks.py`: Ajustes na verificação de estado de handoff, lógica de timeout de sessão e gatilhos para mensagens de feedback.
- `src/infrastructure/database.py` ou modelos de banco de dados: Necessidade de salvar estado do atendimento (ativo, em handoff, encerrado) e avaliações de pacientes.
- `src/application/learning_loop.py` (ou similar): Adaptação para ingerir os feedbacks nas melhorias de comportamento da Cora.