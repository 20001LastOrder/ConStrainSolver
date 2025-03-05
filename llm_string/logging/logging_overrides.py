import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("llm.log", level="DEBUG")

def getLogger():
    return logger

def addConsoleToLogger():
    return logger.add(sys.stderr, level="INFO")

def removeConsoleFromLogger(logger_id: int):
    logger.remove(logger_id)