# 🇮🇳 NPS Bondhu - Production Version

**Your AI-Powered Guide to the National Pension System**

---

## 🎯 What is NPS Bondhu?

NPS Bondhu is an intelligent virtual assistant that helps NPS (National Pension System) subscribers understand pension rules, calculate retirement corpus, and get accurate answers from official PFRDA documents.

### Key Features:
- ✅ **AI-Powered Q&A** - Ask questions in natural language
- ✅ **Multilingual Support** - English, Hindi (हिन्दी), Assamese (অসমীয়া)
- ✅ **Source Citations** - Every answer includes source references
- ✅ **Pension Calculator** - Estimate your retirement corpus
- ✅ **Official Documents** - Powered by official NPS PDFs & FAQs
- ✅ **Automated Data Scraping** - Keeps knowledge base up-to-date with PFRDA website

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys
Create a `.env` file with your API key:
```bash
# Use either Groq (recommended for speed) or Google Gemini
GROQ_API_KEY=your_groq_api_key_here
# OR
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Scrape & Ingest Documents (First Time or Updates)
To get the latest official documents and build the knowledge base:

```bash
# 1. Scrape latest data from NPS Trust/PFRDA
python3 scripts/scrape_nps_data.py

# 2. Ingest documents into vector store
python3 src/ingest.py
```
This downloads PDFs and FAQs from official sources into `data/` and creates the vector store.

### 4. Run the App
**Frontend (React):**
```bash
cd frontend
npm install
npm run dev
```

**Backend (FastAPI):**
```bash
uvicorn backend.main:app --reload --port 8000
```

The app will be available at `http://localhost:5173`

---

## 📊 System Architecture

### RAG Pipeline:
1. **Data Acquisition** - Automated scrapers fetch PDFs & FAQs from PFRDA/NPS Trust
2. **Document Ingestion** - PDFs/Text → Chunks (800 chars)
3. **Embedding** - Text → Vectors (sentence-transformers)
4. **Vector Store** - FAISS index for fast retrieval
5. **Retrieval** - MMR search for diverse, relevant chunks
6. **Generation** - LLM generates answer with source citations

### Optimizations:
- ✅ **Unified Ingestion**: Handles both PDFs and text files recursively
- ✅ **Automated Scraping**: Keeps data fresh without manual upload
- ✅ **Hybrid Content**: Integrates both formal circulars and user-friendly FAQs
- ✅ **MMR search**: For diverse, non-redundant results
- ✅ **Source citations**: For transparency

---

## 📁 Project Structure

```
NPS Bondhu/
├── backend/                    # FastAPI Backend
│   └── main.py                
├── frontend/                   # React Frontend
├── data/                       # Data storage
│   ├── scraped_pdfs/          # Downloaded PDF documents
│   └── scraped_text/          # Scraped text content (FAQs)
├── vector_store/               # FAISS index (generated)
├── scripts/
│   └── scrape_nps_data.py     # Automated data scraper
├── src/
│   ├── ingest.py              # Document processing pipeline
│   ├── rag_chain.py           # RAG implementation
│   └── calculator.py          # Pension calculator
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 📚 Data Sources

The system automatically scrapes and indexes:
1.  **Circulars** from NPS Trust
2.  **Acts & Regulations** from NPS Trust
3.  **FAQs** (Text & PDFs) from NPS Trust
4.  **Official Gazettes**

**Total Knowledge Base:** Dynamically updated from official sources.

---

## 🎛️ Features

### 1. Ask Bondhu (Chat Interface)
- Natural language Q&A
- Streaming responses
- Source citations with every answer
- Configurable search strategies (MMR/Similarity/Threshold)

### 2. Pension Calculator
- Estimate retirement corpus
- Calculate lumpsum withdrawal (60%)
- Calculate annuity corpus (40%)
- Estimate monthly pension

### 3. 🌍 Multilingual Support
- **Languages:** English, Hindi (हिन्दी), Assamese (অসমীয়া)
- **Auto-Translation:** Queries are translated to English for processing, then answers are translated back
- **UI Localization:** Interface elements adapt to selected language

---

## 📝 API Keys

### Groq (Recommended)
- **Speed:** Very fast (Llama 3.3 70B)
- **Free tier:** Generous limits
- **Get key:** https://console.groq.com

### Google Gemini (Fallback)
- **Speed:** Good
- **Free tier:** Available
- **Get key:** https://makersuite.google.com/app/apikey

---

## 📄 License

This is a prototype/demo application. Official NPS information should always be verified with PFRDA.

---

## 🙏 Acknowledgments

- **PFRDA/NPS Trust** for official NPS documents
- **LangChain** for RAG framework
- **FastAPI & React** for full-stack architecture
- **Groq/Google** for LLM APIs
- **Sentence Transformers** for embeddings

---

**Built with ❤️ for NPS subscribers**

**Version:** 3.0 (Full Stack & Automated Data)  
**Last Updated:** February 19, 2026
