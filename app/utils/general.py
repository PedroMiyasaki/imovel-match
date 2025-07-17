import yaml
import duckdb

async def load_config(config_path: str):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config

async def check_if_property_exists(connection: duckdb.DuckDBPyConnection, property_id: str) -> bool:
    result = connection.execute(f"SELECT EXISTS(SELECT 1 FROM property_slots WHERE property_id = '{property_id}') AS exists").fetchone()
    return bool(result[0])
