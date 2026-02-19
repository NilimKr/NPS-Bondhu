import streamlit as st
import os
from src.rag_chain import (
    get_rag_chain, 
    get_rag_chain_with_sources,
    get_cached_response, 
    cache_response,
    get_retrieval_stats,
    format_sources_for_display,
    get_sources_from_query
)
from src.languages import TRANSLATIONS, LANGUAGE_MAP, LANGUAGE_FULL_NAMES, get_text
from src.translator import translate_to_english, translate_from_english


# Page Config
st.set_page_config(
    page_title="NPS Bondhu",
    page_icon="🇮🇳",
    layout="wide"
)

# ─────────────────────────────────────
# Custom CSS – Premium, Responsive UI
# ─────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --primary:     #1e40af;
    --primary-light:#3b82f6;
    --accent:      #f59e0b;
    --bg-body:     #f0f4f8;
    --bg-card:     #ffffff;
    --text-primary:#1e293b;
    --text-secondary:#64748b;
    --border:      #e2e8f0;
    --gradient-hero: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
    --shadow-sm:   0 1px 3px rgba(0,0,0,0.08);
    --shadow-md:   0 4px 14px rgba(0,0,0,0.08);
    --shadow-lg:   0 10px 30px rgba(0,0,0,0.10);
    --radius:      12px;
    --radius-lg:   16px;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp {
    background: var(--bg-body) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }

/* ── Hero Header ── */
.hero-header {
    background: var(--gradient-hero);
    color: white;
    padding: 2rem 1.5rem 1.6rem;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    text-align: center;
    margin: -1rem -1rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.12) 0%, transparent 60%);
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    position: relative;
}
.hero-subtitle {
    font-size: 1rem;
    opacity: 0.88;
    margin-top: 0.35rem;
    font-weight: 400;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 4px 14px;
    border-radius: 24px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.7rem;
    position: relative;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stAlert {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: var(--radius) !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}

/* ── Sidebar branding ── */
.sidebar-brand {
    text-align: center;
    padding: 1.25rem 0 0.75rem;
}
.sidebar-brand-icon { font-size: 2.8rem; }
.sidebar-brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: white !important;
    margin-top: 0.25rem;
}
.sidebar-brand-tag {
    font-size: 0.7rem;
    opacity: 0.5;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 4px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 0.65rem 1.4rem;
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text-secondary);
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
    box-shadow: var(--shadow-sm);
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"]    { display: none; }

/* ── Chat messages ── */
.stChatMessage {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.75rem !important;
    animation: fadeSlideIn 0.35s ease-out;
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* user bubble accent */
.stChatMessage[class*="user"] {
    border-left: 3px solid var(--primary-light) !important;
    background: #f8fafc !important;
}

/* ── Chat input ── */
.stChatInput {
    border-radius: var(--radius) !important;
    border: 2px solid var(--border) !important;
    box-shadow: var(--shadow-md) !important;
    transition: border-color 0.2s ease;
}
.stChatInput:focus-within {
    border-color: var(--primary-light) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--gradient-hero) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    padding: 0.65rem 2rem !important;
    font-size: 0.92rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-md) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow-sm);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}
[data-testid="stMetricLabel"] {
    font-weight: 600;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-secondary) !important;
}
[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    color: var(--primary) !important;
}

/* ── Alerts ── */
.stAlert {
    border-radius: var(--radius) !important;
    border-width: 0 0 0 4px !important;
}
.stSuccess { border-left-color: #10b981 !important; }
.stInfo    { border-left-color: var(--primary-light) !important; }
.stWarning { border-left-color: var(--accent) !important; }

/* ── Number inputs / Selects ── */
.stNumberInput, .stSelectbox, .stSlider {
    margin-bottom: 0.5rem;
}
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid var(--border) !important;
    transition: border-color 0.2s ease !important;
}
.stNumberInput > div > div > input:focus,
.stSelectbox > div > div:focus-within {
    border-color: var(--primary-light) !important;
}

/* ── Dividers ── */
hr { border-color: var(--border) !important; }

/* ── Language Selector pill ── */
.lang-selector {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: 24px;
    padding: 4px 14px 4px 10px;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-secondary);
    box-shadow: var(--shadow-sm);
}

