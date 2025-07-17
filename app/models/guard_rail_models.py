from pydantic import BaseModel
from pydantic import Field

class GuardRailAgentOutput(BaseModel):
    rules_are_being_broken: bool = Field(..., description="Whether the rules are being broken")
