## Why

Recebemos feedback de que o agente de IA está apresentando alucinações. Para garantir a confiabilidade do sistema e evitar esse comportamento, precisamos realizar testes mais aprofundados e de maior amplitude nos fluxos, conversações e interações. Além disso, a inclusão de referências de contexto atualizadas e confiáveis, inspiradas no Context7, é fundamental para prover dados verídicos ao agente e minimizar suposições sistêmicas.

## What Changes

- Implementação de testes de fluxo e validação focados em cenários de conversação que tendem a induzir alucinação.
- Criação de mecanismos de teste de integração avaliando as respostas do agente frente a diferentes níveis de ambiguidade nas perguntas.
- Configuração de um pipeline de injeção de contexto usando referências sólidas e dinâmicas (ex.: Context7) para enriquecer o embasamento das respostas da IA.
- Desenvolvimento de relatórios ou uma suíte de "todos" testáveis para que as validações possam rodar de forma contínua durante o desenvolvimento de features do agente.

## Capabilities

### New Capabilities
- `context-injection`: Mecanismo para buscar, processar e injetar documentação/contexto atualizado (como Context7) no prompt do agente.
- `anti-hallucination-tests`: Suíte de validação com foco principal na acurácia e integridade conversacional do agente, blindando fluxos contra alucinações.

### Modified Capabilities
- `agent-core`: Atualização no comportamento e na interpretação de prompts pelo núcleo do agente, focado em rejeitar incertezas quando houver falta de contexto.

## Impact

- Afetará o núcleo do serviço/agente (`agent-core`), exigindo que o mesmo suporte injeção de documentos dinâmicos de forma nativa.
- Impactará o fluxo de integração contínua e CI/CD com a introdução da suíte `anti-hallucination-tests`.
- Dependência de ferramentas de documentação online ou bases de conhecimento atualizadas para prover contexto seguro.
