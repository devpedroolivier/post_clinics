import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import search_store

def test_retrieval():
    queries = [
        "Tem convênio?",
        "Qual a regra para retorno infantil?",
        "Fono atende adultos?"
    ]
    
    print("Testing Semantic Search on local ChromaDB...")
    for query in queries:
        print(f"\nQUERY: '{query}'")
        results = search_store(query, k=2)
        for i, res in enumerate(results):
            print(f"  [{i+1}] {res.page_content.strip()}")

if __name__ == "__main__":
    test_retrieval()
