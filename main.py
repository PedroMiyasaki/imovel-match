import asyncio
import duckdb
import mlflow
from app.agents.real_estate_agent import real_state_agent
from app.agents.guard_rail_agent import guard_rail_agent
from app.models.user_models import UserInput
from app.utils.general import load_config
from pydantic_ai.messages import ToolCallPart


mlflow.pydantic_ai.autolog()
mlflow.set_experiment("imovel-match")


async def main(user_name: str = "Pedro", execution_mode: str = "default", use_guard_rail: bool = True):
    """
    Main function to run the chat interface for the real estate agent.
    """
    print("Real Estate Agent Chat")
    print("Type 'exit' to end the conversation.")
    print("--------------------")

    config = await load_config("config/config.yml")
    connection = duckdb.connect(config["database"])
    message_history = []

    while True:
        try:
            user_input = str(input("You: "))
            
            if user_input.lower() == "exit":
                print("Exiting chat. Goodbye!")
                break

            if not user_input.strip():
                continue

            if use_guard_rail:
                guard_rail_response = await guard_rail_agent.ainvoke({"input": user_input, "history": message_history})
                if guard_rail_response.rules_are_being_broken:
                    print("Agent: I'm sorry, I can only help with real estate inquiries.")
                    continue
            
            if execution_mode == "default":
                agent_response = await real_state_agent.run(user_input, deps=UserInput(connection=connection, user_name=user_name), message_history=message_history)

            elif execution_mode == "stream":
                print("Agent:")
                async with real_state_agent.run_stream(user_input, deps=UserInput(connection=connection, user_name=user_name), message_history=message_history) as stream:
                    print(await stream.get_output())

                agent_response = stream

            elif execution_mode == "debug":
                async with real_state_agent.iter(user_input, deps=UserInput(connection=connection, user_name=user_name), message_history=message_history) as agent_run:
                    async for node in agent_run:
                        if real_state_agent.is_call_tools_node(node):
                            for tool_call in node.model_response.parts:
                                if isinstance(tool_call, ToolCallPart) and tool_call.tool_name != "final_result":
                                    print("Agent is making a tool call:")
                                    print(f"  - Tool: {tool_call.tool_name}")
                                    print(f"    Args: {tool_call.args}")
                
                agent_response = agent_run.result
            
            if agent_response:
                message_history.extend(agent_response.new_messages())
                if execution_mode != "stream":
                    print("Agent:")
                    print(agent_response)


        except (KeyboardInterrupt, EOFError):
            print("\nChat was stopped by the user")
            break
        
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main(use_guard_rail=True))

    except KeyboardInterrupt:
        print("\nExiting chat. Goodbye!")
