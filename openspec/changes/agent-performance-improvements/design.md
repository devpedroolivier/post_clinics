<artifact id="design" change="agent-performance-improvements">

## Motivation & Context
O webhook Z-API atual do `post_clinics` é síncrono. Isso significa que ele recebe o Payload do WhatsApp, faz o tratamento e aguarda toda a requisição de conclusão do Groq/LLama 3.1. Caso o Groq enfrente rate limits, ou demore 40 segundos, a requisição do webhook fica "pendurada". Isso causa indisponibilidade, perda de requisições paralelas (gargalo de IO na VPS) e erros de timeout no Z-API. Além disso, o usuário pode mandar várias mensagens picadas que acionam múltiplos agentes de uma vez.

## Proposed Architecture
- **Inversão de Sincronia (BackgroundTasks)**: Utilizaremos o módulo `BackgroundTasks` nativo do FastAPI para transferir a invocação do `Runner.run` e envio do `send_message` para segundo plano.
- **Resposta Imediata**: O webhook, após fazer a checagem Antispam e Deduplicação Básica, agendará o processamento na BackgroundTask e responderá `{"status": "queued"}` imediatamente em <100ms.
- **Locking Concorrente por Telefone**: Para evitar que duas mensagens do mesmo usuário (enviadas em milissegundos) iniciem dois Agentes paralelos que não conhecem o contexto um do outro, vamos criar um mecanismo de bloqueio (`asyncio.Lock` armazenado em um dicionário global `_phone_locks = {}`). O agente processará a fila do usuário em sequência lógica de chegada, gerando coerência na conversação.

## Alternatives Considered
- Usar Celery/Redis ou RabbitMQ. *Rejeitado porque introduz muita complexidade estrutural (servidores extras) para um problema que o loop assíncrono do Python/FastAPI (`asyncio`/`BackgroundTasks`) consegue resolver em memória, visto a escala atual da clínica.*

## API / Interface Changes
A resposta do `/webhook/zapi` de sucesso ou erro do envio pro Z-API não será imediata na chamada HTTP de entrada, retornando `{"status": "queued"}`.

## Data Storage Changes
Nenhuma alteração estrutural no Banco de Dados (SQLite). Adicionaremos apenas estado em memória `_phone_locks` local no Python e `_phone_message_queues` se for enfileirar as falas.

</artifact>
