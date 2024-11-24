import logging
import inspect
import os
from datetime import datetime

class LoggerSingleton:
    _instance = None

    @staticmethod
    def get_instance(master_level=45, log_to_file=True, file_path="application.log"):
        if LoggerSingleton._instance is None:
            LoggerSingleton._instance = DynamicLogger(
                master_level=master_level,
                log_to_file=log_to_file,
                file_path=file_path,
            )
        else:
            # If instance exists, update the master level dynamically
            LoggerSingleton._instance.master_level = master_level
        return LoggerSingleton._instance

class DynamicLogger:
    LEVELS = {
        (0, 9): "CRITICAL",  # CRITICAL range 0-9
        (10, 19): "ERROR",   # ERROR range 10-19
        (20, 29): "WARNING", # WARNING range 20-29
        (30, 39): "INFO",    # INFO range 30-39
        (40, 49): "DEBUG",   # DEBUG range 40-49
        (50, 59): "NOTSET",  # NOTSET range 50-59
    }

    def __init__(self, master_level=45, log_to_file=False, file_path="application.log"):
        """
        Initialize the logger.

        Args:
            master_level (int): The master logging level (e.g., 10 for DEBUG, 20 for INFO).
            log_to_file (bool): Whether to log messages to a file.
            file_path (str): The path to the log file (if log_to_file is True).
        """
        self.master_level = master_level
        self.log_to_file = log_to_file
        self.file_path = file_path

        # Setup file logging if enabled
        if self.log_to_file:
            self.file_handler = open(self.file_path, "a")

    def _get_caller_info(self):
        """
        Retrieve caller information such as file name, line number, and function name.

        Returns:
            str: A string containing the caller's file name, line number, and function name.
        """
        # Get the stack trace and skip the first three frames (current method, log method, and logger)
        stack = inspect.stack()
        
        # Check if there are enough frames in the stack to access the caller
        if len(stack) > 3:
            # Access the frame that called the log method
            frame = stack[3]  # Skip 3 frames to get the actual caller's frame
            filename = os.path.basename(frame.filename)  # Extract just the filename
            line_number = frame.lineno  # Extract the line number
            function_name = frame.function  # Extract the function name

            # Return the caller info in a readable format
            return f"{filename}:{line_number} in {function_name}()"
        
        return "Unknown Caller"

    def _format_log_message(self, level, message):
        """
        Format the log message with timestamp, level, and caller info.

        Args:
            level (int): Logging level.
            message (str): The log message.

        Returns:
            str: The formatted log message.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_name = self._get_level_name(level)
        caller_info = self._get_caller_info()
        return f"{timestamp} - {level_name} - {caller_info} - {message}"

    def _get_level_name(self, level):
        """
        Get the name of the log level based on the level's range.

        Args:
            level (int): The log level.
        
        Returns:
            str: The name of the log level.
        """
        for level_range, name in self.LEVELS.items():
            if level_range[0] <= level <= level_range[1]:
                return name
        return "UNKNOWN"  # If no range matches, return "UNKNOWN"

    def log(self, level, message):
        """
        Log a message if its level meets or under the master logging level.

        Args:
            level (int): Logging level (e.g., 10 for DEBUG, 20 for INFO).
            message (str): The log message.
        """
        if level <= self.master_level:
            log_message = self._format_log_message(level, message)
            print(log_message)  # Print to console
            if self.log_to_file:
                self.file_handler.write(log_message + "\n")
                self.file_handler.flush()

    def __del__(self):
        """Close the file handler when the logger is destroyed."""
        if self.log_to_file and hasattr(self, "file_handler"):
            self.file_handler.close()
