from pydantic_ai import Agent
from dotenv import load_dotenv
from app.prompts.real_estate_prompts import system_prompt
from app.models.real_estate_models import RealStateAgentOutput
from app.models.user_models import UserInput
from app.tools.real_estate_tools import search_properties

load_dotenv()

real_state_agent = Agent(
    "groq:llama-3.3-70b-versatile",
    deps_type=UserInput,
    system_prompt=system_prompt,
    output_type=RealStateAgentOutput,
    tools=[search_properties]
)
