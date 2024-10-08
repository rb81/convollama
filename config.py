import yaml
from typing import Dict, Any

# Configure logging
import logging
logger = logging.getLogger(__name__)

def load_config(config_file: str) -> Dict[str, Any]:
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        validate_config(config)
        logger.info(f"Configuration loaded successfully from {config_file}")
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        raise
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_file}")
        raise

def validate_config(config: Dict[str, Any]):
    required_keys = ['moderator_model', 'ollama_host', 'save_path', 'available_models']
    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required configuration key: {key}")
            raise ValueError(f"Missing required configuration key: {key}")
    
    if not isinstance(config['save_path'], str):
        logger.error("save_path must be a string")
        raise ValueError("save_path must be a string")

    logger.info("Configuration validated successfully")