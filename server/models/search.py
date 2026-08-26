from pydantic import BaseModel, Field
from typing import List

class SearchRequest(BaseModel):
    idea: str = Field(..., min_length=1, description="The startup idea to validate")

class SearchResultItem(BaseModel):
    title: str
    url: str
    content: str

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
