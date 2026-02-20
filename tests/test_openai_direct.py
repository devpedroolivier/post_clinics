
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
print(f"Key present: {bool(api_key)}")
if api_key:
    print(f"Key prefix: {api_key[:4]}...")

base_url = "https://api.groq.com/openai/v1"

print(f"Testing connection to: {base_url}")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print("Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
