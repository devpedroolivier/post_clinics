import asyncio
import os
import sqlite3
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "conversations.db")

async def summarize_learning(messages_str: str) -> str:
    prompt = f"""
    Analise o seguinte histórico de mensagens entre um Paciente e uma Assistente de Clínica (Cora).
    Identifique se o paciente forneceu alguma preferência explícita (ex: horários preferidos, restrições)
    ou se houve alguma correção manual. Se houver um aprendizado válido, retorne APENAS um resumo curto (uma frase) desse aprendizado.
    Se não houver nada relevante, retorne a string exata: "NULL".
    
    Histórico:
    {messages_str}
    """
    
    completion = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    return completion.choices[0].message.content.strip()

async def run_learning_loop():
    print("Running Code Learning Loop...")
    if not os.path.exists(DB_PATH):
        print("conversations.db not found.")
        return

    from src.vector_store import add_patient_preference
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Puxando sessões com pelo menos 3 interações (para ter algum contexto)
        cursor.execute("SELECT session_id FROM messages GROUP BY session_id HAVING count(*) >= 3")
        sessions = [r[0] for r in cursor.fetchall()]
        
        for session_id in sessions:
            phone = session_id.split(":")[-1] if ":" in session_id else session_id
            cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT 10", (session_id,))
            messages = cursor.fetchall()
            
            history_str = "\n".join([f"{r[0]}: {r[1]}" for r in messages])
            
            learning = await summarize_learning(history_str)
            if learning and learning != "NULL" and "NULL" not in learning:
                print(f"Extracted learning for {phone}: {learning}")
                # Store it
                add_patient_preference(phone, learning)
                
    except Exception as e:
        print(f"Error in learning loop: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(run_learning_loop())
