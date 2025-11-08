"""
Nuclia Search UI - Main Application Entry Point

A Streamlit web interface for searching knowledge bases using different strategies.
Provides chat interface and comparison tool for evaluating search quality.

Pages:
- 💬 Chat: Interactive chat with search-powered responses
- 🔍 Compare: Side-by-side strategy comparison

Usage:
    streamlit run app.py
"""
import streamlit as st
from utils.session import init_session_state, get_api_client
from utils.display import show_api_health_indicator

# Page configuration
st.set_page_config(
    page_title="Nuclia Search UI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Main content
st.title("🔍 Nuclia Search UI")
st.markdown("### AI-Powered Knowledge Base Search")

# Welcome message
st.markdown("""
Welcome to the Nuclia Search UI! This application provides two ways to explore your knowledge base:

- **💬 Chat**: Ask questions and get search-powered answers with your choice of strategy
- **🔍 Compare**: Run the same query across multiple strategies to compare quality

Select a page from the sidebar to get started.
""")

# API Health Check
st.divider()
st.subheader("System Status")

client = get_api_client()
is_healthy = client.health_check()

show_api_health_indicator(is_healthy)

if not is_healthy:
    st.warning("""
    ⚠️ **API Server Not Running**
    
    The FastAPI backend is currently unavailable. Please start it with:
    
    ```bash
    uvicorn api:app --reload
    ```
    
    The server should be running at: `http://localhost:8000`
    """)
else:
    st.success("✅ Ready to search!")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    
    st.markdown("""
    ### Pages
    - **💬 Chat**: Interactive search interface
    - **🔍 Compare**: Strategy comparison tool
    
    ### Search Strategies
    - **Semantic**: Vector-based similarity
    - **Hybrid**: Combined keyword + vector
    - **Merged**: Aggregated results
    
    ### Getting Started
    1. Ensure API server is running
    2. Select a page from above
    3. Start searching!
    """)
    
    st.divider()
    
    # Configuration info
    st.caption("**API Endpoint**")
    st.code(client.base_url)
    
    st.caption("**Timeout**")
    st.code(f"{client.timeout}s")
