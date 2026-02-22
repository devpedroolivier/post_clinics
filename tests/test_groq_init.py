import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

try:
    from src.application.agent import agent
    print(f"Successfully initialized agent: {agent.name}")
    print(f"Model: {agent.model}")
    print("Groq configuration seems accepted.")
except Exception as e:
    print(f"Failed to initialize agent: {e}")
