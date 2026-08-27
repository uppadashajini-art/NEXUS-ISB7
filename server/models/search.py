from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    idea: str = Field(..., min_length=1, description="The startup idea to validate")
    domain: Optional[str] = Field(default=None, description="Optional startup domain / industry")
    target_customer: Optional[str] = Field(default=None, description="Optional target customer segment")
    validation_type: Optional[str] = Field(default="all", description="Validation focus area: all, market, competition, customers, business, risks")

class SearchResultItem(BaseModel):
    title: str
    url: str
    content: str

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
