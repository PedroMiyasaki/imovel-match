# Imóveis AI Agent 🏠🤖

An intelligent real estate assistant built with Pydantic AI that simulates a "corretor de imóveis" (real estate agent) to help users find their ideal properties in Brazil.

## 🎯 Purpose

This AI-powered agent streamlines the property search process by guiding users through their preferences and requirements, making property hunting more efficient and personalized. It serves as a virtual real estate agent, helping users discover properties that match their specific criteria.

## 🚀 Key Features

-   **Interactive Conversation**: Engages users in a natural conversation to gather their property requirements.
-   **Intelligent Slot Filling**: Dynamically identifies and fills in missing details about user preferences (e.g., budget, location, property type).
-   **Guard Rail System**: Ensures the conversation stays on topic and handles irrelevant user inputs gracefully.
-   **DuckDB Integration**: Stores and queries property data efficiently using an in-memory database.
-   **Telegram Bot Interface**: Allows users to interact with the agent through a familiar messaging platform.
-   **Extensible Tool System**: Easily add new tools to expand the agent's capabilities (e.g., scheduling, favorites).

## 🛠️ Technologies

-   **Pydantic AI**: Core framework for building the AI agent.
-   **DuckDB**: For efficient, in-memory database management.
-   **Telegram Bot**: As the primary user interface.
-   **Pandas & NumPy**: For data manipulation and analysis.
-   **Pytest**: For robust testing of all components.
-   **Ruff**: For code linting and formatting.

##  Project Structure

The project is organized into the following directories:

-   `app/`: Contains the core application logic.
    -   `agents/`: Defines the AI agents (e.g., `RealEstateAgent`, `GuardRailAgent`).
    -   `models/`: Pydantic models for data validation and structure.
    -   `prompts/`: Stores the prompts used to guide the language model.
    -   `tools/`: Implements the tools the agent can use (e.g., database queries).
    -   `utils/`: miscellaneous utility functions.
-   `config/`: Configuration files (e.g., `config.yml`).
-   `db/`: Holds the database files.
-   `tests/`: Contains all the tests for the project.

## 🤝 Contributing

Contributions are welcome! Feel free to:

-   Report bugs
-   Suggest new features
-   Submit pull requests

## 📝 License

MIT License
