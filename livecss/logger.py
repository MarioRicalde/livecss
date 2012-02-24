import logging
import os
from .menu import PLUGIN_DIRECTORY

__all__ = ['debug', 'info']

level = logging.DEBUG

logger = logging.getLogger('livecss')
logger.setLevel(level)

logfile = os.path.join(PLUGIN_DIRECTORY, 'livecss.log')

fh = logging.FileHandler(logfile)
fh.setLevel(level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

info = logger.info
debug = logger.debug
