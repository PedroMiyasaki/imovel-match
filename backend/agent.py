# Import langchain packages
from langchain_anthropic import ChatAnthropic
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import custom variables, classes, and functions
from real_estate_system_prompt import REAL_ESTATE_SYSTEM_PROMPT
from real_estate_tools import (
    search_properties, 
    validate_budget, 
    get_location_info, 
    schedule_visit
)

# Instantiate the main function of agent.py
def main(input: str):
    # Instantiate the LLM
    llm = ChatAnthropic(model="claude-3-opus-20240229")

    # Load the tools
    tools = [
        StructuredTool.from_function(search_properties),
        StructuredTool.from_function(validate_budget),
        StructuredTool.from_function(get_location_info),
        StructuredTool.from_function(schedule_visit)
    ]

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", REAL_ESTATE_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    # Take conversation_id history # TODO: THIS IS CANVAS
    chat_history = [
            HumanMessage(content="Hi!"),
            AIMessage(content="Hello! How can I assist you today?"),
    ]

    # Make the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools,
        verbose=True
    )

    # Invoke the chain
    response = agent_executor.invoke(
        {
            "input": input,
            "chat_history": chat_history,
        }
    )

    # Show response
    print(response)


# Run as script
if __name__ == "__main__":
    main(input="Hi would like assistant on finding I place")
