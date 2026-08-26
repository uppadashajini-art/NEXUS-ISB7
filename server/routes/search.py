from fastapi import APIRouter, HTTPException
from server.models.search import SearchRequest, SearchResponse

try:
    from server.agents import run_web_search_agent
except ImportError:
    # Fallback/Mock for when Member 2's code isn't merged yet
    # or the module is missing in the current branch context.
    async def run_web_search_agent(idea: str) -> dict:
        return {
            "results": [
                {
                    "title": "Mock Results (Agent Not Found)",
                    "url": "https://example.com/mock",
                    "content": f"Mock data for idea: {idea}"
                }
            ]
        }

router = APIRouter()

@router.post("/api/search", response_model=SearchResponse)
async def search_idea(request: SearchRequest):
    # Validation for empty or just whitespace strings
    if not request.idea.strip():
        raise HTTPException(status_code=400, detail="Idea cannot be empty or just whitespace.")
    
    # Validation for very short input
    if len(request.idea.strip()) < 3:
        raise HTTPException(status_code=400, detail="Idea is too short to validate.")
    
    try:
        agent_response = await run_web_search_agent(request.idea)
        
        if not agent_response or "results" not in agent_response:
            return SearchResponse(results=[])
            
        return SearchResponse(**agent_response)
        
    except Exception as e:
        # According to Member 2, their code shouldn't raise unhandled exceptions,
        # but it's best practice for the API to have a safety net.
        raise HTTPException(status_code=500, detail="Search agent failed to process the request.")
