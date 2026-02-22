import sys
import os
import asyncio
import re
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Runner, SQLiteSession
from src.application.agent import agent
from src.infrastructure.database import engine
from src.domain.models import Appointment, Patient
from sqlmodel import Session, select
from src.application.tools import (
    _schedule_appointment, check_availability, schedule_appointment, 
    confirm_appointment, cancel_appointment, reschedule_appointment, 
    get_available_services, find_patient_appointments, search_knowledge_base
)

TOOL_MAP = {
    "check_availability": check_availability,
    "schedule_appointment": schedule_appointment,
    "confirm_appointment": confirm_appointment,
    "cancel_appointment": cancel_appointment,
    "reschedule_appointment": reschedule_appointment,
    "get_available_services": get_available_services,
    "find_patient_appointments": find_patient_appointments,
    "search_knowledge_base": search_knowledge_base
}

async def chat():
    # Setup dummy appointments
    tomorrow = datetime.now() + timedelta(days=1)
    date_str1 = tomorrow.strftime("%Y-%m-%d 10:00")
    date_str2 = tomorrow.strftime("%Y-%m-%d 14:00")
    test_phone = "5511000000001"
    
    print("Scheduling 2 initial appointments for Test Patient...")
    _schedule_appointment("Maria LLM", test_phone, date_str1, "Clínica Geral")
    _schedule_appointment("Maria LLM", test_phone, date_str2, "Nutrição")
    
    session = SQLiteSession(session_id="test_llm_session_v2", db_path=":memory:")
    
    # User message
    text_content = "Oi Cora, eu preciso cancelar minha consulta de amanhã."
    print(f"\nUser: {text_content}")
    
    agent_input = f"Telefone do paciente: {test_phone}\n{text_content}"
    result = await Runner.run(agent, input=agent_input, session=session)
    final_text = str(result.final_output)
    
    # Emulate the main.py tool loop
    tool_pattern = r'<function=(\w+)>(.*?)</function>'
    for attempt in range(3):
        matches = list(re.finditer(tool_pattern, final_text, re.DOTALL))
        if not matches:
            break
            
        tool_results = []
        for match in matches:
            func_name = match.group(1)
            args_str = match.group(2).strip()
            print(f">> Cora called Tool: {func_name}({args_str})")
            kwargs = json.loads(args_str) if args_str else {}
            out = TOOL_MAP[func_name](**kwargs)
            tool_results.append(f"Tool '{func_name}' returned: {out}")
            
        next_input = f"(SYSTEM: {' \n'.join(tool_results)}\nBased on these results, respond to the user in Portuguese.)"
        result = await Runner.run(agent, input=next_input, session=session)
        final_text = str(result.final_output)
        
    # Clean text
    reply_text = re.sub(r'<thought>.*?</thought>', '', final_text, flags=re.DOTALL)
    reply_text = re.sub(r'\[TOOL_CALL\]|\[SYSTEM\]|\[FUNCTION\]', '', reply_text)
    reply_text = re.sub(r'Telefone do paciente:\s*\S+', '', reply_text)
    reply_text = re.sub(r'<function=.*?>.*?</function>', '', reply_text, flags=re.DOTALL).strip()
    
    print(f"\nCora Reply: {reply_text}")

if __name__ == "__main__":
    asyncio.run(chat())
