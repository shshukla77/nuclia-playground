from search import search_semantic, search_hybrid, search_merged


async def test_semantic():
    """Test semantic search."""
    print("\n" + "=" * 80)
    print("Testing SEMANTIC Search")
    print("=" * 80)

    queries = [
        ("Activity object", 0.7),
        ("Topic and Trigger", 0.6),
        ("Action integration", 0.6),
        ("Entity definition", 0.5),
    ]

    for query, min_score in queries:
        print(f"\n🔍 Query: '{query}' (min_score: {min_score})")
        print("-" * 80)
        results = await search_semantic(query=query, page_size=3, min_score=min_score)

        if results:
            for i, r in enumerate(results, 1):
                score = r.get("score", 0)
                text = r.get("text", "N/A")[:180].strip()
                print(f"{i}. [{score:.4f}] {text}...")
        else:
            print("❌ No results found.")


async def test_hybrid():
    """Test hybrid search."""
    print("\n" + "=" * 80)
    print("Testing HYBRID Search (Semantic + Fulltext)")
    print("=" * 80)

    queries = [
        ("Activity object", 0.5, 0.0),
        ("Topic and Trigger", 0.5, 0.0),
        ("Action integration", 0.3, 0.0),
        ("Entity definition", 0.4, 0.0),
    ]

    for query, min_semantic, min_bm25 in queries:
        print(f"\n🔎 Query: '{query}'")
        print("-" * 80)
        results = await search_hybrid(
            query=query,
            page_size=3,
            min_score_semantic=min_semantic,
            min_score_bm25=min_bm25,
        )

        if results:
            for i, r in enumerate(results, 1):
                score = r.get("score", 0)
                text = r.get("text", "N/A")[:180].strip()
                print(f"{i}. [{score:.4f}] {text}...")
        else:
            print("❌ No results found.")


async def test_comparison():
    """Compare semantic vs hybrid search."""
    print("\n" + "=" * 80)
    print("COMPARISON: Semantic vs Hybrid")
    print("=" * 80)

    queries = [
        ("Activity object", 0.6),
        ("Action integration", 0.5),
        ("Trigger types", 0.5),
    ]

    for query, threshold in queries:
        print(f"\nQuery: '{query}'")
        semantic = await search_semantic(query=query, page_size=3, min_score=threshold)
        hybrid = await search_hybrid(query=query, page_size=3, min_score_semantic=threshold, min_score_bm25=0.0)
        
        sem_top = semantic[0].get("score", 0) if semantic else None
        hyb_top = hybrid[0].get("score", 0) if hybrid else None
        
        print(f"  Semantic: {len(semantic)} results, top score: {sem_top:.4f if sem_top else 'N/A'}")
        print(f"  Hybrid:   {len(hybrid)} results, top score: {hyb_top:.4f if hyb_top else 'N/A'}")


async def test_all():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("NUCLIA DOCUMENT SEARCH TESTS")
    print("=" * 80)
    await test_semantic()
    await test_hybrid()
    await test_comparison()
    print("\n" + "=" * 80)
    print("✅ Tests Complete!")
    print("=" * 80)
