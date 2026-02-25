<artifact id="specs" change="agent-performance-improvements">

## NEW Capabilities

### `agent-performance`
**Description**: Refatorar o FastAPI webhook para retornar status imediato (HTTP 200) e delegar o processamento do LLM e o envio de mensagens Z-API para BackgroundTasks, a fim de proteger o servidor contra Rate Limits e melhorar a responsividade.

#### Scenario: Responder Imediatamente ao Z-API
- **GIVEN** o servidor Z-API enviar um POST para `/webhook/zapi` com uma nova mensagem de usuário.
- **WHEN** a requisição for autenticada e pré-processada (antispam e deduplicação de Message ID concluídas).
- **THEN** o FastAPI deve agendar a função de processamento pesado usando `BackgroundTasks` e retornar código de sucesso HTTP 200 `{"status": "queued"}` instantaneamente.

#### Scenario: Prevenir Fila Paralela para o Mesmo Telefone (Safe Debounce)
- **GIVEN** o usuário enviar 2 ou mais mensagens quase no mesmo segundo (ex: "ola" e logo em seguida "tudo bem?").
- **WHEN** as duas requisições passarem pelo debouncer e chegarem ao `BackgroundTasks`.
- **THEN** o sistema deve usar uma trava (`asyncio.Lock` ou flag de estado) associada ao telefone (`phone`) para garantir que o Agente LLM processe a lista de mensagens recebidas de forma sequencial ou ignorada com aviso, evitando que duas sessões concorrentes destruam o contexto.

</artifact>
