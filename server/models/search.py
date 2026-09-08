
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from server.agents.web_search_agent import run_web_search_agent


router = APIRouter(
    prefix="/api",
    tags=["Search"],
)


class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


@router.post("/search")
async def search(request: SearchRequest):
    """
    Search the web for information related to a startup idea.
    """

    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    try:
        results = await run_web_search_agent(
            query=request.query.strip(),
            max_results=request.max_results or 5,
        )

        return {
            "query": request.query,
            "results": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}",
        )
