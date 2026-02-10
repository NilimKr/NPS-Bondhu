import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_DIR = "data/"
VECTOR_STORE_DIR = "vector_store/"

def ingest_docs():
    """
    Loads PDFs from data/ directory, chunks them, and creates a FAISS index.
    """
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} does not exist.")
        return

    documents = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(DATA_DIR, filename)
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded {len(docs)} pages from {filename}")

    if not documents:
        print("No documents found to ingest.")
        return

    # Split text - Using smaller chunks for better precision
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # Create Embeddings
    print("Generating embeddings... This might take a moment.")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create Vector Store
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save Index
    vector_store.save_local(VECTOR_STORE_DIR)
    print(f"FAISS index saved to {VECTOR_STORE_DIR}")

if __name__ == "__main__":
    ingest_docs()
