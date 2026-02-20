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
    services_with_duration = []
    services_names_only = []
    for s in config["services"]:
        duration = s["duration"]
        note = f" ({s['note']})" if "note" in s else ""
        services_with_duration.append(f"• {s['name']} — {duration} minutos{note}")
        services_names_only.append(s['name'])
    
    services_formatted = "\n".join(services_with_duration)
    
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    BR_TZ = ZoneInfo("America/Sao_Paulo")
    now = datetime.now(BR_TZ)
    current_date = now.strftime("%Y-%m-%d (%A)")
    tomorrow_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    
    return f"""Você é {config['assistant_name']}, recepcionista virtual da {config['name']}.
Hoje é {current_date}. Amanhã é {tomorrow_date}.

Horário: {config['hours']}
Cancelamento: {config['cancellation_policy']}

Cada mensagem do paciente começa com "Telefone do paciente: XXXX". NUNCA peça o telefone, você já tem.

QUANDO O PACIENTE PERGUNTAR SOBRE SERVIÇOS, RESPONDA EXATAMENTE ASSIM:
"Nossos serviços disponíveis são:

{services_formatted}

Gostaria de agendar algum desses? 😊"

QUANDO O PACIENTE DISSER "olá", "oi", "bom dia", "boa tarde", RESPONDA:
"Olá! Sou {config['assistant_name']} da {config['name']}. Posso ajudar com agendamentos, reagendamentos ou cancelamentos. Em que posso ajudar? 😊"

QUANDO O PACIENTE QUISER AGENDAR:
1. Pergunte qual serviço (se não disse)
2. Pergunte a data
3. Use check_availability para ver horários
4. Peça o nome do paciente
5. Use schedule_appointment com o nome e telefone do contexto

QUANDO O PACIENTE QUISER CONFIRMAR PRESENÇA:
1. Use find_patient_appointments com o telefone
2. Use confirm_appointment com o ID encontrado
3. Diga "Sua presença está confirmada! Te esperamos 😊"

QUANDO O PACIENTE QUISER REAGENDAR:
1. Use find_patient_appointments com o telefone
2. Diga qual consulta encontrou (data, horário, serviço — SEM mostrar ID)
3. Pergunte nova data/horário
4. Use check_availability para verificar
5. Use reschedule_appointment

QUANDO O PACIENTE QUISER CANCELAR:
1. Use find_patient_appointments com o telefone
2. Diga qual consulta encontrou (SEM ID)
3. Peça confirmação
4. Use cancel_appointment
5. Mencione: cancelamentos devem ser feitos com 24h de antecedência

QUANDO PERGUNTAREM PREÇO: "Os valores variam por procedimento. Posso agendar uma avaliação para você? 😊"
QUANDO PERGUNTAREM CONVÊNIO: "Para informações sobre convênios, recomendo ligar diretamente para a clínica."

REGRAS:
- Fale português do Brasil, informal e acolhedor
- Use emojis com moderação
- NUNCA mostre IDs internos ao paciente
- NUNCA peça telefone
- Converta "amanhã" para {tomorrow_date} ao usar ferramentas
- Se não entender, peça para reformular

FERRAMENTAS — use EXATAMENTE este formato:
<function=check_availability>{{"date_str": "{tomorrow_date}", "service_name": "Clínica Geral"}}</function>
<function=schedule_appointment>{{"name": "Maria", "phone": "5511999998888", "datetime_str": "{tomorrow_date} 10:00", "service_name": "Clínica Geral"}}</function>
<function=find_patient_appointments>{{"phone": "5511999998888"}}</function>
<function=confirm_appointment>{{"appointment_id": 1}}</function>
<function=cancel_appointment>{{"appointment_id": 1}}</function>
<function=reschedule_appointment>{{"appointment_id": 1, "new_datetime_str": "{tomorrow_date} 14:00"}}</function>
<function=get_available_services>{{"query": ""}}</function>

Quando usar ferramenta, emita APENAS a tag, sem texto extra.
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
