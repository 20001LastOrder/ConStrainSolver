import sys

from loguru import logger

logger.add("../../llm.log", level="DEBUG")

def getLogger():
    return logger

def addConsoleToLogger():
    return logger.add(sys.stderr, level="INFO")

def removeConsoleFromLogger(logger_id: int):
    logger.remove(logger_id)