<div align="center">
  <img src="https://img.icons8.com/wired/128/health-data.png" alt="POST Clinics Logo" width="100" />
  <h1>POST_clinics</h1>
  <p><strong>Ecossistema de Gestão Clínica Inteligente & IA Receptionist</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-black?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com/)
</div>

<br />

## 📖 Visão Geral

O **POST_clinics** é um sistema Full-Stack projetado para modernizar o fluxo de agendamentos em clínicas médicas e terapêuticas. Mais do que um simples CRUD, o projeto integra um **Agente de IA (Virtual Receptionist)** que gerencia conversas reais via WhatsApp, processa intenções de agendamento e interage com o banco de dados da clínica de forma autônoma e segura.

## ✨ Funcionalidades Core

- 🤖 **IA Receptionist (Cora):** Agente inteligente que realiza triagem, agendamentos, cancelamentos e tira dúvidas clínicas via WhatsApp/Z-API.
- 🧠 **Memória de Longo Prazo (RAG):** Armazenamento vetorial para busca de informações sobre a clínica e preferências dos pacientes.
- 📅 **Dashboard de Gestão:** Painel em React com visual moderno para controle de agenda, tarefas e pacientes.
- ⚡ **Alta Performance:** Processamento assíncrono de webhooks para resposta imediata ao usuário, evitando gargalos de API.
- 🔒 **Arquitetura Limpa:** Separação rígida de responsabilidades entre Domínio, Aplicação e Infraestrutura.

## 🛠️ Arquitetura & Stack Técnica

### Backend (Python/FastAPI)
- **Engine de IA:** `openai-agents` com modelo `gpt-4o-mini`.
- **Persistência:** SQLModel (SQLite) com migrações assíncronas.
- **RAG & Vetores:** Busca semântica para base de conhecimento.
- **Performance:** Uso de `BackgroundTasks` e `asyncio.Locks` para debouncing de mensagens concorrentes.

### Frontend (React/TypeScript)
- **UI:** TailwindCSS & Framer Motion para experiências fluidas.
- **Componentes:** FullCalendar para visualização densa de agendas.
- **State:** Gerenciamento eficiente com Hooks customizados.

### Infraestrutura & DevOps
- **Deploy:** Docker Compose (Prod e Dev) com Nginx Reverse Proxy.
- **Segurança:** SSL automático via Certbot (Let's Encrypt).
- **CI/CD:** Preparado para deploys automatizados em VPS.

## 🚀 Destaque Técnico: Resiliência e Concorrência

Um dos diferenciais deste projeto é o tratamento de **Race Conditions** em chats de IA. Implementamos um sistema de **locks por número de telefone**:
- Impede que múltiplas mensagens simultâneas do mesmo usuário disparem agens concorrentes corrompendo o contexto.
- Garante processamento sequencial e determinístico das intenções do paciente.

## 📂 Estrutura do Projeto

```text
📁 src/                  # Backend: Domain, Application, Infrastructure
├── 📁 api/              # Rotas FastAPI e Webhooks
├── 📁 application/      # Lógica de Agentes e Ferramentas
├── 📁 infrastructure/   # DB e Integrações Externas (Z-API)
📁 dashboard/            # Frontend: React + Vite App
📁 docs/                 # Relatórios Técnicos e Design
📁 tests/                # Cobertura de Testes (Unit, E2E, Anti-Hallucination)
```

## 💻 Como Rodar

1. **Clone & Env:**
   ```bash
   git clone https://github.com/seu-user/post_clinics.git
   cp .env.example .env
   ```
2. **Docker Compose:**
   ```bash
   docker-compose up --build
   ```
   Acesse o Dashboard em `http://localhost:5173` e a documentação da API em `http://localhost:8000/docs`.

---

<div align="center">
  Desenvolvido por <strong>Pedro Olivier / Posolutions Tech</strong> 🚀
</div>
