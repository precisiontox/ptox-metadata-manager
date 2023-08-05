""" Small module to make the logger easy to import
"""

from logging import getLogger, basicConfig, DEBUG

LOGGER = getLogger('ptmd')
basicConfig(format="%(asctime)s [%(levelname)s]: %(filename)s(%(funcName)s:%(lineno)s) >> %(message)s")
LOGGER.setLevel(DEBUG)
