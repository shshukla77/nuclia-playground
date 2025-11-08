"""
Compare Strategies Page

Side-by-side comparison of search results across multiple strategies.
Helps users evaluate which strategy works best for their queries.
"""
import streamlit as st
from utils.session import (
    init_session_state,
    get_last_query,
    set_last_query,
    cache_comparison_results,
    get_cached_comparison_results,
    get_api_client
)
from utils.display import (
    render_comparison_results,
    render_error,
    format_result_count
)
from utils.api_client import safe_search

# Page configuration
st.set_page_config(
    page_title="Compare - Nuclia Search",
    page_icon="🔍",
    layout="wide"
)

# Initialize session
init_session_state()

# Header
st.title("🔍 Compare Search Strategies")
st.markdown("Run the same query across multiple strategies to compare quality")

# Sidebar - Strategy selection
with st.sidebar:
    st.header("Settings")
    
    st.markdown("""
    ### Selected Strategies
    Choose which strategies to compare:
    """)
    
    # Strategy checkboxes
    compare_semantic = st.checkbox("🧠 Semantic", value=True, help="Vector-based similarity")
    compare_hybrid = st.checkbox("🔀 Hybrid", value=True, help="Keyword + vector combined")
    compare_merged = st.checkbox("📊 Merged", value=True, help="Aggregated results")
    
    # Collect selected strategies
    selected_strategies = []
    if compare_semantic:
        selected_strategies.append("semantic")
    if compare_hybrid:
        selected_strategies.append("hybrid")
    if compare_merged:
        selected_strategies.append("merged")
    
    if len(selected_strategies) == 0:
        st.warning("⚠️ Select at least one strategy")
    
    st.divider()
    
    # Display options
    st.subheader("Display Options")
    
    max_results = st.slider(
        "Results per strategy",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of results to show for each strategy"
    )
    
    st.divider()
    
    # Cache info
    last_query = get_last_query()
    if last_query:
        st.caption("**Last Query**")
        st.code(last_query, language=None)

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Enter search query",
        placeholder="What would you like to search for?",
        help="Enter a question or keywords to search across strategies"
    )

with col2:
    st.write("")  # Spacer
    st.write("")  # Spacer
    search_button = st.button("🔍 Compare", type="primary", use_container_width=True)

# Execute comparison
if search_button and query:
    if len(selected_strategies) == 0:
        st.error("Please select at least one strategy to compare")
    else:
        # Store query
        set_last_query(query)
        
        # Check cache first
        cached_results = get_cached_comparison_results(query)
        
        if cached_results:
            st.info("📦 Using cached results")
            results_by_strategy = cached_results
        else:
            # Execute searches
            client = get_api_client()
            results_by_strategy = {}
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, strategy in enumerate(selected_strategies):
                status_text.text(f"Searching with {strategy} strategy...")
                
                response = safe_search(client, query, strategy)
                
                if response["success"]:
                    results_by_strategy[strategy] = response["results"]
                else:
                    results_by_strategy[strategy] = []
                    st.warning(f"❌ {strategy.title()} failed: {response['error']}")
                
                # Update progress
                progress_bar.progress((i + 1) / len(selected_strategies))
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Cache results
            cache_comparison_results(query, results_by_strategy)
        
        # Display results summary
        st.divider()
        st.subheader("Results Overview")
        
        summary_cols = st.columns(len(selected_strategies))
        for col, strategy in zip(summary_cols, selected_strategies):
            with col:
                result_count = len(results_by_strategy.get(strategy, []))
                st.metric(
                    strategy.title(),
                    format_result_count(result_count),
                    delta=None
                )
        
        # Display comparison
        st.divider()
        st.subheader("📊 Strategy Results")
        
        # Filter results to only show selected strategies
        filtered_results = {
            strategy: results_by_strategy[strategy]
            for strategy in selected_strategies
            if strategy in results_by_strategy
        }
        
        if filtered_results:
            render_comparison_results(filtered_results, max_per_strategy=max_results)
        else:
            st.info("No results to display")
        
        # Analysis insights
        st.divider()
        st.subheader("💡 Analysis Insights")
        
        # Calculate basic statistics
        total_results = sum(len(results_by_strategy.get(s, [])) for s in selected_strategies)
        
        if total_results > 0:
            # Find strategy with most results
            max_strategy = max(
                selected_strategies,
                key=lambda s: len(results_by_strategy.get(s, []))
            )
            max_count = len(results_by_strategy.get(max_strategy, []))
            
            # Find strategy with highest average score
            avg_scores = {}
            for strategy in selected_strategies:
                results = results_by_strategy.get(strategy, [])
                if results:
                    avg_score = sum(r.get("score", 0) for r in results) / len(results)
                    avg_scores[strategy] = avg_score
            
            if avg_scores:
                best_quality_strategy = max(avg_scores.keys(), key=lambda s: avg_scores[s])
                best_avg_score = avg_scores[best_quality_strategy]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"""
                    **Most Results**: {max_strategy.title()}  
                    Found {max_count} result{'s' if max_count != 1 else ''}
                    """)
                
                with col2:
                    st.info(f"""
                    **Highest Avg Score**: {best_quality_strategy.title()}  
                    Average: {best_avg_score:.3f}
                    """)
            
            # Overlap analysis
            if len(selected_strategies) >= 2:
                st.markdown("**Result Overlap**")
                
                # Check if any results appear in multiple strategies
                all_sources = {}
                for strategy in selected_strategies:
                    results = results_by_strategy.get(strategy, [])
                    for result in results:
                        source = result.get("source", "")
                        if source not in all_sources:
                            all_sources[source] = []
                        all_sources[source].append(strategy)
                
                # Count overlaps
                overlap_count = sum(1 for strategies in all_sources.values() if len(strategies) > 1)
                
                if overlap_count > 0:
                    st.success(f"✅ {overlap_count} result{'s' if overlap_count != 1 else ''} appear in multiple strategies")
                else:
                    st.warning("⚠️ No overlapping results between strategies")
        
        else:
            st.warning("No results found for any strategy. Try a different query.")

elif search_button:
    st.warning("Please enter a search query")

# Help section
if not query:
    st.divider()
    st.markdown("""
    ### How to Use
    
    1. **Select Strategies**: Choose which strategies to compare from the sidebar
    2. **Enter Query**: Type your search query in the input box above
    3. **Compare**: Click the Compare button to run searches
    4. **Analyze**: Review results side-by-side and check the insights
    
    ### Tips
    
    - Try the same query with different strategy combinations
    - Use the slider to adjust how many results are shown
    - Results are cached - re-running the same query is instant
    - Look for overlap to find consistently relevant results
    
    ### Example Queries
    
    - "What is retrieval-augmented generation?"
    - "How do vector databases work?"
    - "Explain semantic search techniques"
    - "Machine learning best practices"
    """)

# Footer
st.divider()
client = get_api_client()
st.caption(f"Comparing {len(selected_strategies)} strateg{'ies' if len(selected_strategies) != 1 else 'y'} • API: {client.base_url}")
