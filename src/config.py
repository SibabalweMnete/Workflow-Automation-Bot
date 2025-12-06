"""Configuration management for the Workflow Automation Bot"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Config:
    """Manages configuration from JSON rules file"""

    def __init__(self, config_path: str = "config/rules.json"):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to configuration JSON file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}")
                self.config = self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            self.config = self._get_default_config()

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "csv": {
                "remove_duplicates": True,
                "handle_missing": "fill_zeros",
                "required_columns": ["id", "date", "value"],
                "date_format": "%Y-%m-%d",
            },
            "json": {
                "validate_schema": True,
                "flatten_nested": False,
                "required_fields": ["timestamp", "data"],
            },
            "excel": {
                "remove_duplicates": True,
                "handle_missing": "fill_zeros",
                "required_columns": ["id", "date", "value"],
            },
            "notifications": {
                "console": True,
                "log_file": True,
                "slack": False,
                "email": False,
            },
            "processing": {
                "max_retries": 3,
                "retry_delay": 5,
                "timeout_seconds": 300,
                "parallel_workers": 1,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self.config.get(key, default)

    def get_nested(self, *keys: str) -> Any:
        """Get nested configuration value"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def reload(self) -> None:
        """Reload configuration from file"""
        self.load_config()
        logger.info("Configuration reloaded")