/* ── Calculator results card ── */
.calc-results-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-md);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .hero-title  { font-size: 1.6rem; }
    .hero-subtitle { font-size: 0.88rem; }
    .hero-header { padding: 1.4rem 1rem 1.2rem; margin: -0.5rem -0.5rem 1rem; }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 0.9rem;
        font-size: 0.8rem;
    }
    .stButton > button {
        padding: 0.55rem 1.2rem !important;
        font-size: 0.84rem !important;
    }
    [data-testid="stMetric"] { padding: 0.75rem 0.9rem !important; }
}
@media (max-width: 480px) {
    .hero-title  { font-size: 1.35rem; }
    .hero-subtitle { font-size: 0.78rem; }
    .hero-badge  { font-size: 0.62rem; padding: 3px 10px; }
    .stTabs [data-baseweb="tab-list"] { flex-direction: column; }
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    font-size: 0.75rem;
    color: var(--text-secondary);
    opacity: 0.7;
}
.app-footer a { color: var(--primary-light); text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────
# Sidebar
# ─────────────────────────────────────
# Production defaults
search_type = "mmr"
enable_streaming = True
debug_mode = False

with st.sidebar:
    # Branding
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🇮🇳</div>
        <div class="sidebar-brand-name">NPS Bondhu</div>
        <div class="sidebar-brand-tag">Pension Assistant</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Language selection in sidebar
    selected_language_display = st.selectbox(
        "🌐  Language / भाषा / ভাষা",
        ["English", "हिन्दी", "অসমীয়া"],
        key="language_selector"
    )
    selected_lang_code = LANGUAGE_MAP.get(selected_language_display, "en")
    lang_full_name = LANGUAGE_FULL_NAMES.get(selected_lang_code, "English")
    
    st.divider()
    
    st.header(get_text(selected_lang_code, "about_header"))
    st.info(get_text(selected_lang_code, "about_text"))
    
    st.divider()
    
    # API Key Check
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GROQ_API_KEY"):
        st.error(get_text(selected_lang_code, "api_key_error"))
        st.stop()

# ─────────────────────────────────────
# Hero Header
# ─────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">NPS Bondhu 🤝</div>
    <div class="hero-subtitle">{get_text(selected_lang_code, "sub_header")}</div>
    <div class="hero-badge">Powered by Official NPS Documents</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────
# Chat Interface
# ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": get_text(selected_lang_code, "welcome_message")
    })

chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input(get_text(selected_lang_code, "chat_placeholder")):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # Check cache first
    cached_answer = get_cached_response(prompt)
    
    if cached_answer:
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(cached_answer)
                st.caption(get_text(selected_lang_code, "cache_indicator"))
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": cached_answer
        })
        st.rerun()
    else:
        with st.spinner(get_text(selected_lang_code, "searching")):
            try:
                if debug_mode:
                    with st.expander("🔍 Retrieval Debug Info", expanded=True):
                        docs_with_scores = get_retrieval_stats(prompt)
                
                query_in_english = translate_to_english(prompt, selected_lang_code)
                
                if selected_lang_code != "en" and debug_mode:
                    st.info(f"🌐 Translated query: {query_in_english}")
                
                rag_chain_func = get_rag_chain_with_sources(
                    streaming=enable_streaming,
                    search_type=search_type,
                    language="English"
                )
                
                if enable_streaming:
                    with chat_container:
                        with st.chat_message("assistant"):
                            response_placeholder = st.empty()
                            
                            full_response = ""
                            
                            for chunk in rag_chain_func({"input": query_in_english}):
                                full_response += chunk
                                response_placeholder.markdown(full_response + "▌")
                            
                            full_response_translated = translate_from_english(full_response, selected_lang_code)
                            
                            source_docs = get_sources_from_query(query_in_english, search_type)
                            formatted_sources = format_sources_for_display(source_docs)
                            
                            if formatted_sources:
                                full_response_with_source = f"{full_response_translated}\n\n{formatted_sources}"
                            else:
                                full_response_with_source = full_response_translated
                            
                            response_placeholder.markdown(full_response_with_source)
                    
                    answer = full_response_with_source
                else:
                    result = rag_chain_func({"input": query_in_english})
                    answer = result["answer"]
                    sources = result["sources"]
                    
                    answer_translated = translate_from_english(answer, selected_lang_code)
                    
                    if sources:
                        answer_with_source = f"{answer_translated}\n\n{sources}"
                    else:
                        answer_with_source = answer_translated
                    
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.markdown(answer_with_source)
                    
                    answer = answer_with_source
                
                cache_response(prompt, answer)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"{get_text(selected_lang_code, 'error_occurred')}{e}")
                if debug_mode:
                    st.exception(e)


# ── Footer ──
st.markdown("""
<div class="app-footer">
    Built with ❤️ for NPS subscribers &nbsp;·&nbsp; Data sourced from official PFRDA documents
</div>
""", unsafe_allow_html=True)
