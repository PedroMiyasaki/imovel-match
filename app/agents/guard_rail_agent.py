from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.prompts.guard_rail_prompts import system_prompt
from app.models.guard_rail_models import GuardRailAgentOutput


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
    ]
)
model = ChatOpenAI(model="o4-mini-2025-04-16").with_structured_output(GuardRailAgentOutput)


guard_rail_agent = prompt | model
