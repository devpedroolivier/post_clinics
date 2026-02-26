## Context

Atualmente, o fluxo do agente registra conversas no banco `data/conversations.db` (tabelas `agent_messages` e `agent_sessions`). O mecanismo de repasse para atendimento humano (handoff) está baseado em um TTL na camada de webhook (`_phone_handoff_until`), o que tem se mostrado frágil (agente volta a interagir inadvertidamente). Não há também encerramento proativo de sessões inativas ou coleta de avaliação do paciente após agendamentos, perdendo oportunidades de retroalimentação para a Cora no seu `learning_loop`.

## Goals / Non-Goals

**Goals:**
- Implementar estado persistente de `handoff` (atendimento humano) na sessão do usuário ou via cache de longo prazo, de modo a desativar permanentemente o bot para aquele número até que um humano feche a aba/sessão.
- Criar cronjob ou verificação na entrada do webhook para encerrar sessões "vencidas" (inatividade de X minutos). Se o usuário mandar nova mensagem após isso, iniciar nova sessão do zero (reativação).
- Ao confirmar o agendamento no prompt da Cora, instrui-la a solicitar um feedback/avaliação de 1 a 5 ou texto aberto.
- Inserir esse feedback num fluxo que vá parar no `learning_loop.py` ou no ChromaDB, adicionando-o ao contexto inicial ("coisas que aprendi com feedbacks passados").

**Non-Goals:**
- Criar um painel de chat para o humano (assumimos que o humano já usa Z-API web/WhatsApp).
- Reconstruir o banco `conversations.db` inteiramente; usaremos migrações simples ou campos adicionais de contexto em JSON.

## Decisions

1. **Persistência do Handoff:** Atualizaremos o TTL de `_phone_handoff_until` para algo permanente (como 24h ou infinito) ao ser invocado o `request_human_attendant`, ou gravaremos um status `is_human_handoff = true` no SQLite `agent_sessions`.
2. **Timeout de Inatividade:** No `webhook.py`, ao receber a mensagem, calcularemos a diferença entre o momento atual e a data da última mensagem daquela sessão. Se for > 30 minutos, o bot encerra a sessão anterior no histórico e abre uma nova, cumprimentando o paciente novamente.
3. **Coleta de Avaliação:** Ajuste no prompt `agent-core`. Adicionar regra: "Após agendar com sucesso, SEMPRE peça uma avaliação do paciente sobre o atendimento, e se despeça". O LLM fará isso organicamente.
4. **Learning Loop do Feedback:** O script `learning_loop.py` já varre `conversations.db`. Atualizaremos a heurística no script para também extrair sentenças de avaliação dos pacientes (mensagens logo após um agendamento bem-sucedido) e resumir isso na persona da Cora.

## Risks / Trade-offs

- **[Risco] O paciente avalia mal mas faz uma nova pergunta junto ("Dou nota 5, mas que horas é mesmo?"):**
  - Mitigação: OLLM já tratará a avaliação organicamente no chat, pois a sessão ainda estará em aberto (antes do timeout).
- **[Risco] O timeout de 30 minutos pode cortar conversas demoradas:**
  - Mitigação: Se o paciente manda nova mensagem 31 min depois, o sistema o trata como novo contato ou reconhece que ele já tem agendamento pendente, sendo relativamente natural para o WhatsApp.