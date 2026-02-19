
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_DIR = "data/"
VECTOR_STORE_DIR = "vector_store/"

def load_documents_from_folder(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} not found.")
        return documents

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                if filename.lower().endswith(".pdf"):
                    print(f"Loading PDF: {filename}")
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
                elif filename.lower().endswith(".txt"):
                    print(f"Loading Text: {filename}")
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs = loader.load()
                    documents.extend(docs)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return documents

def ingest_docs():
    """
    Loads documents from data/ (recursive), chunks them, and creates/updates FAISS index.
    """
    print("Starting ingestion process...")
    documents = load_documents_from_folder(DATA_DIR)

    if not documents:
        print("No documents found to ingest.")
        return

    print(f"Total documents loaded: {len(documents)}")

    # Split text - Using smaller chunks for better precision, especially for FAQs
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # Create Embeddings
    print("Generating embeddings... This might take a moment.")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create Vector Store
    # Note: Creating a new one to ensure clean slate with new data structure
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save Index
    vector_store.save_local(VECTOR_STORE_DIR)
    print(f"FAISS index saved to {VECTOR_STORE_DIR}")

if __name__ == "__main__":
    ingest_docs()
