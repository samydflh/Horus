import logging
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class Config:
    """
    Configuration manager.
    """

    def __init__(self) -> None:
        # Default log file: ~/.horus/horus.log
        self._default_log_file = Path.home() / ".horus" / "horus.log"
        # Setup logging
        self._setup_logging()

    def get_logger(self, module_name: str) -> Logger:
        """
        Return a configured logger for a specific module.

        Args:
            module_name (str): The module name.

        Returns:
            Logger: Configured logger instance.
        """

        return logging.getLogger(module_name)

    def _setup_logging(self) -> None:
        """
        Setup root logging.
        """

        # Log directory
        self._default_log_file.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger()

        if logger.hasHandlers():
            logger.handlers.clear()

        # Root logger
        logger.setLevel(logging.INFO)

        # Setup a formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Setup a rotating file handler
        file_handler = TimedRotatingFileHandler(
            filename=self._default_log_file,
            when="midnight",
            backupCount=14,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)

        # Avoid message duplication in the root logger
        logger.propagate = False


config = Config()
