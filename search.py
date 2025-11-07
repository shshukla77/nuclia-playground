from nuclia import sdk
from nucliadb_models.search import SearchRequest, FindRequest, SearchOptions, FindOptions, ResourceProperties


async def search_semantic(
    query: str,
    page_size: int = 5,
    min_score: float | None = None,
) -> list[dict]:
    """Semantic-only search using /search endpoint."""
    search_api = sdk.AsyncNucliaSearch()
    req = SearchRequest(
        query=query,
        top_k=page_size,
        show=[ResourceProperties.VALUES, ResourceProperties.EXTRA],
        features=[SearchOptions.SEMANTIC],
    )
    if min_score is not None:
        req.min_score = min_score

    res = await search_api.search(query=req)
    data = res.model_dump()
    results = []

    sentences = data.get("sentences", {}) or {}
    for result in sentences.get("results", []):
        results.append({
            "rid": result.get("rid"),
            "score": result.get("score"),
            "text": result.get("text"),
            "field": result.get("field"),
            "search_type": "semantic",
        })

    return results[:page_size]


async def search_hybrid(
    query: str,
    page_size: int = 5,
    min_score_semantic: float | None = None,
    min_score_bm25: float = 0.0,
) -> list[dict]:
    """Hybrid search: semantic + fulltext using /search endpoint."""
    search_api = sdk.AsyncNucliaSearch()

    min_score_dict = {}
    if min_score_semantic is not None:
        min_score_dict["semantic"] = min_score_semantic
    if min_score_bm25 > 0:
        min_score_dict["bm25"] = min_score_bm25

    req = SearchRequest(
        query=query,
        top_k=page_size * 2,
        show=[ResourceProperties.VALUES, ResourceProperties.EXTRA],
        features=[SearchOptions.SEMANTIC, SearchOptions.FULLTEXT],
    )
    if min_score_dict:
        req.min_score = min_score_dict

    res = await search_api.search(query=req)
    data = res.model_dump()

    results_map = {}
    for result_type in ["sentences", "fulltext"]:
        results_data = data.get(result_type, {}) or {}
        for result in results_data.get("results", []):
            key = f"{result.get('rid')}:{result.get('field')}:{result.get('index')}"
            if key in results_map:
                results_map[key]["score"] = max(results_map[key]["score"], result.get("score", 0))
            else:
                results_map[key] = {
                    "rid": result.get("rid"),
                    "score": result.get("score", 0),
                    "text": result.get("text", ""),
                    "field": result.get("field"),
                    "search_type": "hybrid",
                }

    sorted_results = sorted(results_map.values(), key=lambda x: x["score"], reverse=True)
    return sorted_results[:page_size]


async def search_merged(
    query: str = "Search query",
    page_size: int = 5,
    min_score: float | None = None,
) -> list[dict]:
    """Merged+ranked search using /find endpoint with rank fusion."""
    search_api = sdk.AsyncNucliaSearch()
    req = FindRequest(
        query=query,
        top_k=page_size,
        show=[ResourceProperties.VALUES, ResourceProperties.EXTRA],
        features=[FindOptions.SEMANTIC, FindOptions.KEYWORD],
    )
    if min_score is not None:
        req.min_score = min_score

    res = await search_api.find(query=req)
    data = res.model_dump()

    resources = data.get("resources") or {}
    paragraphs = []

    for rid, resource in resources.items():
        for field_id, field in (resource.get("fields") or {}).items():
            for paragraph in (field.get("paragraphs") or {}).values():
                paragraphs.append({
                    "rid": rid,
                    "score": paragraph.get("score"),
                    "text": paragraph.get("text"),
                    "field": field_id,
                    "search_type": "merged",
                })

    return paragraphs[:page_size]
