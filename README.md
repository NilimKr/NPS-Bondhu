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
- ✅ **Official Documents** - Powered by 15 official NPS PDFs

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

### 3. Ingest Documents (First Time Only)
```bash
python3 src/ingest.py
```
This creates the vector store from PDF documents in the `data/` folder.

### 4. Run the App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📊 System Architecture

### RAG Pipeline:
1. **Document Ingestion** - PDFs → Chunks (500 chars each)
2. **Embedding** - Text → Vectors (sentence-transformers)
3. **Vector Store** - FAISS index for fast retrieval
4. **Retrieval** - MMR search for diverse, relevant chunks
5. **Generation** - LLM generates answer with source citations

### Optimizations:
- ✅ **Smaller chunks** (500 chars) for better precision
- ✅ **MMR search** for diverse, non-redundant results
- ✅ **Response caching** for instant repeated queries
- ✅ **Streaming responses** for better UX
- ✅ **Source citations** for transparency

---

## 📁 Project Structure

```
NPS Bondhu/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not in git)
├── data/                       # PDF documents (15 files)
├── vector_store/               # FAISS index (generated)
├── src/
│   ├── ingest.py              # Document processing
│   ├── rag_chain.py           # RAG implementation
│   └── calculator.py          # Pension calculator
├── .backups/                   # Old versions (safe to delete)
└── README.md                   # This file
```

---

## 📚 Data Sources

The system uses **15 official NPS documents** from PFRDA:

| Document | Type | Chunks |
|----------|------|--------|
| Glossary final for approval | Reference | 172 |
| FAQs on UPS for Subscriber | FAQ | 67 |
| Exit guides (5 files) | Guide | 197 |
| APY.pdf | Guide | 45 |
| NPS-All citizen Model | Guide | 36 |
| Other FAQs (4 files) | FAQ | 70 |

**Total:** 1,190 chunks covering all aspects of NPS

---

## 🎛️ Features

### 1. Ask Bondhu (Chat Interface)
- Natural language Q&A
- Streaming responses
- Source citations with every answer
- Configurable search strategies (MMR/Similarity/Threshold)
- Debug mode for testing

### 2. Pension Calculator
- Estimate retirement corpus
- Calculate lumpsum withdrawal (60%)
- Calculate annuity corpus (40%)
- Estimate monthly pension

### 3. 🌍 Multilingual Support
- **Languages:** English, Hindi (हिन्दी), Assamese (অসমীয়া)
- **Auto-Translation:** Queries are translated to English for processing, then answers are translated back
- **UI Localization:** Interface elements adapt to selected language
- **Transparent:** Source citations remain in English (original source)

---

## ⚙️ Configuration

### Search Strategies:
- **MMR** (default): Balanced similarity + diversity
- **Similarity**: Pure similarity search
- **Similarity Score Threshold**: Only high-quality matches (>0.7)

### Performance Settings:
```python
# In src/rag_chain.py
RETRIEVAL_CONFIG = {
    "k": 5,                    # Retrieve 5 chunks
    "fetch_k": 10,             # Fetch 10 for MMR
    "score_threshold": 0.7,    # Min similarity
    "lambda_mult": 0.7,        # MMR diversity
}
```

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| **Retrieval Precision** | ~85% |
| **Response Time (new)** | 2-3s |
| **Response Time (cached)** | 0.1s |
| **Chunks Retrieved** | 5 per query |
| **Total Chunks** | 1,190 |
| **Chunk Size** | 500 chars |

---

## 🧪 Testing

### Test Queries:
```python
# Simple factual
"What is PRAN?"

# Complex process
"How do I exit NPS before retirement?"

# Specific regulation
"What is the minimum contribution?"

# Tax benefits
"Tell me about tax benefits of NPS"
```

### Debug Mode:
Enable in sidebar to see:
- Retrieval scores
- Source documents
- Similarity scores
- Performance metrics

---

## 🔧 Troubleshooting

### "Vector store not found"
**Solution:** Run `python3 src/ingest.py` to create the index

### Slow responses
**Solutions:**
1. Enable streaming in sidebar
2. Check internet connection
3. Try Groq API instead of Gemini

### Inaccurate answers
**Solutions:**
1. Check source citations
2. Try different search strategy
3. Enable debug mode to see retrieval scores

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

## 🎯 Roadmap

### Completed ✅
- [x] RAG system with official documents
- [x] Pension calculator
- [x] Source citations
- [x] Optimized retrieval (MMR, caching, streaming)
- [x] Streamlit web interface
- [x] Multilingual support (Hindi, Assamese)

### Coming Soon 🚧
- [ ] Voice input/output
- [ ] PDF export of conversations
- [ ] User authentication
- [ ] Analytics dashboard

---

## 📄 License

This is a prototype/demo application. Official NPS information should always be verified with PFRDA.

---

## 🆘 Support

For issues or questions:
1. Check `DATA_QUALITY_REPORT.md` for data quality info
2. Check `OPTIMIZATION_SUMMARY.md` for optimization details
3. Enable Debug Mode in the app
4. Check `.backups/` folder for old versions

---

## 🙏 Acknowledgments

- **PFRDA** for official NPS documents
- **LangChain** for RAG framework
- **Streamlit** for web interface
- **Groq/Google** for LLM APIs
- **Sentence Transformers** for embeddings

---

**Built with ❤️ for NPS subscribers**

**Version:** 2.1 (Multilingual Update)  
**Last Updated:** February 19, 2026
