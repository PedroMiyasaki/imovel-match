from pydantic_ai import Agent
from dotenv import load_dotenv
from app.prompts.real_estate_prompts_fixed import system_prompt
from app.models.real_estate_models import RealStateAgentOutput
from app.models.user_models import UserInput


load_dotenv()


real_state_agent = Agent(
    "openai:o4-mini-2025-04-16",
    deps_type=UserInput,
    system_prompt=system_prompt,
    output_type=RealStateAgentOutput,
    model_settings={
        "timeout": 60,
    }
)


# Delayed/Local imports
from app.tools import real_estate_tools
from app.prompts import real_estate_prompts_dynamic
