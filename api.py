from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from search import search_semantic, search_hybrid, search_merged

app = FastAPI()

class SearchQuery(BaseModel):
    query: str
    search_type: Optional[str] = "merged"

class SearchResult(BaseModel):
    text: str
    score: float
    source: str

@app.post("/search", response_model=List[SearchResult])
async def search(query: SearchQuery):
    if query.search_type == "semantic":
        results = await search_semantic(query.query)
    elif query.search_type == "hybrid":
        results = await search_hybrid(query.query)
    elif query.search_type == "merged":
        results = await search_merged(query.query)
    else:
        raise HTTPException(status_code=422, detail="Invalid search_type")
    
    return [SearchResult(text=r.get('text', ''), score=r.get('score', 0.0), source=r.get('field', '')) for r in results]
