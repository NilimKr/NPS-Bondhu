from langchain_community.embeddings import HuggingFaceEmbeddings
import os

def download_model():
    print("Downloading embedding model for build cache...")
    # This triggers the download
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("Model downloaded successfully!")

if __name__ == "__main__":
    download_model()
