from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from app.prompts.guard_rail_prompts import system_prompt
from app.models.guard_rail_models import GuardRailAgentOutput


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
    ]
)
model = ChatGroq(model="llama3-70b-8192", temperature=0).with_structured_output(GuardRailAgentOutput)


guard_rail_agent = prompt | model
