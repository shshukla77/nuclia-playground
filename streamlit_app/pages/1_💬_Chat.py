"""
Chat Interface Page

Interactive chat interface with search-powered responses.
Users can ask questions and see results from their chosen strategy.
"""
import streamlit as st
from utils.session import (
    init_session_state,
    get_messages,
    add_message,
    clear_messages,
    get_strategy,
    set_strategy,
    get_api_client
)
from utils.display import (
    render_search_results,
    render_error
)
from utils.api_client import safe_search

# Page configuration
st.set_page_config(
    page_title="Chat - Nuclia Search",
    page_icon="💬",
    layout="wide"
)

# Initialize session
init_session_state()

# Header
st.title("💬 Chat Interface")
st.markdown("Ask questions and get search-powered answers")

# Sidebar - Strategy selector and controls
with st.sidebar:
    st.header("Settings")
    
    # Strategy selection
    strategy = st.selectbox(
        "Search Strategy",
        options=["semantic", "hybrid", "merged"],
        index=["semantic", "hybrid", "merged"].index(get_strategy()),
        help="Choose how to search the knowledge base"
    )
    
    # Update strategy in session
    if strategy != get_strategy():
        set_strategy(strategy)
    
    st.divider()
    
    # Strategy descriptions
    st.caption("**Strategy Info**")
    
    if strategy == "semantic":
        st.info("🧠 **Semantic**: Vector-based similarity search. Best for conceptual queries.")
    elif strategy == "hybrid":
        st.info("🔀 **Hybrid**: Combines keyword and vector search. Balanced approach.")
    else:  # merged
        st.info("📊 **Merged**: Aggregates results from multiple sources. Comprehensive coverage.")
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        clear_messages()
        st.rerun()
    
    # Message count
    message_count = len(get_messages())
    st.caption(f"Messages: {message_count}")

# Main chat area
chat_container = st.container()

# Display chat history
with chat_container:
    messages = get_messages()
    
    if len(messages) == 0:
        # Welcome message
        st.info("""
        👋 **Welcome to Chat!**
        
        Ask a question about your knowledge base and get search-powered answers.
        
        **Example queries:**
        - What is retrieval-augmented generation?
        - How do vector databases work?
        - Explain semantic search
        """)
    else:
        # Render existing messages
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            metadata = msg.get("metadata", {})
            
            if role == "user":
                # User query
                with st.chat_message("user"):
                    st.write(content)
            else:
                # Assistant response with results
                with st.chat_message("assistant"):
                    # Show metadata if available
                    if metadata:
                        strategy_used = metadata.get("strategy", "unknown")
                        result_count = metadata.get("result_count", 0)
                        st.caption(f"Strategy: {strategy_used} • Results: {result_count}")
                    
                    # Show response text
                    st.write(content)
                    
                    # Show search results if available
                    if "results" in metadata and metadata["results"]:
                        with st.expander("📄 View Search Results", expanded=False):
                            render_search_results(
                                metadata["results"],
                                max_results=5,
                                show_scores=True
                            )

# Chat input
user_query = st.chat_input("Ask a question...")

if user_query:
    # Add user message
    add_message("user", user_query)
    
    # Display user message immediately
    with chat_container:
        with st.chat_message("user"):
            st.write(user_query)
    
    # Execute search
    client = get_api_client()
    
    with st.spinner(f"Searching with {strategy} strategy..."):
        response = safe_search(client, user_query, strategy)
    
    # Process response
    if response["success"]:
        results = response["results"]
        result_count = len(results)
        
        # Create answer based on results
        if result_count > 0:
            answer = f"I found {result_count} result{'s' if result_count != 1 else ''} for your query."
        else:
            answer = "I couldn't find any results for your query. Try rephrasing or using a different strategy."
        
        # Add assistant message with results
        add_message(
            "assistant",
            answer,
            metadata={
                "strategy": strategy,
                "result_count": result_count,
                "results": results
            }
        )
        
        # Display assistant message
        with chat_container:
            with st.chat_message("assistant"):
                st.caption(f"Strategy: {strategy} • Results: {result_count}")
                st.write(answer)
                
                if results:
                    with st.expander("📄 View Search Results", expanded=True):
                        render_search_results(
                            results,
                            max_results=5,
                            show_scores=True
                        )
    
    else:
        # Error occurred
        error_msg = response["error"]
        
        # Add error message to chat
        add_message(
            "assistant",
            f"❌ Error: {error_msg}",
            metadata={"error": True}
        )
        
        # Display error
        with chat_container:
            with st.chat_message("assistant"):
                render_error(error_msg, "Search Failed")
    
    # Rerun to update chat display
    st.rerun()

# Footer
st.divider()
api_client = get_api_client()
st.caption(f"Using **{strategy}** strategy • API: {api_client.base_url}")
