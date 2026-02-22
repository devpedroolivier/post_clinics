import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
from src.core.config import DATA_DIR

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CHROMA_DB_PATH = os.path.join(DATA_DIR, "chroma_db")

_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store(collection_name: str = "clinic_knowledge"):
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    vector_store = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=_embeddings,
    )
    return vector_store

def add_documents_to_store(docs, collection_name: str = "clinic_knowledge"):
    store = get_vector_store(collection_name)
    store.add_documents(docs)
    return store

def search_store(query: str, k: int = 3, collection_name: str = "clinic_knowledge"):
    store = get_vector_store(collection_name)
    results = store.similarity_search(query, k=k)
    return results

def add_patient_preference(phone: str, text: str):
    from langchain_core.documents import Document
    store = get_vector_store("patient_profiles")
    doc = Document(page_content=text, metadata={"phone": phone})
    store.add_documents([doc])

def get_patient_profile(phone: str) -> str:
    store = get_vector_store("patient_profiles")
    results = store.similarity_search("patient preferences", k=10, filter={"phone": phone})
    if not results:
        return ""
    
    prefs = [res.page_content for res in results]
    return "Preferências do Paciente:\n" + "\n".join(f"- {p}" for p in prefs)
