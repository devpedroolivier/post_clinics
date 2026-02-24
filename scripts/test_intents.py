import os
import sys

# Setup path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.routes.webhooks import preprocess_intent

def run_tests():
    test_cases = [
        ("Sim", "Quero confirmar minha consulta"),
        ("ok", "Quero confirmar minha consulta"),
        ("reagendar", "Quero reagendar minha consulta"),
        ("cancela", "Quero cancelar minha consulta"),
        ("x", "Quero cancelar minha consulta"),
        ("❌", "Quero cancelar minha consulta"),
        ("Ahhh pra lá cora chata", "Quero falar com um atendente"),
        ("Quero falar com um humano", "Quero falar com um atendente"),
        ("Qual o valor da consulta?", "Quero falar com um atendente"),
        ("bom dia", "bom dia"),
        ("quero marcar uma limpeza", "quero marcar uma limpeza")
    ]
    
    passed = 0
    for input_text, expected in test_cases:
        result = preprocess_intent(input_text)
        if result == expected:
            print(f"✅ PASS: '{input_text}' -> '{result}'")
            passed += 1
        else:
            print(f"❌ FAIL: '{input_text}' Expected: '{expected}', Got: '{result}'")
            
    print(f"\n{passed}/{len(test_cases)} tests passed.")

if __name__ == "__main__":
    run_tests()
