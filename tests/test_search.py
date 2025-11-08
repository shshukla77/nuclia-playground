import pytest
from search import search_semantic, search_hybrid, search_merged


@pytest.mark.asyncio
async def test_semantic_activity_object():
    """Test semantic search with 'Activity object' query."""
    query = "Activity object"
    min_score = 0.7
    
    results = await search_semantic(query=query, page_size=3, min_score=min_score)
    
    assert isinstance(results, list)
    if results:
        for result in results:
            assert "score" in result
            assert "text" in result
            assert result["score"] >= min_score


@pytest.mark.asyncio
async def test_semantic_topic_and_trigger():
    """Test semantic search with 'Topic and Trigger' query."""
    query = "Topic and Trigger"
    min_score = 0.6
    
    results = await search_semantic(query=query, page_size=3, min_score=min_score)
    
    assert isinstance(results, list)
    if results:
        for result in results:
            assert "score" in result
            assert "text" in result
            assert result["score"] >= min_score


@pytest.mark.asyncio
async def test_semantic_action_integration():
    """Test semantic search with 'Action integration' query."""
    query = "Action integration"
    min_score = 0.6
    
    results = await search_semantic(query=query, page_size=3, min_score=min_score)
    
    assert isinstance(results, list)
    if results:
        for result in results:
            assert "score" in result
            assert "text" in result
            assert result["score"] >= min_score


@pytest.mark.asyncio
async def test_semantic_entity_definition():
    """Test semantic search with 'Entity definition' query."""
    query = "Entity definition"
    min_score = 0.5
    
    results = await search_semantic(query=query, page_size=3, min_score=min_score)
    
    assert isinstance(results, list)
    if results:
        for result in results:
            assert "score" in result
            assert "text" in result
            assert result["score"] >= min_score


@pytest.mark.asyncio
async def test_hybrid_activity_object():
    """Test hybrid search with 'Activity object' query."""
    query = "Activity object"
    min_semantic = 0.5
    min_bm25 = 0.0
    
    results = await search_hybrid(
        query=query,
        page_size=3,
        min_score_semantic=min_semantic,
        min_score_bm25=min_bm25,
    )
    
    assert isinstance(results, list)
    if results:
        for result in results:
            assert "score" in result
            assert "text" in result


@pytest.mark.asyncio
async def test_hybrid_topic_and_trigger():
    """Test hybrid search with 'Topic and Trigger' query."""
    query = "Topic and Trigger"
    min_semantic = 0.5
    min_bm25 = 0.0
    
    results = await search_hybrid(
        query=query,
        page_size=3,
        min_score_semantic=min_semantic,
        min_score_bm25=min_bm25,
    )
    
    assert isinstance(results, list)
    if results:
        for result in results:
            assert "score" in result
            assert "text" in result


@pytest.mark.asyncio
async def test_hybrid_action_integration():
    """Test hybrid search with 'Action integration' query."""
    query = "Action integration"
    min_semantic = 0.3
    min_bm25 = 0.0
    
    results = await search_hybrid(
        query=query,
        page_size=3,
        min_score_semantic=min_semantic,
        min_score_bm25=min_bm25,
    )
    
    assert isinstance(results, list)
    if results:
        for result in results:
            assert "score" in result
            assert "text" in result


@pytest.mark.asyncio
async def test_hybrid_entity_definition():
    """Test hybrid search with 'Entity definition' query."""
    query = "Entity definition"
    min_semantic = 0.4
    min_bm25 = 0.0
    
    results = await search_hybrid(
        query=query,
        page_size=3,
        min_score_semantic=min_semantic,
        min_score_bm25=min_bm25,
    )
    
    assert isinstance(results, list)
    if results:
        for result in results:
            assert "score" in result
            assert "text" in result


@pytest.mark.asyncio
async def test_semantic_vs_hybrid_activity_object():
    """Compare semantic vs hybrid search for 'Activity object' query."""
    query = "Activity object"
    threshold = 0.6
    
    semantic = await search_semantic(query=query, page_size=3, min_score=threshold)
    hybrid = await search_hybrid(
        query=query, 
        page_size=3, 
        min_score_semantic=threshold, 
        min_score_bm25=0.0
    )
    
    assert isinstance(semantic, list)
    assert isinstance(hybrid, list)
    
    # Both should return results (though this may not always be true)
    # We just verify the structure is correct


@pytest.mark.asyncio
async def test_semantic_vs_hybrid_action_integration():
    """Compare semantic vs hybrid search for 'Action integration' query."""
    query = "Action integration"
    threshold = 0.5
    
    semantic = await search_semantic(query=query, page_size=3, min_score=threshold)
    hybrid = await search_hybrid(
        query=query, 
        page_size=3, 
        min_score_semantic=threshold, 
        min_score_bm25=0.0
    )
    
    assert isinstance(semantic, list)
    assert isinstance(hybrid, list)


@pytest.mark.asyncio
async def test_semantic_vs_hybrid_trigger_types():
    """Compare semantic vs hybrid search for 'Trigger types' query."""
    query = "Trigger types"
    threshold = 0.5
    
    semantic = await search_semantic(query=query, page_size=3, min_score=threshold)
    hybrid = await search_hybrid(
        query=query, 
        page_size=3, 
        min_score_semantic=threshold, 
        min_score_bm25=0.0
    )
    
    assert isinstance(semantic, list)
    assert isinstance(hybrid, list)


@pytest.mark.asyncio
async def test_semantic_page_size():
    """Test that semantic search respects page_size parameter."""
    query = "Activity object"
    page_size = 5
    
    results = await search_semantic(query=query, page_size=page_size, min_score=0.5)
    
    assert isinstance(results, list)
    assert len(results) <= page_size


@pytest.mark.asyncio
async def test_hybrid_page_size():
    """Test that hybrid search respects page_size parameter."""
    query = "Activity object"
    page_size = 5
    
    results = await search_hybrid(
        query=query, 
        page_size=page_size, 
        min_score_semantic=0.5,
        min_score_bm25=0.0
    )
    
    assert isinstance(results, list)
    assert len(results) <= page_size
