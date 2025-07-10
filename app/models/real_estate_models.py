from pydantic import BaseModel
from pydantic import Field
from typing import Optional

class RealStateAgentOutput(BaseModel):
    response: str = Field(..., description="Agent response")
    properties: Optional[str] = Field(None, description="Properties found by the `search_properties` tool")
