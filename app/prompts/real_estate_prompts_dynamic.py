from pydantic_ai import RunContext
from app.models.user_models import UserInput
from app.agents.real_estate_agent import real_state_agent

@real_state_agent.system_prompt
async def add_user_name(ctx: RunContext[UserInput]) -> str:
    """
    Adds the user's name to the system prompt.
    """
    return f"\nThe user's name is {ctx.deps.user_name}."
