import yaml

async def load_config(config_path: str):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config
