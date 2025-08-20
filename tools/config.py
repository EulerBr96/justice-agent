"""
Configuration management for Justice Agent tools.
Handles environment variables, settings, and default configurations.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class APIConfig:
    """Configuration for Web Justice API."""
    base_url: str
    api_key: str
    timeout: float = 30.0
    max_retries: int = 3


@dataclass
class PollingConfig:
    """Configuration for polling behavior."""
    initial_interval: float = 2.0
    max_interval: float = 30.0
    backoff_multiplier: float = 1.5
    max_wait_time: float = 900.0  # 15 minutes
    timeout_buffer: float = 30.0


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = False
    log_file_path: Optional[str] = None


@dataclass
class ToolsConfig:
    """Main configuration for Justice Agent tools."""
    api: APIConfig
    polling: PollingConfig
    logging: LoggingConfig
    
    @classmethod
    def from_environment(cls) -> 'ToolsConfig':
        """
        Create configuration from environment variables.
        
        Returns:
            ToolsConfig instance with values from environment
            
        Raises:
            ValueError: If required environment variables are missing
        """
        # Required environment variables
        api_key = os.getenv('WEB_JUSTICE_API_KEY')
        if not api_key:
            raise ValueError(
                "WEB_JUSTICE_API_KEY environment variable is required. "
                "Please set it to your Web Justice API key."
            )
        
        # API configuration
        api_config = APIConfig(
            base_url=os.getenv('WEB_JUSTICE_API_URL', 'http://localhost:8000'),
            api_key=api_key,
            timeout=float(os.getenv('WEB_JUSTICE_API_TIMEOUT', '30.0')),
            max_retries=int(os.getenv('WEB_JUSTICE_API_MAX_RETRIES', '3'))
        )
        
        # Polling configuration
        polling_config = PollingConfig(
            initial_interval=float(os.getenv('POLLING_INITIAL_INTERVAL', '2.0')),
            max_interval=float(os.getenv('POLLING_MAX_INTERVAL', '30.0')),
            backoff_multiplier=float(os.getenv('POLLING_BACKOFF_MULTIPLIER', '1.5')),
            max_wait_time=float(os.getenv('POLLING_MAX_WAIT_TIME', '900.0')),
            timeout_buffer=float(os.getenv('POLLING_TIMEOUT_BUFFER', '30.0'))
        )
        
        # Logging configuration
        log_file = os.getenv('JUSTICE_TOOLS_LOG_FILE')
        logging_config = LoggingConfig(
            level=os.getenv('JUSTICE_TOOLS_LOG_LEVEL', 'INFO'),
            format=os.getenv('JUSTICE_TOOLS_LOG_FORMAT', 
                           "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            enable_file_logging=bool(log_file),
            log_file_path=log_file
        )
        
        return cls(
            api=api_config,
            polling=polling_config,
            logging=logging_config
        )


def setup_logging(config: LoggingConfig):
    """
    Configure logging based on the provided configuration.
    
    Args:
        config: Logging configuration
    """
    # Set logging level
    level = getattr(logging, config.level.upper(), logging.INFO)
    
    # Configure root logger
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(config.format))
    handlers.append(console_handler)
    
    # File handler if enabled
    if config.enable_file_logging and config.log_file_path:
        try:
            file_handler = logging.FileHandler(config.log_file_path)
            file_handler.setFormatter(logging.Formatter(config.format))
            handlers.append(file_handler)
        except Exception as e:
            logging.warning(f"Failed to setup file logging: {e}")
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format=config.format,
        handlers=handlers,
        force=True
    )


def get_default_config() -> ToolsConfig:
    """
    Get default configuration from environment variables.
    
    Returns:
        Default ToolsConfig instance
        
    Raises:
        ValueError: If required environment variables are missing
    """
    return ToolsConfig.from_environment()


def validate_config(config: ToolsConfig) -> Dict[str, Any]:
    """
    Validate configuration and return validation results.
    
    Args:
        config: Configuration to validate
        
    Returns:
        Dict with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Validate API configuration
    if not config.api.api_key:
        results["errors"].append("API key is required")
        results["valid"] = False
    
    if not config.api.base_url:
        results["errors"].append("API base URL is required")
        results["valid"] = False
    
    if config.api.timeout <= 0:
        results["warnings"].append("API timeout should be positive")
    
    # Validate polling configuration
    if config.polling.initial_interval <= 0:
        results["warnings"].append("Polling initial interval should be positive")
    
    if config.polling.max_interval < config.polling.initial_interval:
        results["warnings"].append("Max polling interval should be >= initial interval")
    
    if config.polling.max_wait_time <= 0:
        results["errors"].append("Max wait time must be positive")
        results["valid"] = False
    
    return results


# Global configuration instance
_config = None

def get_config() -> ToolsConfig:
    """
    Get the global configuration instance.
    
    Returns:
        ToolsConfig instance
    """
    global _config
    if _config is None:
        _config = get_default_config()
        # Setup logging with the configuration
        setup_logging(_config.logging)
    return _config


def set_config(config: ToolsConfig):
    """
    Set the global configuration instance.
    
    Args:
        config: Configuration to set
    """
    global _config
    _config = config
    setup_logging(config.logging)


# Environment variable documentation
ENV_VARS_HELP = """
Justice Agent Tools Environment Variables:

Required:
  WEB_JUSTICE_API_KEY           API key for Web Justice service

Optional:
  WEB_JUSTICE_API_URL           API base URL (default: http://localhost:8000)
  WEB_JUSTICE_API_TIMEOUT       Request timeout in seconds (default: 30.0)
  WEB_JUSTICE_API_MAX_RETRIES   Max retry attempts (default: 3)
  
  POLLING_INITIAL_INTERVAL      Initial polling interval in seconds (default: 2.0)
  POLLING_MAX_INTERVAL          Maximum polling interval in seconds (default: 30.0)
  POLLING_BACKOFF_MULTIPLIER    Exponential backoff multiplier (default: 1.5)
  POLLING_MAX_WAIT_TIME         Maximum total wait time in seconds (default: 900.0)
  POLLING_TIMEOUT_BUFFER        Buffer before timeout in seconds (default: 30.0)
  
  JUSTICE_TOOLS_LOG_LEVEL       Logging level (default: INFO)
  JUSTICE_TOOLS_LOG_FILE        Log file path (optional)
  JUSTICE_TOOLS_LOG_FORMAT      Log message format (optional)
"""