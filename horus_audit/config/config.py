import logging
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


LOG_FILE = Path.home() / ".horus" / "horus.log"


def setup_logging() -> None:
    """
    Setup root logging.
    """

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()

    if logger.handlers:
        return

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = TimedRotatingFileHandler(
        filename=LOG_FILE,
        when="midnight",
        backupCount=14,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.propagate = False


def get_logger(module_name: str) -> Logger:
    """
    Return a configured logger for a specific module.

    Args:
        module_name (str): The module name.

    Returns:
        Logger: Configured logger instance.
    """

    return logging.getLogger(module_name)
