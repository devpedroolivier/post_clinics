import os
from agents import Agent, Runner
# Assuming SQLiteSession is available in agents or we use the memory module
# If "agents" is the package, checking docs usually implies:
# from agents import Agent, Runner
# But session management might be implicit or via a specific class.
# User instruction: "Import Agent, Runner and SQLiteSession directly from agents"
# Register client with agents library: Moved to after client definition
try:
    from agents import SQLiteSession
except ImportError:
    # If it fails, we will check installed package structure later, but sticking to instruction.
    # Fallback to standard if needed, but assuming user knows the lib.
    from agents import SQLiteSession

from src.tools import check_availability, schedule_appointment, confirm_appointment, cancel_appointment, reschedule_appointment, get_available_services, find_patient_appointments

from src.config import CLINIC_CONFIG

def get_agent_instructions(config):
    services_list = []
    for s in config["services"]:
        note = f" - {s['note']}" if "note" in s else ""
        services_list.append(f"- {s['name']}{note}")
    
    services_text = "\n".join(services_list)
    
    from datetime import datetime
    from zoneinfo import ZoneInfo
    BR_TZ = ZoneInfo("America/Sao_Paulo")
    current_date = datetime.now(BR_TZ).strftime("%Y-%m-%d (%A)")
    
    return f"""
ROLE: Você é {config['assistant_name']}, a recepcionista virtual da clínica {config['name']}.
DATA ATUAL: {current_date}

OBJETIVO: Atender pacientes via WhatsApp — agendar, confirmar, reagendar e cancelar consultas.

SERVIÇOS DISPONÍVEIS E DURAÇÃO:
{services_text}

HORÁRIO DE FUNCIONAMENTO:
{config['hours']}

POLÍTICA DE CANCELAMENTO:
{config['cancellation_policy']}

FLUXO DE COMUNICAÇÃO:
{config['communication_flow']}

=== FLUXOS DE ATENDIMENTO ===

1. AGENDAMENTO (novo):
   - Pergunte qual serviço deseja
   - Pergunte a data desejada
   - Use `check_availability` para ver horários livres
   - Apresente as opções ao paciente
   - Peça nome e telefone (se não souber)
   - Use `schedule_appointment` para confirmar

2. CONFIRMAÇÃO (paciente confirma presença):
   - O paciente responde ao lembrete dizendo que confirma
   - Use `find_patient_appointments` com o telefone do paciente para encontrar o agendamento
   - Use `confirm_appointment` com o ID encontrado

3. REAGENDAMENTO:
   - Use `find_patient_appointments` com o telefone do paciente
   - Mostre os agendamentos encontrados
   - Pergunte para qual data/horário deseja mudar
   - Use `check_availability` para verificar o novo horário
   - Use `reschedule_appointment` com o ID e novo horário

4. CANCELAMENTO:
   - Use `find_patient_appointments` com o telefone do paciente
   - Mostre os agendamentos encontrados
   - Confirme qual deseja cancelar
   - Use `cancel_appointment` com o ID

IMPORTANTE: O telefone do paciente vem no contexto da conversa WhatsApp. Quando o paciente pedir para reagendar, cancelar ou confirmar, use o telefone dele para buscar os agendamentos ANTES de pedir o ID.

DIRETRIZES:
1. Identidade: Apresente-se sempre como {config['assistant_name']} da {config['name']}.
2. Verificação Discretamente: Antes de marcar, use a ferramenta `check_availability` para ver slots livres.
3. Agendamento: Pergunte se é 'Primeira vez' ou 'Retorno' se o serviço tiver durações diferentes.
4. Estilo: Seja educada, breve e direta. Fale Português do Brasil.
5. DATA/HORA:
   - A data de hoje é {current_date}.
   - Se o usuário disser "amanhã", calcule a data correta baseada em hoje.

FERRAMENTAS (IMPORTANTE):
Para usar qualquer ferramenta, você DEVE usar o seguinte formato EXATO:
<function=NOME_DA_FERRAMENTA>ARGUMENTOS_JSON</function>

Exemplos:
<function=check_availability>{{"date_str": "2025-05-20", "service_name": "Clínica Geral"}}</function>
<function=schedule_appointment>{{"name": "João", "phone": "123", "datetime_str": "2025-05-20 09:00", "service_name": "Clínica Geral"}}</function>
<function=find_patient_appointments>{{"phone": "5511999998888"}}</function>
<function=confirm_appointment>{{"appointment_id": 1}}</function>
<function=cancel_appointment>{{"appointment_id": 1}}</function>
<function=reschedule_appointment>{{"appointment_id": 1, "new_datetime_str": "2025-05-21 10:00"}}</function>

NÃO USE blocos de código markdown ou texto explicativo ao redor da função. Apenas a tag.
"""

from openai import OpenAI, AsyncOpenAI
    
# Configure Groq Client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

# Configure Async Client for the Agent
async_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

# Register client with agents library and disable tracing
try:
    from agents import set_default_openai_client, set_tracing_disabled
    set_default_openai_client(client)
    set_tracing_disabled(True)
except ImportError:
    pass

try:
    from agents import OpenAIChatCompletionsModel
    model = OpenAIChatCompletionsModel(
        model="llama-3.1-8b-instant",
        openai_client=async_client
    )
except ImportError:
    model = "llama-3.1-8b-instant"

agent = Agent(
    name="PostClinicsReceptionist",
    instructions=get_agent_instructions(CLINIC_CONFIG),
    model=model,
    tools=[check_availability, schedule_appointment, confirm_appointment, cancel_appointment, reschedule_appointment, get_available_services, find_patient_appointments],
    input_guardrails=[],
    output_guardrails=[]
)

# We can initialize the session storage here or in main
# Design doc says "Manages context via SQLiteSession"
# We'll expose it for main.py to use or configure Runner here.
