from fastapi import APIRouter, HTTPException
from server.models.search import SearchRequest, SearchResponse

try:
    from server.agents import run_web_search_agent
except ImportError:
    try:
        from server.agents.web_search_agent import run_web_search_agent
    except ImportError:
        async def run_web_search_agent(idea: str, target_customer: str | None = None, validation_type: str = "all") -> dict:
            return {
                "results": [
                    {
                        "title": "Mock Results (Agent Not Found)",
                        "url": "https://example.com/mock",
                        "content": f"Mock data for idea: {idea} | customer: {target_customer} | focus: {validation_type}"
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
        agent_response = await run_web_search_agent(
            idea=request.idea.strip(),
            domain=request.domain.strip() if request.domain else None,
            target_customer=request.target_customer.strip() if request.target_customer else None,
            validation_type=request.validation_type or "all"
        )
        
        if not agent_response or "results" not in agent_response:
            return SearchResponse(results=[])
            
        return SearchResponse(**agent_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search agent failed to process the request.")
