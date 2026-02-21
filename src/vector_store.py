import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CHROMA_DB_PATH = os.path.join(DATA_DIR, "chroma_db")

# Use a lightweight, fast local embedding model
# all-MiniLM-L6-v2 is standard and works well for general PT-BR as well (though there are better multilingual ones, it's a good start)
# Using `paraphrase-multilingual-MiniLM-L12-v2` is better for Portuguese
_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store(collection_name: str = "clinic_knowledge"):
    """
    Initializes and returns a LangChain Chroma vector store instance.
    The embeddings and database are stored locally.
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    vector_store = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=_embeddings,
    )
    
    return vector_store

def add_documents_to_store(docs, collection_name: str = "clinic_knowledge"):
    """
    Adds structured documents to a specific collection.
    """
    store = get_vector_store(collection_name)
    store.add_documents(docs)
    return store

def search_store(query: str, k: int = 3, collection_name: str = "clinic_knowledge"):
    """
    Searches the collection for the closest matches.
    """
    store = get_vector_store(collection_name)
    results = store.similarity_search(query, k=k)
    return results

def add_patient_preference(phone: str, text: str):
    """
    Saves a specific preference or note for a patient into the long-term memory vector store.
    """
    from langchain_core.documents import Document
    store = get_vector_store("patient_profiles")
    doc = Document(page_content=text, metadata={"phone": phone})
    store.add_documents([doc])

def get_patient_profile(phone: str) -> str:
    """
    Retrieves all stored preferences for a given patient.
    Uses exact filter match on phone number rather than semantic search.
    """
    store = get_vector_store("patient_profiles")
    # Langchain Chroma supports filtering by metadata
    results = store.similarity_search("patient preferences", k=10, filter={"phone": phone})
    if not results:
        return ""
    
    prefs = [res.page_content for res in results]
    return "Preferências do Paciente:\n" + "\n".join(f"- {p}" for p in prefs)
