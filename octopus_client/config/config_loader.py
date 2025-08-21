# =============================================================================
# 🐙 OCTOPUS CLIENT CONFIGURATION LOADER
# =============================================================================
"""
Configuration loader that determines which configuration to use based on
command line arguments or environment variables.

Usage:
    python main.py          # Loads development config
    python main.py dev      # Loads development config  
    python main.py prod     # Loads production config
"""

import sys
import os
import logging
from typing import Type, Union, Optional

from .config_base import BaseConfig
from .config_dev import DevelopmentConfig
from .config_prod import ProductionConfig


# Global variable to store the current configuration
_current_config: Union[Type[BaseConfig], None] = None


def determine_environment() -> str:
    """
    Determine the environment from command line arguments or environment variables.
    
    Priority:
    1. Command line argument (python main.py prod)
    2. Environment variable OCTOPUS_ENV
    3. Default to 'dev'
    
    Returns:
        Environment name ('dev' or 'prod')
    """
    # Check command line arguments
    if len(sys.argv) > 1:
        env_arg = sys.argv[1].lower()
        if env_arg in ['prod', 'production']:
            return 'prod'
        elif env_arg in ['dev', 'development']:
            return 'dev'
        elif env_arg in ['--help', '-h', 'help']:
            print_usage()
            sys.exit(0)
        else:
            print(f"Warning: Unknown environment '{env_arg}', defaulting to 'dev'")
            print("Valid environments: dev, prod")
    
    # Check environment variable
    env_var = os.getenv('OCTOPUS_ENV', '').lower()
    if env_var in ['prod', 'production']:
        return 'prod'
    elif env_var in ['dev', 'development']:
        return 'dev'
    
    # Default to development
    return 'dev'


def load_config(environment: Optional[str] = None) -> Type[BaseConfig]:
    """
    Load configuration based on environment.
    
    Args:
        environment: Environment name ('dev' or 'prod'). If None, auto-determine.
        
    Returns:
        Configuration class
        
    Raises:
        ValueError: If unknown environment is specified
    """
    global _current_config
    
    if environment is None:
        environment = determine_environment()
    
    environment = environment.lower()
    
    if environment in ['dev', 'development']:
        _current_config = DevelopmentConfig
        config_name = "Development"
    elif environment in ['prod', 'production']:
        _current_config = ProductionConfig
        config_name = "Production"
    else:
        raise ValueError(f"Unknown environment: {environment}. Valid options: dev, prod")
    
    # Validate the configuration
    validation_errors = _current_config.validate_config()
    if validation_errors:
        print(f"Configuration validation errors for {config_name}:")
        for error in validation_errors:
            print(f"  - {error}")
        sys.exit(1)
    
    
    return _current_config


def get_current_config() -> Type[BaseConfig]:
    """
    Get the currently loaded configuration.
    
    Returns:
        Current configuration class
        
    Raises:
        RuntimeError: If no configuration has been loaded yet
    """
    global _current_config
    
    if _current_config is None:
        # Auto-load configuration if not loaded yet
        load_config()
    
    return _current_config


def reload_config(environment: Optional[str] = None) -> Type[BaseConfig]:
    """
    Reload configuration (useful for runtime configuration changes).
    
    Args:
        environment: Environment name. If None, re-determine from current state.
        
    Returns:
        Reloaded configuration class
    """
    global _current_config
    _current_config = None
    return load_config(environment)


def print_usage():
    """Print usage information."""
    print("""
🐙 Octopus Client Configuration Usage:

Basic Usage:
    python main.py          # Loads development configuration
    python main.py dev      # Loads development configuration
    python main.py prod     # Loads production configuration

Environment Variable:
    set OCTOPUS_ENV=prod && python main.py    # Windows
    export OCTOPUS_ENV=prod && python main.py # Unix/Linux

Configuration Environments:
    dev/development  - Local development with verbose logging and frequent checks
    prod/production  - Optimized for production with minimal logging and efficiency

Examples:
    python main.py                    # Development mode
    python main.py dev                # Development mode
    python main.py prod               # Production mode
    python main.py --help             # Show this help
""")


def get_config_info() -> dict:
    """
    Get detailed information about the current configuration.
    
    Returns:
        Dictionary with configuration details
    """
    config = get_current_config()
    
    return {
        "environment": config.ENVIRONMENT,
        "debug": config.DEBUG,
        "server_url": getattr(config, 'SERVER_URL', 'Not configured'),
        "heartbeat_interval": config.HEARTBEAT_INTERVAL,
        "task_check_interval": config.TASK_CHECK_INTERVAL,
        "log_level": config.LOG_LEVEL,
        "log_file": config.LOG_FILE,
        "cache_ttl": config.CACHE_TTL,
        "username": config.USERNAME,
        "client_metadata": config.CLIENT_METADATA
    }


# Initialize configuration on module import
if _current_config is None:
    try:
        load_config()
    except Exception as e:
        print(f"Warning: Failed to auto-load configuration: {e}")
        print("Configuration will be loaded when first accessed.")
