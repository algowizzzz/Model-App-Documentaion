"""
Debugging and logging utilities for the Model Documentation Agent.
"""

import logging
import time
import traceback
import functools
from typing import Dict, Any, Callable, Optional, List, TypeVar, cast

# Type variable for generic function decorator
F = TypeVar('F', bound=Callable[..., Any])

class ModelDocDebugger:
    """
    Debugger for the Model Documentation Agent that handles logging,
    performance tracking, and exception handling.
    """
    
    def __init__(
        self, 
        logger_name: str = "ModelDocAgent", 
        debug_level: str = "INFO",
        log_to_console: bool = True,
        log_file: Optional[str] = None
    ):
        """
        Initialize the debugger.
        
        Args:
            logger_name: Name for the logger
            debug_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_console: Whether to log to console
            log_file: Optional file path to log to
        """
        # Convert string level to logging level
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        level = level_map.get(debug_level.upper(), logging.INFO)
        
        # Configure logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Clear existing handlers
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        # Performance tracking
        self.timers: Dict[str, float] = {}
    
    def time_function(self, func: F) -> F:
        """
        Decorator to time function execution.
        
        Args:
            func: The function to time
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            self.logger.debug(f"Starting {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                self.logger.debug(f"Completed {func.__name__} in {elapsed:.2f} seconds")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                self.logger.error(f"Error in {func.__name__} after {elapsed:.2f} seconds: {str(e)}")
                raise
                
        return cast(F, wrapper)
    
    def log_exception(self, context: str, exception: Exception, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an exception with context and metadata.
        
        Args:
            context: Context where the exception occurred
            exception: The exception object
            metadata: Optional metadata to include in the log
        """
        self.logger.error(f"Exception in {context}: {str(exception)}")
        
        if metadata:
            self.logger.error(f"Metadata: {metadata}")
            
        self.logger.debug(f"Traceback: {traceback.format_exc()}")
    
    def start_timer(self, timer_name: str) -> None:
        """
        Start a named timer.
        
        Args:
            timer_name: Name of the timer
        """
        self.timers[timer_name] = time.time()
        self.logger.debug(f"Timer '{timer_name}' started")
    
    def end_timer(self, timer_name: str) -> float:
        """
        End a named timer and return elapsed time.
        
        Args:
            timer_name: Name of the timer
            
        Returns:
            Elapsed time in seconds
        """
        if timer_name not in self.timers:
            self.logger.warning(f"Timer '{timer_name}' was not started")
            return 0.0
            
        elapsed = time.time() - self.timers.pop(timer_name)
        self.logger.debug(f"Timer '{timer_name}' ended: {elapsed:.2f} seconds")
        return elapsed 