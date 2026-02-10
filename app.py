import streamlit as st
import os
from src.calculator import calculate_pension_corpus
from src.rag_chain import (
    get_rag_chain, 
    get_rag_chain_with_sources,
    get_cached_response, 
    cache_response,
    get_retrieval_stats,
    format_sources_for_display,
    get_sources_from_query
)

# Page Config
st.set_page_config(
    page_title="NPS Bondhu",
    page_icon="🇮🇳",
    layout="wide"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-bubble {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .optimization-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">NPS Bondhu 🤝<span class="optimization-badge">⚡ OPTIMIZED</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your AI-Powered Guide to the National Pension System</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About")
    st.info(
        "NPS Bondhu is a prototype AI assistant designed to help you understand NPS rules "
        "and estimate your pension. \n\n"
        "**Note**: Responses are generated based on official documents using AI. "
        "Always verify with official PFRDA sources."
    )
    
    st.divider()
    
    # Optimization Settings
    st.header("⚙️ Settings")
    
    search_type = st.selectbox(
        "Search Strategy",
        ["mmr", "similarity", "similarity_score_threshold"],
        index=0,
        help="MMR: Diverse results | Similarity: Most similar | Threshold: High-quality only"
    )
    
    
    enable_streaming = st.checkbox("Enable Streaming", value=True, help="Stream responses for faster perceived speed")
    
    st.divider()
    
    # Performance Stats
    st.header("📊 Performance")
    st.metric("Chunk Size", "500 chars", delta="-50%", delta_color="normal")
    st.metric("Retrieval Count", "5 chunks", delta="+67%", delta_color="normal")
    st.caption("Optimized for precision & speed")
    
    st.divider()
    
    # API Key Check
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GROQ_API_KEY"):
        st.error("⚠️ No API key found! Please set GROQ_API_KEY or GOOGLE_API_KEY in .env file.")
        st.stop()
        
    st.success("✅ System Online")
    
    # Debug mode
    debug_mode = st.checkbox("🔍 Debug Mode", value=False, help="Show retrieval details")

# Tabs
tab1, tab2 = st.tabs(["💬 Ask Bondhu", "🧮 Pension Calculator"])

# --- Tab 1: Chat Interface ---
with tab1:
    st.header("Ask your NPS Queries")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I am NPS Bondhu. Ask me anything about rules, withdrawal limits, or tax benefits!\n\n*Now with optimized retrieval for faster, more accurate responses!* ⚡"
        })

    # Create a container for chat messages
    chat_container = st.container()
    
    # Display chat history in the container
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input (this will automatically stay at bottom)
    if prompt := st.chat_input("Ex: What is the lock-in period for Tier I?"):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Check cache first
        cached_answer = get_cached_response(prompt)
        
        if cached_answer:
            # Use cached response (cached answer already includes source citation)
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(cached_answer)
                    st.caption("⚡ Instant response from cache")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": cached_answer
            })
            st.rerun()
        else:
            # Generate new response with sources
            with st.spinner("🔍 Searching official documents..."):
                try:
                    # Debug mode: show retrieval stats
                    if debug_mode:
                        with st.expander("🔍 Retrieval Debug Info", expanded=True):
                            docs_with_scores = get_retrieval_stats(prompt)
                    
                    # Get RAG chain with sources
                    rag_chain_func = get_rag_chain_with_sources(
                        streaming=enable_streaming,
                        search_type=search_type
                    )
                    
                    # Generate response with sources
                    if enable_streaming:
                        # Streaming response
                        with chat_container:
                            with st.chat_message("assistant"):
                                response_placeholder = st.empty()
                                
                                full_response = ""
                                
                                # Stream the answer
                                for chunk in rag_chain_func({"input": prompt}):
                                    full_response += chunk
                                    response_placeholder.markdown(full_response + "▌")
                                
                                # Get sources after streaming
                                source_docs = get_sources_from_query(prompt, search_type)
                                formatted_sources = format_sources_for_display(source_docs)
                                
                                # Append source citation to the answer
                                if formatted_sources:
                                    full_response_with_source = f"{full_response}\n\n{formatted_sources}"
                                else:
                                    full_response_with_source = full_response
                                
                                response_placeholder.markdown(full_response_with_source)
                        
                        answer = full_response_with_source
                    else:
                        # Non-streaming response
                        result = rag_chain_func({"input": prompt})
                        answer = result["answer"]
                        sources = result["sources"]
                        
                        # Append source citation to the answer
                        if sources:
                            answer_with_source = f"{answer}\n\n{sources}"
                        else:
                            answer_with_source = answer
                        
                        with chat_container:
                            with st.chat_message("assistant"):
                                st.markdown(answer_with_source)
                        
                        answer = answer_with_source
                    
                    # Cache the response (answer with source citation)
                    cache_response(prompt, answer)
                    
                    # Add assistant response to session state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer
                    })
                    
                    # Rerun to update the display
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    if debug_mode:
                        st.exception(e)


# --- Tab 2: Pension Calculator ---
with tab2:
    st.header("Pension Estimator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_age = st.number_input("Current Age", min_value=18, max_value=70, value=25)
        retirement_age = st.number_input("Retirement Age", min_value=18, max_value=75, value=60)
        contribution = st.number_input("Monthly Contribution (₹)", min_value=500, step=500, value=5000)
        return_rate = st.slider("Expected Annual Return (%)", min_value=5.0, max_value=15.0, value=10.0, step=0.1)
    
    if st.button("Calculate Pension"):
        result = calculate_pension_corpus(current_age, retirement_age, contribution, return_rate)
        
        if "error" in result:
            st.error(result["error"])
        else:
            with col2:
                st.subheader("Projection Summary")
                st.metric("Total Investment", f"₹ {result['total_investment']:,.2f}")
                st.metric("Total Corpus Created", f"₹ {result['total_corpus']:,.2f}")
                st.metric("Interest Earned", f"₹ {result['interest_earned']:,.2f}")
                
                st.divider()
                st.write("### At Retirement (Age 60+)")
                st.success(f"**Lumpsum Withdrawal (60%):** ₹ {result['lumpsum_withdrawal']:,.2f}")
                st.info(f"**Annuity Corpus (40%):** ₹ {result['annuity_corpus']:,.2f}")
                st.warning(f"**Est. Monthly Pension:** ₹ {result['estimated_monthly_pension']:,.2f} / month")

# Footer
st.divider()
st.caption("🚀 Optimized with: Smaller chunks (500 chars) • MMR search • Response caching • Streaming • Source citations")
