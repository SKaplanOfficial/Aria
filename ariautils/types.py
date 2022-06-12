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

#### Enums
class AriaPhase(Enum):
    """Phases in Aria's command execution cycle.
    """
    INPUT_PHASE = 0         # Aria is awaiting input.
    INVOCATION_PHASE = 1    # Aria is checking plugins for an invocation match to the inputted query
    HANDLER_CHECK_PHASE = 2 # Aria is checking plugins for a handler match to the inputted query
    HANDLER_PHASE = 3       # Aria found a handler for the query and is now running it
    EXECUTION_PHASE = 4     # Aria is running the main execution method of a plugin
    END_PHASE = 5           # Aria is cleaning up and preparing for the input phase

class RunningState(Enum):
    """Levels of running states for processes.
    """
    WAITING = 0     # Process is awaiting start.
    RUNNING = 1     # Process is in progress.
    PAUSED = 2      # Process is paused, but can be continued.
    BLOCKED = 3     # Process is paused and cannot continue until conditions are met.
    STOPPED = 4     # Process was terminated before it could complete.
    FINISHED = 5    # Process has reached completion.

#### Errors
class AriaError(Exception):
    """A general error class for Aria-specific errors.
    """
    def __init__(self, message):
        super().__init__(message)

### Internal Aria Errors
# class ContextError(AriaError):
#     """A class for errors that occur during the handler checking phase."""
#     def __init__(self, query: str, plugin: str, message: str = ""):
#         message = f"Failed while checking handler for query '{query}' by plugin '{plugin}'. {message}"
#         super().__init__(message)

### Phase-Specific Errors
## Invocation
class InvocationError(AriaError):
    """A class for errors that occur during the command invocation phase.
    """
    def __init__(self, query: str, plugin: str, message: str = ""):
        message = f"Failed while checking for invocation match for query '{query}' against plugin '{plugin}'. {message}"
        super().__init__(message)

class AssumedQueryLengthError(InvocationError, IndexError):
    """A class for errors that occur due to a plugin trying to access term indices beyond the indices present in a query.
    """
    def __init__(self, query: str, plugin: str):
        message = f"The plugin assumed the query had more terms than it did."
        super().__init__(query, plugin, message)

## Handler Checking
class CommandHandlerCheckError(AriaError):
    """A class for errors that occur during the handler checking phase."""
    def __init__(self, query: str, plugin: str, message: str = ""):
        message = f"Failed while checking handler for query '{query}' in plugin '{plugin}'. {message}"
        super().__init__(message)

## Handling
class CommandHandlerError(AriaError):
    """A class for errors that occur during the handling phase.
    """
    def __init__(self, query: str, plugin: str, message: str = ""):
        message = f"Failed while handling query '{query}' by plugin '{plugin}'. {message}"
        super().__init__(message)

## Execution
class CommandExecutionError(AriaError):
    """A class for errors that occur during the execution phase."""
    def __init__(self, query: str, plugin: str, message: str = ""):
        message = f"Failed while executing plugin '{plugin}' with query '{query}'. {message}"
        super().__init__(message)

class InsufficientInfoForQueryError(CommandExecutionError):
    """A class for errors that occur due to missing, inaccessible, or otherwise unavailable information necessary to run a command.
    
    When this error is raised, it indicates that the user supplied a correct query, that the plugin can handle the query in general, and that there is some course of action the user can take to supply the necessary information.
    """
    def __init__(self, query: str, plugin: str, message: str = ""):
        message = f"The plugin '{plugin}' could not complete query '{query}' because it could not access necessary information. {message}"
        super().__init__(message)

class MalformedQueryError(CommandExecutionError):
    """A class for errors caused by invalid queries.
    
    When this error is raised, it indicates that the user supplied a nearly correct query that the plugin would be able to handle if one or two small changers were made. Plugin creators should predict the different ways users will try to invoke their commands and code their plugin to match  only with the queries that the plugin can truthfully handle.
    
    For example, plugins must not match with all queries. Raising a MalformedQueryError in such a case does not provide adequate feedback as to what the user did wrong.
    """
    def __init__(self, query: str, plugin: str, message: str = ""):
        message = f"The plugin '{plugin}' failed could not parse query '{query}' because the query was malformed. {message}"
        super().__init__(message)