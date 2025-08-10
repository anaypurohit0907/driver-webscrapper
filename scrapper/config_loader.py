import json
import os

def load_config(config_path):
    """
    Load configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Parsed configuration dictionary.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as file:
        return json.load(file)
