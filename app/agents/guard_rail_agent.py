from pydantic_ai import Agent
from dotenv import load_dotenv
from app.prompts.guard_rail_prompts import system_prompt
from app.models.guard_rail_models import GuardRailAgentOutput


load_dotenv()


guard_rail_agent = Agent(
    "groq:llama-3.3-70b-versatile",
    deps_type=str,
    system_prompt=system_prompt,
    output_type=GuardRailAgentOutput,
    model_settings={
        "temperature": 0,
        "max_tokens": 100,
        "timeout": 60,
    }
)
