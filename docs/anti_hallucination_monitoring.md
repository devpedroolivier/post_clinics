# Monitoramento Anti-Alucinação (Arquitetura Simples)

A prevenção e o monitoramento de alucinações no agente de IA da clínica dependem de dois pilares principais: **Testes de Inibição em CI/CD** e **Injeção Dinâmica de Contexto**.

## 1. Fluxo de Inibição em CI/CD (Testes)
A suíte `test_agent_hallucination.py` opera como nosso "Gatekeeper" padrão.
- **Ambiente**: O Github Actions executa a suíte antes de todo deploy (via `deploy.yml`).
- **Casos Base**: Garante que o agente continua negando fornecer informações clínicas (ex: transplantes de coração) fora de escopo.
- **Critério de Falha**: O deploy é cancelado se o modelo gerar dados falsos ao invés de usar a heurística "Não sei/Não possuo essa informação" ou acionar `request_human_attendant`.

## 2. Telemetria e Verificação de Logs em Produção
Para analisar se o modelo está aderindo às regras antialucinatórias no trânsito do dia a dia:
   
1. **Instrumentação de Observabilidade**: 
   Sempre que o módulo `context_injection.py` agir (inserindo um limite de corte), nós registramos isso no log em nível `WARNING`.
   
2. **"I don't know" Metrics**:
   Todas as mensagens que o assistente disparar indicando que "não encontrou" a informação (com base nas respostas validadas no teste) podem ser contabilizadas via filtros simples no log do Docker:
   ```bash
   docker logs post_clinics_api_1 | grep "Não possuo essa informação no momento"
   ```
   *Se esse número disparar, significa que o Context Injection não está recuperando a informação correta do Vector Store (RAG gap).*

## 3. Próximos Passos (Melhorias Futuras)
- **Feedback Loop**: O cliente (via WhatsApp) pedir um atendente humano após o bot não conseguir responder deve acionar um alerta no painel de gestão indicando que há um "buraco de conhecimento" naquela dúvida.
- **LLM-as-a-Judge**: Rodar um script Diário em Cron verificando os históricos de chat recentes (no BD SQLite/Postgres), pedindo para um modelo "juiz" barato (ex: Llama-3-8b) votar 1 ou 0 se houve alucinação na transcrição daquele dia.
