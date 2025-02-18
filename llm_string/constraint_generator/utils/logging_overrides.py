import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='../core/constraint_generator.log',
                    filemode='a')

console = logging.StreamHandler()

console.setLevel(logging.INFO)

console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))

def getLogger(name):
    return logging.getLogger(name)

def addConsoleToLogger():
    logging.getLogger().addHandler(console)

def removeConsoleFromLogger():
    logging.getLogger().removeHandler(console)