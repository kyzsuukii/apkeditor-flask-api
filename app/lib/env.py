# -*- coding: utf-8 -*-

"""

Copyright (c) 2024 Dwiky Rizky Ananditya

All rights reserved.


This code is licensed under the MIT License.

You may obtain a copy of the License at

https://opensource.org/licenses/MIT

"""

import os
from typing import Any, Optional
from pathlib import Path
from dotenv import load_dotenv, set_key


class EnvLoader:
    def __init__(self, env_path: str = ".env"):
        """Initialize environment loader.

        Args:
            env_path: Path to .env file (default: ".env")
        """
        self._env_path = Path(env_path)

    def load(self) -> None:
        """Load environment variables from .env file."""
        load_dotenv(self._env_path)

    def get(self, key: str, default: Any = None) -> Optional[str]:
        """Get environment variable value.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.environ.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set environment variable.

        Args:
            key: Environment variable name
            value: Value to set
        """
        os.environ[key] = value
        set_key(self._env_path, key, value)

    def required(self, key: str) -> str:
        """Get required environment variable or raise error.

        Args:
            key: Environment variable name

        Returns:
            Environment variable value

        Raises:
            ValueError: If environment variable not found
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required environment variable '{key}' not found")
        return value
