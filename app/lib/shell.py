# -*- coding: utf-8 -*-

"""

Copyright (c) 2024 Dwiky Rizky Ananditya

All rights reserved.


This code is licensed under the MIT License.

You may obtain a copy of the License at

https://opensource.org/licenses/MIT

"""

from typing import Optional, Any, Dict, Union, List
import subprocess
import json


class Shell:
    def __init__(self, base_command: str) -> None:
        self.base_command: str = base_command
        self.trailer: str = ""
        self._last_result: Optional[subprocess.CompletedProcess] = None
        self._last_error: Optional[str] = None
        self._templates: Dict[str, List[str]] = {}
        self._current_template: Optional[str] = None

    def add_template(self, name: str, parts: List[str]) -> None:
        """Add a command template using array parts"""
        self._templates[name] = parts

    def use_template(self, name: str) -> None:
        """Set current template to use"""
        if name in self._templates:
            self._current_template = name
        else:
            raise KeyError(f"Template '{name}' not found")

    def format_command(self, **kwargs: str) -> str:
        """Format current template with provided arguments"""
        if not self._current_template:
            return self.base_command

        template_parts = self._templates[self._current_template]
        formatted_parts = []

        for part in template_parts:
            try:
                formatted_parts.append(part.format(**kwargs))
            except KeyError as e:
                raise KeyError(f"Missing template parameter: {str(e)}")

        return " ".join(formatted_parts)

    def run(
        self, args: str = "", json_output: bool = False, **kwargs: str
    ) -> Optional[Union[str, Dict[str, Any]]]:
        if self._current_template:
            command = f"{self.base_command} {self.format_command(**kwargs)}"
            if args:
                command = f"{command} {args}"
        else:
            command = f"{self.base_command} {args}"

        if self.trailer:
            command = f"{command} {self.trailer}"

        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            self._last_result = result

            if result.returncode != 0:
                self._last_error = result.stderr
                return None

            output = result.stdout.strip()

            if json_output:
                try:
                    return json.loads(output)
                except json.JSONDecodeError as e:
                    self._last_error = f"JSON parsing error: {str(e)}"
                    return None

            return output

        except Exception as e:
            self._last_error = str(e)
            return None

    def set_trailer(self, trailer: str) -> None:
        """Set trailer string to be appended to all commands"""
        self.trailer = trailer

    def error(self) -> Optional[str]:
        """Return last error message"""
        return self._last_error

    def ok(self) -> bool:
        """Check if last command succeeded"""
        return bool(self._last_result and self._last_result.returncode == 0)

    def fail(self) -> bool:
        """Check if last command failed"""
        return not self.ok()
