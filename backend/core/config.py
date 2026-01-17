"""
Configuration loading module.

Provides centralized configuration management for the system.
Handles path resolution and error handling for config files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    "simulation": {
        "seed": 42,
        "max_days": 120
    },
    "risk_weights": {
        "rule_weight": 0.6,
        "ml_weight": 0.4
    },
    "risk_thresholds": {
        "high": 70,
        "medium": 40
    },
    "model": {
        "type": "logistic"
    }
}


def get_config_path() -> Path:
    """
    Determines the config file path.
    
    Searches in order:
    1. Environment variable CONFIG_PATH (if set)
    2. configs/system_config.yaml relative to project root
    3. ../configs/system_config.yaml (for backend context)
    
    Returns:
        Path object to the config file
    """
    # Try relative to project root
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "configs" / "system_config.yaml"
    
    if config_path.exists():
        return config_path
    
    # Try relative to current file (backend context)
    alt_path = Path(__file__).parent.parent.parent / "configs" / "system_config.yaml"
    if alt_path.exists():
        return alt_path
    
    # Return expected path (will raise error in load_config if not found)
    return config_path


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Loads system configuration from YAML file.
    
    Falls back to default values if config file is not found.
    Merges loaded config with defaults to ensure all keys exist.
    
    Args:
        config_path: Optional explicit path to config file.
                     If None, uses get_config_path().
    
    Returns:
        Configuration dictionary with all required keys
        
    Example:
        >>> config = load_config()
        >>> print(config["risk_weights"]["rule_weight"])
        0.6
    """
    if config_path is None:
        config_path = get_config_path()
    
    try:
        with open(config_path, "r") as f:
            loaded = yaml.safe_load(f) or {}
    except FileNotFoundError:
        # Return defaults if config file doesn't exist
        return DEFAULT_CONFIG.copy()
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")
    
    # Merge with defaults (loaded values take precedence)
    config = DEFAULT_CONFIG.copy()
    for key, value in loaded.items():
        if isinstance(value, dict) and key in config:
            config[key] = {**config[key], **value}
        else:
            config[key] = value
    
    return config
