import logging
import sys
import os

def get_logger():
    logger = logging.getLogger("clamav-fastapi")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger
