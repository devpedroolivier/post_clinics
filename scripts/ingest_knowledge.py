import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import get_vector_store
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter

FAQ_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "FAQ.md")

def ingest_faq():
    if not os.path.exists(FAQ_PATH):
        print(f"File not found: {FAQ_PATH}")
        return
        
    print(f"Loading {FAQ_PATH}...")
    loader = TextLoader(FAQ_PATH, encoding="utf-8")
    docs = loader.load()
    
    print("Chunking document...")
    # Split by headers
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(docs)
    
    print(f"Generated {len(splits)} chunks. Embeeding into ChromaDB...")
    
    # Store in "clinic_knowledge"
    vector_store = get_vector_store("clinic_knowledge")
    vector_store.add_documents(splits)
    
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_faq()
