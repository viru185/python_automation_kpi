import os
import sys

from loguru import logger

from config import LOG_LEVEL, LOG_TO_CONSOLE, LOG_TO_FILE, LOGS_DIR, LOGS_FILE

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)


def init_loguru():

    # Remove the default logger
    logger.remove()

    # Add file logger if LOG_TO_FILE is True
    if LOG_TO_FILE:
        logger.add(
            LOGS_FILE,
            level=LOG_LEVEL,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
        )

    # Add console logger if LOG_TO_CONSOLE is True
    if LOG_TO_CONSOLE:
        logger.add(
            sys.stdout,
            level=LOG_LEVEL,
            colorize=True,
        )


init_loguru()
