import yaml
from typing import Dict, Any

def load_config(config_file: str) -> Dict[str, Any]:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    validate_config(config)
    return config

def validate_config(config: Dict[str, Any]):
    required_keys = ['moderator_model', 'participant_model', 'ollama_host', 'save_path', 'max_context_length']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    if not isinstance(config['max_context_length'], int) or config['max_context_length'] <= 0:
        raise ValueError("max_context_length must be a positive integer")
    
    if not isinstance(config['save_path'], str):
        raise ValueError("save_path must be a string")