from typing import Any, Optional
import os
from enum import IntEnum

class DebugLevel(IntEnum):
    NONE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4
    VERBOSE = 5

class DebugPrint:
    def __init__(self):
        # Initialize with environment variable or default to INFO
        self.level = DebugLevel[os.getenv('DEBUG_LEVEL', 'INFO')]
        self._enabled = True

    def set_level(self, level: DebugLevel | str) -> None:
        """Set the debug level"""
        if isinstance(level, str):
            self.level = DebugLevel[level.upper()]
        else:
            self.level = level

    def enable(self) -> None:
        """Enable debug printing"""
        self._enabled = True

    def disable(self) -> None:
        """Disable debug printing"""
        self._enabled = False

    def print(self, *args: Any, level: DebugLevel = DebugLevel.INFO, **kwargs) -> None:
        """Print debug message if level is sufficient"""
        if self._enabled and level <= self.level:
            print(*args, **kwargs)

    def error(self, *args: Any, **kwargs) -> None:
        """Print error message"""
        self.print(*args, level=DebugLevel.ERROR, **kwargs)

    def warning(self, *args: Any, **kwargs) -> None:
        """Print warning message"""
        self.print(*args, level=DebugLevel.WARNING, **kwargs)

    def info(self, *args: Any, **kwargs) -> None:
        """Print info message"""
        self.print(*args, level=DebugLevel.INFO, **kwargs)

    def debug(self, *args: Any, **kwargs) -> None:
        """Print debug message"""
        self.print(*args, level=DebugLevel.DEBUG, **kwargs)

    def verbose(self, *args: Any, **kwargs) -> None:
        """Print verbose message"""
        self.print(*args, level=DebugLevel.VERBOSE, **kwargs)

# Create a singleton instance
dprint = DebugPrint()

# Export the DebugLevel enum and singleton instance
__all__ = ['dprint', 'DebugLevel']
