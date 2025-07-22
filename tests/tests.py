import pytest
import sys
import os
from pydantic_ai.messages import ToolCallPart
import duckdb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.guard_rail_agent import guard_rail_agent
from app.agents.real_estate_agent import real_state_agent
from app.models.user_models import UserInput


connection = duckdb.connect("tests/test_db.db")


class TestRealEstateAgent:
    """
    Tests the imovel-match application.

    Tests:
    1. test_guard_rail_agent: Tests the guard rail agent.
    2. test_real_estate_agent: Tests the real estate agent.
    3. test_search_properties: Tests the search_properties tool.
    4. test_get_property_slots: Tests the get_property_slots tool.
    5. test_book_property_slot: Tests the book_property_slot tool.
    6. test_cancel_property_slot: Tests the cancel_property_slot tool.
    """
    @pytest.mark.parametrize("user_input, expected_result", [
        ("Can you do my math homework?", True),
        ("Can you help me find a house?", False)
    ])
    def test_guard_rail_agent(self, user_input:str , expected_result:bool):
        """
        Tests the guard rail agent.
        """
        result = guard_rail_agent.run_sync(user_input)
        assert result.output.rules_are_being_broken == expected_result


    @pytest.mark.parametrize("user_input", [
        ("Hi there!"),
    ])
    @pytest.mark.asyncio
    async def test_real_estate_agent(self, user_input:str):
        """
        Tests the real estate agent without any tool calls
        """
        tool_names = []
        custom_tools = ["search_properties", "get_property_slots", "book_property_slot", "cancel_property_slot"]
        async with real_state_agent.iter(user_input, deps=UserInput(connection=connection, user_name="Alex")) as agent_run:
            async for node in agent_run:
                if real_state_agent.is_call_tools_node(node):
                    for tool_call in node.model_response.parts:
                        if isinstance(tool_call, ToolCallPart) :
                            tool_names.append(tool_call.tool_name)
        
        assert not any(tool in tool_names for tool in custom_tools)


    @pytest.mark.parametrize("user_input, makes_tool_call, returns_properties", [
        ("Eu gostaria de uma casa com 2 quartos em Curitiba", True, True),
        ("Eu gostaria de uma casa com 1 quarto e 1 banheiro em Pindamonhangaba", True, False),
        ("Eu gostaria de uma casa em Curitiba", True, False),
    ])
    @pytest.mark.asyncio
    async def test_search_properties(self, user_input:str, makes_tool_call:bool, returns_properties:bool):
        """
        Tests the search_properties tool.
        """
        tool_names = []
        async with real_state_agent.iter(user_input, deps=UserInput(connection=connection, user_name="Alex")) as agent_run:
            async for node in agent_run:
                if real_state_agent.is_call_tools_node(node):
                    for tool_call in node.model_response.parts:
                        if isinstance(tool_call, ToolCallPart) :
                            tool_names.append(tool_call.tool_name)

        if makes_tool_call:
            assert "search_properties" in tool_names, "Tool call was not made"
            
            if returns_properties:
                markdown_result = agent_run.result.output.properties
                n_returned_properties = len(markdown_result.strip().split('\n')) - 2
                assert n_returned_properties > 0, "No properties were returned"

        else:
            assert "search_properties" not in tool_names, "Tool call was made"


    @pytest.mark.parametrize("user_input, makes_tool_call, returns_slots", [
        ("Quais os horários para visitar o imóvel com id 'abcfoo42'?", True, True),
        ("Quais os horários para visitar o imóvel '999999'?", True, False),
        ("Quais os horários para visitar o imóvel?", False, False),
    ])
    @pytest.mark.asyncio
    async def test_get_property_slots(self, user_input:str, makes_tool_call:bool, returns_slots:bool):
        """
        Tests the get_property_slots tool.
        """
        tool_names = []
        async with real_state_agent.iter(user_input, deps=UserInput(connection=connection, user_name="Alex")) as agent_run:
            async for node in agent_run:
                if real_state_agent.is_call_tools_node(node):
                    for tool_call in node.model_response.parts:
                        if isinstance(tool_call, ToolCallPart) :
                            tool_names.append(tool_call.tool_name)
        
        if makes_tool_call:
            assert "get_property_slots" in tool_names, "Tool call was not made"
            
            if returns_slots:
                markdown_result = agent_run.result.output.slots
                n_slots = len(markdown_result.strip().split('\n')) - 2
                assert n_slots > 0
                
        else:
            assert "get_property_slots" not in tool_names, "Tool call was made"


    @pytest.mark.parametrize("user_input, makes_tool_call", [
        ("Gostaria de agendar uma visita para o imóvel 'abcfoo42' no dia 2024-12-25 as 10 da manhã.", True),
        ("Quero agendar uma visita para o imovel de id '999999' as 10 da manhã.", False),
    ])
    @pytest.mark.asyncio
    async def test_book_property_slot(self, user_input:str, makes_tool_call:bool):
        """
        Tests the book_property_slot tool.
        """
        tool_names = []
        async with real_state_agent.iter(user_input, deps=UserInput(connection=connection, user_name="Alex")) as agent_run:
            async for node in agent_run:
                if real_state_agent.is_call_tools_node(node):
                    for tool_call in node.model_response.parts:
                        if isinstance(tool_call, ToolCallPart) :
                            tool_names.append(tool_call.tool_name)
        
        if makes_tool_call:
            assert "book_property_slot" in tool_names, "Tool call was not made"

        else:
            assert "book_property_slot" not in tool_names, "Tool call was made"


    @pytest.mark.parametrize("user_input, makes_tool_call", [
        ("Preciso cancelar minha visita ao imóvel 'xyzbar99' que eu marquei no dia 2024-12-25 as 10 da manhã.", True),
        ("Preciso cancelar minha visita ao imóvel '999999' que eu marquei no dia 2024-12-25 as 8 da manhã.", False),
    ])
    @pytest.mark.asyncio
    async def test_cancel_property_slot(self, user_input:str, makes_tool_call:bool):
        """
        Tests the cancel_property_slot tool.
        """
        tool_names = []
        async with real_state_agent.iter(user_input, deps=UserInput(connection=connection, user_name="Alex")) as agent_run:
            async for node in agent_run:
                if real_state_agent.is_call_tools_node(node):
                    for tool_call in node.model_response.parts:
                        if isinstance(tool_call, ToolCallPart) :
                            tool_names.append(tool_call.tool_name)
        
        if makes_tool_call:
            assert "cancel_property_slot" in tool_names, "Tool call was not made"

        else:
            assert "cancel_property_slot" not in tool_names, "Tool call was made"
