import asyncio
import duckdb
from app.agents.real_estate_agent import real_state_agent
from app.models.user_models import UserInput
from app.utils.general import load_config
from pydantic_ai.messages import ToolCallPart


async def main():
    """
    Main function to run the chat interface for the real estate agent.
    """
    print("Real Estate Agent Chat")
    print("Type 'exit' to end the conversation.")
    print("--------------------")

    config = await load_config("config/config.yml")
    connection = duckdb.connect(config["database"])

    while True:
        try:
            user_input = str(input("You: "))
            if user_input.lower() == "exit":
                print("Exiting chat. Goodbye!")
                break

            if not user_input.strip():
                continue

            final_response = None
            async with real_state_agent.iter(user_input, deps=UserInput(connection=connection)) as agent_run:
                async for node in agent_run:
                    if real_state_agent.is_call_tools_node(node):
                        print("Agent is making a tool call:")
                        for tool_call in node.model_response.parts:
                            if isinstance(tool_call, ToolCallPart):
                                print(f"  - Tool: {tool_call.tool_name}")
                                print(f"    Args: {tool_call.args}")
            
            final_response = agent_run.result
            
            print("Agent:")
            if final_response:
                print(final_response.output)


        except (KeyboardInterrupt, EOFError):
            print("\nChat was stopped by the user")
            break
        
        #except Exception as e:
        #    print(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting chat. Goodbye!")
