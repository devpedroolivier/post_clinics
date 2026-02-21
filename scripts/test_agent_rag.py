import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Runner, SQLiteSession
from src.agent import agent

async def main():
    print("Initializing Agent Runner...")
    
    # Use an in-memory session for quick testing
    session = SQLiteSession(session_id="test_session", db_path=":memory:")
    
    user_id = "test_user_rag"
    
    query = "Telefone do paciente: 5511999998888\nVocês aceitam plano de saúde bradesco?"
    
    print(f"\nUser: {query}")
    print("\nCora (Agent) is thinking...")
    
    response = await Runner.run(agent, input=query, session=session)
    print(f"\nCora: {response}")

if __name__ == "__main__":
    asyncio.run(main())
