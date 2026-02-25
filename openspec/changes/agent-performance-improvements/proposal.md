<artifact id="proposal" change="agent-performance-improvements">

<problem>
O webhook do agente (`/webhook/zapi`) processa as mensagens de forma síncrona. Quando a API do Groq/LLM atinge o limite de taxa (Rate Limit - HTTP 429), o cliente OpenAI embutido realiza retentativas automáticas com `exponential backoff`, o que trava a thread do FastAPI por 40 a 50 segundos. Isso gera uma experiência lenta e inconsistente para o paciente no WhatsApp (exemplificado pelos altos tempos de resposta no número 11989107142) e pode levar a falhas de timeout do Z-API.
</problem>

<success_criteria>
- **Desacoplamento de Webhooks**: A rota do webhook deve enfileirar as mensagens e retornar status 200 pro Z-API imediatamente. O processamento do LLM deve ocorrer de forma assíncrona (background task).
- **Sem bloqueios por Rate Limit**: As indisponibilidades momentâneas do LLM não devem travar a aplicação, e retentativas não devem travar a API principal.
- **Debounce de Mensagens**: Quando o usuário envia múltiplas mensagens seguidas (ex: "oi" \n "tudo bem?"), o bot não deve gerar 2 chamadas isoladas simultâneas, processando melhor a intenção final.
</success_criteria>

<unlocks>
  <!-- Capabilities whose REQUIREMENTS are introduced or CHANGED by this proposal -->
  <capability name="agent-performance">
    <description>Mecanismos de enfileiramento assíncrono (BackgroundTasks), controle de concorrência e gerenciamento de limite de requisições de LLM.</description>
    <requirement>A rota de webhook no FastAPI deve responder em menos de 1 segundo.</requirement>
    <requirement>O processamento do agente deve ocorrer pós-reconhecimento do webhook.</requirement>
  </capability>
</unlocks>

</artifact>
