"""
POST Clinics - Real Agent Conversation Test

Simulates a multi-turn patient conversation with the AI agent.
Tests: greeting, availability check, scheduling, rescheduling, cancellation.
"""

import asyncio
import sys
import os
import re
import json
from datetime import datetime, timedelta

sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from agents import Runner, SQLiteSession
from src.agent import agent
from src.database import create_db_and_tables, engine, Appointment, Patient
from src.config import DATA_DIR, CLINIC_CONFIG
from src.tools import (
    _check_availability, _schedule_appointment, _cancel_appointment,
    _reschedule_appointment, _get_available_services
)
from sqlmodel import Session, delete

# Tool map for manual execution (same as main.py)
TOOL_MAP = {
    "check_availability": _check_availability,
    "schedule_appointment": _schedule_appointment,
    "cancel_appointment": _cancel_appointment,
    "reschedule_appointment": _reschedule_appointment,
    "get_available_services": _get_available_services,
}

def process_tool_calls(text):
    """Parse and execute any tool calls found in agent output."""
    tool_pattern = r'<function=(\w+)>(.*?)</function>'
    matches = list(re.finditer(tool_pattern, text, re.DOTALL))
    
    if not matches:
        return text, []
    
    results = []
    for match in matches:
        func_name = match.group(1)
        args_str = match.group(2).strip()
        
        if func_name in TOOL_MAP:
            try:
                kwargs = json.loads(args_str) if args_str else {}
                output = TOOL_MAP[func_name](**kwargs)
            except Exception as e:
                output = f"Error: {e}"
        else:
            output = f"Tool '{func_name}' not found."
        
        results.append((func_name, output))
    
    return text, results

def clean_response(text):
    """Clean agent response of artifacts."""
    text = re.sub(r'<thought>.*?</thought>', '', text, flags=re.DOTALL)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'<function=.*?>.*?</function>', '', text, flags=re.DOTALL)
    return text.strip()


async def chat(user_message, session, turn_num):
    """Send a message and get agent response, handling tool calls."""
    print(f"\n{'='*60}")
    print(f"[Turn {turn_num}] Paciente: {user_message}")
    print(f"{'='*60}")
    
    result = await Runner.run(agent, input=user_message, session=session)
    response = result.final_output
    if not isinstance(response, str):
        response = str(response)
    
    # Handle tool calls (up to 3 rounds)
    for attempt in range(3):
        response_text, tool_results = process_tool_calls(response)
        
        if not tool_results:
            break
        
        for func_name, output in tool_results:
            print(f"  [TOOL] {func_name} -> {output[:100]}...")
        
        # Feed results back
        results_str = "\n".join([f"Tool '{n}' returned: {o}" for n, o in tool_results])
        next_input = f"(SYSTEM: {results_str}\nBased on these results, respond to the user in Portuguese.)"
        
        result = await Runner.run(agent, input=next_input, session=session)
        response = result.final_output
        if not isinstance(response, str):
            response = str(response)
    
    clean = clean_response(response)
    if not clean:
        clean = "(Resposta vazia - agente pode ter tentado usar ferramenta sem sucesso)"
    
    print(f"\n  Cora: {clean}")
    return clean


async def main():
    print("=" * 60)
    print("  POST Clinics - Teste de Conversa Real com Agente")
    print(f"  Modelo: llama-3.1-8b-instant (Groq)")
    print(f"  Clinica: {CLINIC_CONFIG['name']}")
    print(f"  Assistente: {CLINIC_CONFIG['assistant_name']}")
    print(f"  Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    create_db_and_tables()
    
    # Clean test data
    with Session(engine) as session:
        session.exec(delete(Appointment))
        session.exec(delete(Patient))
        session.commit()
    
    # Use a test date (next weekday)
    today = datetime.now()
    # Find next Monday if today is weekend
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 1
    test_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    # Setup session
    conversation_db = os.path.join(DATA_DIR, "test_conversations.db")
    session = SQLiteSession(db_path=conversation_db, session_id="test:paciente1")
    
    # --- CONVERSATION FLOW ---
    
    # Turn 1: Greeting
    await chat("Oi, boa tarde!", session, 1)
    
    # Turn 2: Ask about services
    await chat("Quais servicos voces oferecem?", session, 2)
    
    # Turn 3: Check availability
    await chat(f"Quero marcar uma consulta de clinica geral para o dia {test_date}", session, 3)
    
    # Turn 4: Confirm booking
    await chat(f"Pode marcar as 10:00 por favor. Meu nome e Maria Silva, telefone 11999998888", session, 4)
    
    # Turn 5: Reschedule
    await chat("Na verdade, preciso mudar para as 14:00, pode ser?", session, 5)
    
    # Turn 6: Cancel
    await chat("Desculpe, vou precisar cancelar a consulta", session, 6)
    
    print("\n" + "=" * 60)
    print("  TESTE CONCLUIDO")
    print("=" * 60)
    
    # Show final DB state
    with Session(engine) as db_session:
        appts = db_session.exec(
            __import__('sqlmodel', fromlist=['select']).select(Appointment)
        ).all()
        print(f"\n  Agendamentos no banco: {len(appts)}")
        for a in appts:
            print(f"    ID:{a.id} | {a.datetime} | {a.service} | Status: {a.status}")


if __name__ == "__main__":
    asyncio.run(main())
