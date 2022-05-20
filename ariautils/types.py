"""This module defines types, enums, etc. for global use in Aria.
"""

from enum import Enum
from typing import (
    Any,
    Dict,
    Tuple,
    Union,
    NewType
)

class RunningState(Enum):
    """Levels of running states for processes.
    """
    WAITING = 0     # Process is awaiting start.
    RUNNING = 1     # Process is in progress.
    PAUSED = 2      # Process is paused, but can be continued.
    BLOCKED = 3     # Process is paused and cannot continue until conditions are met.
    STOPPED = 4     # Process was terminated before it could complete.
    FINISHED = 5    # Process has reached completion.