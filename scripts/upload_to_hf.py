"""
Upload NPS Bondhu backend files to HuggingFace Space using the huggingface_hub API.
This correctly handles binary files (FAISS index) that git push rejects.
"""
from huggingface_hub import HfApi
from dotenv import load_dotenv
import os
import sys

# Load environment variables from the .env file at project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

TOKEN = os.environ.get("HF_TOKEN")
if not TOKEN:
    print("❌ HF_TOKEN not found! Add it to your .env file (e.g. HF_TOKEN=hf_xxx...)")
    sys.exit(1)

REPO_ID = "NilimKr/nps-bondhu-backend"
REPO_TYPE = "space"

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files/folders to upload to the Space
INCLUDE_PATHS = [
    "Dockerfile",
    "requirements.txt",
    "runtime.txt",
    "hf_space_README.md",  # will be uploaded as README.md
    "backend/main.py",
    "src/__init__.py",
    "src/calculator.py",
    "src/download_model.py",
    "src/ingest.py",
    "src/languages.py",
    "src/rag_chain.py",
    "src/translator.py",
    "vector_store/index.faiss",
    "vector_store/index.pkl",
]

api = HfApi(token=TOKEN)

print(f"🚀 Uploading NPS Bondhu backend to HF Space: {REPO_ID}")
print(f"   Base dir: {BASE_DIR}\n")

for rel_path in INCLUDE_PATHS:
    local_path = os.path.join(BASE_DIR, rel_path)
    
    if not os.path.exists(local_path):
        print(f"⚠️  Skipping (not found): {rel_path}")
        continue

    # README.md is special - HF needs it at root with correct name
    if rel_path == "hf_space_README.md":
        path_in_repo = "README.md"
    else:
        path_in_repo = rel_path

    print(f"📤 Uploading: {rel_path} → {path_in_repo}")
    api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=path_in_repo,
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        commit_message=f"Upload {path_in_repo}",
    )
    print(f"   ✅ Done")

print("\n🎉 All files uploaded!")
print(f"   Space URL: https://huggingface.co/spaces/{REPO_ID}")
print(f"   API URL: https://NilimKr-nps-bondhu-backend.hf.space")
print(f"\n⚠️  Next: Add secrets GROQ_API_KEY and GOOGLE_API_KEY in Space Settings!")
